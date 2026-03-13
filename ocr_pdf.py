"""
MTC Validator — ocr_pdf.py v2 (Dual Format)
PDF extraction: pdfplumber (digital) + Mistral API (scanned/OCR)
Tested on 2 formats: Ternium/AHMSA (Actual rows) and Yieh Corporation (Product ID rows)
"""

import pandas as pd
import pdfplumber
import io
import re
import requests
import json
import base64
import streamlit as st
from PIL import Image
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


# ===== ALIASES DICT (tested and working) =====
ALIASES = {
    # Chemical elements
    "si": "Si_%", "fe": "Fe_%", "cu": "Cu_%", "mn": "Mn_%",
    "mg": "Mg_%", "cr": "Cr_%", "zn": "Zn_%", "ti": "Ti_%",
    "al": "Al_%", "c": "C_%", "p": "P_%", "s": "S_%",
    "ni": "Ni_%", "mo": "Mo_%", "v": "V_%", "nb": "Nb_%",
    # Yield Strength variants
    "y.s.(mpa)": "YS_MPa", "y.s. (mpa)": "YS_MPa", "ys": "YS_MPa",
    "yield strength": "YS_MPa", "yield strength (mpa)": "YS_MPa",
    "re": "YS_MPa", "rp0.2": "YS_MPa", "limite elastico": "YS_MPa",
    # Tensile Strength variants
    "t.s.(mpa)": "UTS_MPa", "t.s. (mpa)": "UTS_MPa",
    "tensile strength": "UTS_MPa", "tensile strength (mpa)": "UTS_MPa",
    "uts": "UTS_MPa", "rm": "UTS_MPa", "resistencia tensil": "UTS_MPa",
    # Elongation variants
    "el(%)": "Elong_%", "el( %)": "Elong_%", "elongation": "Elong_%",
    "elongation (%)": "Elong_%", "elong": "Elong_%", "a%": "Elong_%",
    # Spanish
    "carbono": "C_%", "carbon": "C_%", "manganeso": "Mn_%",
    "fosforo": "P_%", "fósforo": "P_%", "azufre": "S_%",
    "silicio": "Si_%", "cromo": "Cr_%", "molibdeno": "Mo_%",
}

# Cells to skip — watermarks, keywords, non-data
SKIP_VALUES = {'-', '', 'none', 'null', 's', 'a', 'm', 'p', 'l', 'e',
               'sample', 'n/a', 'n.a.', '-', '–'}
SKIP_FIRST_CELL = {'product', 'chemical', 'mechanical', 'subtotal',
                   'heat', 'size', 'remarks', 'sample', 'manager',
                   'element', 'property', 'properties', 'others',
                   'min', 'max', 'typical', 'specification'}


# ===== HELPER FUNCTIONS =====

def _clean_header(cell: str) -> str:
    """
    Extract element name from a header cell that may contain limits.
    'Si\n< 0.25%' → 'Si'
    'Y.S.(Mpa)\n17 – 110' → 'Y.S.(Mpa)'
    """
    if not cell:
        return ""
    # Take first line only
    name = str(cell).split('\n')[0].strip()
    # Remove limit patterns like "< 0.25%" or "17 – 110"
    name = re.sub(r'[<>≤≥]\s*[\d.]+\s*%?', '', name).strip()
    name = re.sub(r'[\d.]+\s*[-–]\s*[\d.]+', '', name).strip()
    return name.strip()


def _normalize(name: str) -> str | None:
    """Map raw header name to canonical element name using ALIASES."""
    if not name:
        return None
    return ALIASES.get(name.strip().lower(), None)


def _is_data_row(row: list) -> bool:
    """
    Detect if a table row contains actual measurement data.
    Returns True for Product ID rows and Actual rows.
    Returns False for headers, min/max specs, watermarks, subtotals.
    """
    if not row or not row[0]:
        return False
    first = str(row[0]).strip().lower()
    # Skip known non-data first cells
    if any(kw in first for kw in SKIP_FIRST_CELL):
        return False
    # Skip rows that are entirely '-' or letters (watermark)
    numeric_count = 0
    for v in row[1:]:
        if v and str(v).strip() not in SKIP_VALUES:
            try:
                float(str(v).strip())
                numeric_count += 1
            except:
                pass
    return numeric_count >= 3


def _extract_headers(table: list) -> list:
    """
    Find the row with element symbol headers.
    Handles multi-level headers by finding the row with 4+ short element names.
    """
    for row in table[:4]:
        if not row:
            continue
        cleaned = [_clean_header(str(c)) if c else "" for c in row]
        # This is a header row if it has 4+ known element aliases
        known = sum(1 for h in cleaned if h.lower() in ALIASES)
        if known >= 3:
            return cleaned
    return []


# ===== MAIN EXTRACTION FUNCTIONS =====

