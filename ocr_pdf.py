"""
MTC Validator — ocr_pdf.py
PDF extraction: pdfplumber (digital) + Mistral API (scanned/OCR)
"""

import pandas as pd
import pdfplumber
import io
import re
import requests
import json
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image


def pdf_to_images(pdf_bytes: bytes) -> list:
    """
    Convert PDF pages to PIL Images for OCR.
    Uses pdf2image library (requires poppler-utils on system).
    
    Returns:
        list of PIL Image objects, or empty list on failure
    """
    try:
        images = convert_from_bytes(pdf_bytes, dpi=150)
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []


def extract_with_pdfplumber(pdf_bytes: bytes) -> pd.DataFrame:
    """
    Extract MTC data using pdfplumber (for digital PDFs).
    
    Returns:
        DataFrame with 'elemento' and 'valor' columns, or empty DataFrame
    """
    data = []
    element_patterns = {
        "C_%": r"(?:Carbon|C|C\s*(?:%|pct))\s*[:=]?\s*([\d.]+)",
        "Mn_%": r"(?:Manganese|Mn|Mangan)\s*[:=]?\s*([\d.]+)",
        "P_%": r"(?:Phosphorus|P|Phos)\s*[:=]?\s*([\d.]+)",
        "S_%": r"(?:Sulfur|S)\s*[:=]?\s*([\d.]+)",
        "Si_%": r"(?:Silicon|Si)\s*[:=]?\s*([\d.]+)",
        "Cr_%": r"(?:Chromium|Chrome|Cr)\s*[:=]?\s*([\d.]+)",
        "Mo_%": r"(?:Molybdenum|Mo)\s*[:=]?\s*([\d.]+)",
        "YS_MPa": r"(?:Yield|YS|Re|Rp0\.2)\s*[:=]?\s*([\d.]+)",
        "UTS_MPa": r"(?:Tensile|UTS|Rm|Fu)\s*[:=]?\s*([\d.]+)",
        "Elong_%": r"(?:Elongation|Elong|A%)\s*[:=]?\s*([\d.]+)",
    }
    
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Try table extraction first
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row and len(row) >= 2:
                                elem_cell = str(row[0]).lower() if row[0] else ""
                                val_cell = str(row[1]).lower() if row[1] else ""
                                
                                # Check if row contains element name and numeric value
                                for elem_name, pattern in element_patterns.items():
                                    # Filter out None values and convert to strings
                                    row_str = " ".join(str(c).strip() for c in row if c is not None)
                                    if re.search(elem_name.lower(), elem_cell) or re.search(pattern, row_str):
                                        try:
                                            # Try to extract value
                                            match = re.search(r"([\d.]+)", val_cell)
                                            if match:
                                                valor = float(match.group(1))
                                                data.append({"elemento": elem_name, "valor": valor})
                                        except:
                                            pass
            
            # If no tables found, try text extraction with regex
            if not data:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    for elem_name, pattern in element_patterns.items():
                        matches = re.finditer(pattern, text, re.IGNORECASE)
                        for match in matches:
                            try:
                                valor = float(match.group(1))
                                data.append({"elemento": elem_name, "valor": valor})
                            except:
                                pass
        
        if data:
            df = pd.DataFrame(data).drop_duplicates(subset=["elemento"])
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error with pdfplumber: {e}")
        return pd.DataFrame()


def extract_with_mistral_ocr(pdf_bytes: bytes) -> pd.DataFrame:
    """
    Extract MTC data using Mistral API (for scanned PDFs).
    Requires MISTRAL_API_KEY in st.secrets.
    
    Returns:
        DataFrame with 'elemento' and 'valor' columns, or empty DataFrame
    """
    try:
        api_key = st.secrets.get("MISTRAL_API_KEY", "")
        if not api_key:
            print("MISTRAL_API_KEY not found in secrets")
            return pd.DataFrame()
        
        images = pdf_to_images(pdf_bytes)
        if not images:
            return pd.DataFrame()
        
        # Convert first page to base64
        first_image = images[0]
        img_byte_arr = io.BytesIO()
        first_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        import base64
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        # Call Mistral API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "pixtral-12b-2409",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "url": f"data:image/jpeg;base64,{img_base64}",
                        },
                        {
                            "type": "text",
                            "text": (
                                "Extract all chemical composition values and mechanical properties "
                                "from this Mill Test Certificate. Return ONLY a JSON array like: "
                                "[{'elemento': 'C_%', 'valor': 0.22}, {'elemento': 'Mn_%', 'valor': 0.85}]. "
                                "Use these exact element names: C_%, Mn_%, P_%, S_%, Si_%, Cr_%, Mo_%, "
                                "YS_MPa, UTS_MPa, Elong_%"
                            )
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                df = pd.DataFrame(data)
                # Ensure columns exist
                if "elemento" in df.columns and "valor" in df.columns:
                    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
                    return df
        
        return pd.DataFrame()
    except Exception as e:
        print(f"Error with Mistral OCR: {e}")
        return pd.DataFrame()


def extract_from_pdf(pdf_bytes: bytes) -> tuple[pd.DataFrame, str]:
    """
    Extract MTC data from PDF using two methods:
    1. pdfplumber (for digital PDFs with searchable text/tables)
    2. Mistral API (fallback for scanned PDFs)
    
    Args:
        pdf_bytes: bytes — PDF file content
    
    Returns:
        (DataFrame with 'elemento' and 'valor' columns, method_used string)
        method_used is: 'pdfplumber', 'mistral_ocr', or 'not_found'
        Never raises exceptions — returns empty DataFrame with 'not_found' on failure
    """
    # Try pdfplumber first (faster, no API call)
    df_pdfplumber = extract_with_pdfplumber(pdf_bytes)
    if not df_pdfplumber.empty:
        return df_pdfplumber, "pdfplumber"
    
    # Fallback to Mistral OCR for scanned PDFs
    df_mistral = extract_with_mistral_ocr(pdf_bytes)
    if not df_mistral.empty:
        return df_mistral, "mistral_ocr"
    
    # No data found
    return pd.DataFrame(columns=["elemento", "valor"]), "not_found"