def _extract_pdfplumber(pdf_bytes: bytes) -> pd.DataFrame:
    """
    Extract MTC data from digital PDF using pdfplumber.
    Handles both Format A (Actual row) and Format B (Product ID rows).
    """
    results = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue

                for table in tables:
                    if not table or len(table) < 3:
                        continue

                    headers = _extract_headers(table)
                    if not headers or len(headers) < 4:
                        continue

                    # Try FORMAT A first: look for "Actual" row
                    actual_row = None
                    for row in table:
                        if row and row[0] and str(row[0]).strip().lower() == "actual":
                            actual_row = row
                            break

                    # FORMAT B fallback: use first valid data row
                    if actual_row is None:
                        for row in table:
                            if _is_data_row(row):
                                actual_row = row
                                break

                    if actual_row is None:
                        continue

                    # Map values to canonical element names
                    for j, val in enumerate(actual_row):
                        if j == 0 or j >= len(headers):
                            continue
                        header = headers[j]
                        norm = _normalize(header)
                        if not norm:
                            continue
                        val_str = str(val).strip() if val else ""
                        if val_str.lower() in SKIP_VALUES:
                            continue
                        try:
                            num = float(val_str)
                            # No duplicates — first occurrence wins
                            if not any(r['elemento'] == norm for r in results):
                                results.append({'elemento': norm, 'valor': num})
                        except:
                            pass
    except Exception as e:
        print(f"Error in _extract_pdfplumber: {e}")

    return pd.DataFrame(results) if results else pd.DataFrame(columns=['elemento', 'valor'])


def _extract_mistral(pdf_bytes: bytes) -> pd.DataFrame:
    """
    Fallback OCR using Mistral Pixtral API for scanned PDFs.
    Only called if pdfplumber returns fewer than 3 elements.
    Requires MISTRAL_API_KEY in st.secrets.
    Converts PDF to image (PNG) before sending to Mistral using PyMuPDF + PIL.
    """
    api_key = st.secrets.get("MISTRAL_API_KEY", None)
    if not api_key:
        return pd.DataFrame(columns=['elemento', 'valor'])

    if not HAS_PYMUPDF:
        print("Warning: PyMuPDF not installed, Mistral OCR unavailable")
        return pd.DataFrame(columns=['elemento', 'valor'])

    try:
        # Convert PDF to image using PyMuPDF + PIL for robust JPEG encoding
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) < 1:
            return pd.DataFrame(columns=['elemento', 'valor'])
        
        # Render first page to image
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))  # 1x zoom (original size)
        
        # Convert PyMuPDF pixmap to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        # Resize to max 800x800
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Convert to JPEG with low quality for smallest size
        img_byte_arr = io.BytesIO()
        img = img.convert('RGB')  # Ensure RGB for JPEG
        img.save(img_byte_arr, format='JPEG', quality=60, optimize=True)
        img_byte_arr.seek(0)
        img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        payload = {
            "model": "pixtral-12b",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all chemical composition values and mechanical properties "
                            "from this Mill Test Certificate image. "
                            "Return ONLY a valid JSON array, no markdown, no explanation. "
                            "Format: [{\"elemento\": \"C_%\", \"valor\": 0.22}] "
                            "Use ONLY these element names: "
                            "Si_%, Fe_%, Cu_%, Mn_%, Mg_%, Cr_%, Zn_%, Ti_%, Al_%, "
                            "C_%, P_%, S_%, Ni_%, Mo_%, V_%, "
                            "YS_MPa, UTS_MPa, Elong_% "
                            "Skip elements with value '-' or missing."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    }
                ]
            }]
        }
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
        # Clean markdown fences if present
        content = content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error in _extract_mistral: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(columns=['elemento', 'valor'])


# ===== PUBLIC API =====

METHOD_MESSAGES = {
    "pdfplumber":         ("✅ Extraído con pdfplumber (PDF digital)", "success"),
    "mistral_ocr":        ("🤖 Extraído con Mistral OCR (PDF escaneado)", "info"),
    "mistral_unavailable":("⚠️ Mistral API no configurada — solo PDFs digitales soportados.", "warning"),
    "not_found":          ("❌ No se detectaron datos. Verifica que sea un MTC válido o usa la plantilla Excel.", "error"),
}


def extract_from_pdf(pdf_bytes: bytes) -> tuple[pd.DataFrame, str]:
    """
    Public function. Try pdfplumber first, then Mistral OCR fallback.
    Never raises exceptions.

    Returns:
        (DataFrame with columns 'elemento' and 'valor', method_used)
    """
    # Method 1: pdfplumber
    try:
        df = _extract_pdfplumber(pdf_bytes)
        if len(df) >= 3:
            return df, "pdfplumber"
    except Exception as e:
        print(f"pdfplumber error: {e}")

    # Method 2: Mistral OCR
    try:
        if st.secrets.get("MISTRAL_API_KEY", None):
            df = _extract_mistral(pdf_bytes)
            if len(df) >= 1:
                return df, "mistral_ocr"
            return pd.DataFrame(columns=['elemento', 'valor']), "mistral_unavailable"
    except Exception as e:
        print(f"Mistral error: {e}")

    return pd.DataFrame(columns=['elemento', 'valor']), "not_found"
