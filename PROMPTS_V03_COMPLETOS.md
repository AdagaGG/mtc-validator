# PROMPTS COMPLETOS — MTC Validator v0.3
# Implementa en orden: A → B → C → D → E → F
# Cada prompt va en Copilot Chat (Ctrl+I en VS Code)

---

## PROMPT A — Crear `ocr_pdf.py` (pdfplumber + Mistral fallback)

```
Create a new file called ocr_pdf.py for a Streamlit MTC Validator app.

This module extracts chemical composition data from PDF Mill Test Certificates.

Implement TWO extraction methods:

METHOD 1 — pdfplumber (for digital PDFs):
- Use pdfplumber to open the PDF
- Search all pages for tables
- Look for rows containing element names like C, Mn, P, S, Si, Cr, Mo, or their variations
- Also try text extraction: search for patterns like "C: 0.22" or "Carbon 0.22%" using regex
- Return a pandas DataFrame with columns 'elemento' and 'valor'

METHOD 2 — Mistral OCR API (fallback for scanned PDFs):
- Only used if pdfplumber finds no data
- Convert PDF pages to images using pdf2image
- Send each image to Mistral API: https://api.mistral.ai/v1/chat/completions
- Use model "pixtral-12b-2409"
- Prompt: "Extract all chemical composition values and mechanical properties from this Mill Test Certificate. Return ONLY a JSON array like: [{'elemento': 'C_%', 'valor': 0.22}, {'elemento': 'Mn_%', 'valor': 0.85}]. Use these exact element names: C_%, Mn_%, P_%, S_%, Si_%, Cr_%, Mo_%, YS_MPa, UTS_MPa, Elong_%"
- Get API key from st.secrets['MISTRAL_API_KEY'] — if not available, skip this method
- Parse JSON response and return DataFrame

MAIN FUNCTION:
def extract_from_pdf(pdf_bytes: bytes) -> tuple[pd.DataFrame, str]:
    """
    Extract MTC data from PDF.
    Returns: (DataFrame with 'elemento' and 'valor' columns, method_used string)
    method_used is either 'pdfplumber' or 'mistral_ocr' or 'not_found'
    Never raises exceptions — return empty DataFrame with method='not_found' on failure.
    """

Also add:
def pdf_to_images(pdf_bytes: bytes) -> list:
    """Convert PDF pages to PIL Images for OCR. Uses pdf2image."""

Add to requirements.txt: pdfplumber, pdf2image, requests
Note: pdf2image requires poppler. Add a comment that on Streamlit Cloud,
poppler must be installed via packages.txt file with content: poppler-utils
```

---

## PROMPT B — Expandir `normas.py` con 8 normas nuevas

```
Expand the existing normas.py file for a steel MTC validator.

Keep all existing normas (SAE1020, SAE1045, ASTM_A36, AISI4140).

Add these 8 new normas with accurate ASTM/DIN/API min/max tolerances:

1. ASTM_A572_Gr50 — High-strength low-alloy structural steel Grade 50
   Elements: C_%, Mn_%, P_%, S_%, Si_%, YS_MPa (min 345), UTS_MPa (min 450), Elong_%

2. ASTM_A992 — Structural steel for W-shapes (beams)
   Elements: C_%, Mn_%, P_%, S_%, Si_%, YS_MPa (290-450), UTS_MPa (min 400), Elong_%

3. ASTM_A516_Gr70 — Pressure vessel steel Grade 70
   Elements: C_%, Mn_%, P_%, S_%, Si_%, YS_MPa (min 260), UTS_MPa (485-620), Elong_%

4. API_5L_X42 — Pipeline steel Grade X42
   Elements: C_%, Mn_%, P_%, S_%, Si_%, YS_MPa (290-495), UTS_MPa (min 415), Elong_%

5. DIN_17200_Ck45 — German medium carbon steel (equivalent to SAE1045)
   Elements: C_%, Mn_%, P_%, S_%, Si_%, Cr_%, YS_MPa, UTS_MPa, Elong_%

6. EN_10083_42CrMo4 — European alloy steel (equivalent to AISI4140)
   Elements: C_%, Mn_%, P_%, S_%, Si_%, Cr_%, Mo_%, YS_MPa, UTS_MPa, Elong_%

7. NMX_B_172 — Mexican standard for carbon steel bars
   Elements: C_%, Mn_%, P_%, S_%, YS_MPa, UTS_MPa, Elong_%
   Use SAE 1020 chemical composition ranges as reference since NMX-B-172 adopts SAE grades

8. ASTM_A193_B7 — Alloy steel bolting (chromium-molybdenum)
   Elements: C_%, Mn_%, P_%, S_%, Si_%, Cr_%, Mo_%, YS_MPa (min 725), UTS_MPa (min 860), Elong_%

For each norma, add a 'label' key with full name and a 'descripcion' key with one-line use case.
Example structure:
"ASTM_A572_Gr50": {
    "label": "ASTM A572 Grado 50 — Acero Estructural Alta Resistencia",
    "descripcion": "Vigas, columnas, placas estructurales en construcción y puentes",
    "C_%": {"min": 0.0, "max": 0.23},
    ...
}
```

---

## PROMPT C — Crear `database.py` con SQLite

```
Create a new file called database.py for a Streamlit MTC Validator app.

Implement a SQLite database to store validation history.

Use Python's built-in sqlite3 module. Database file: 'mtc_history.db'

SCHEMA — table 'validaciones':
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- fecha: TEXT (ISO format datetime)
- usuario: TEXT (username from auth)
- empresa: TEXT (company name, same as username for now)
- norma: TEXT (e.g. 'SAE1045')
- archivo: TEXT (original filename)
- n_total: INTEGER (total elements evaluated)
- n_aprobado: INTEGER
- n_rechazado: INTEGER
- veredicto: TEXT ('LOTE APROBADO' or 'LOTE RECHAZADO')
- elementos_fallidos: TEXT (comma-separated list of failed elements)
- metodo_ingreso: TEXT ('excel', 'pdf_pdfplumber', 'pdf_mistral', 'manual')

FUNCTIONS to implement:

def init_db():
    """Create table if not exists. Call on app startup."""

def save_validacion(usuario, norma, archivo, df_resultado, veredicto, metodo):
    """Save a completed validation to history. Returns the new row id."""

def get_historial(usuario=None, limit=50):
    """Get validation history. If usuario is None, return all. Returns list of dicts."""

def get_stats(usuario=None):
    """Return dict with: total_validaciones, total_aprobados, total_rechazados,
    norma_mas_usada, tasa_aprobacion (percentage)"""

def delete_validacion(id):
    """Delete a single record by id."""

Use context managers (with sqlite3.connect(...) as conn:) for all operations.
Never let database errors crash the app — wrap in try/except and return None/empty on failure.
Store the database in the same directory as the app for Streamlit Cloud compatibility.
```

---

## PROMPT D — Mejorar `report.py` con gráficas y diseño ejecutivo

```
Completely rewrite report.py for a steel MTC Validator app.

Create a professional executive PDF report using fpdf2 and matplotlib.

FUNCTION SIGNATURE:
def generate_pdf(df_resultado, norma_key, veredicto, empresa="", archivo="") -> bytes:

PDF LAYOUT (A4 portrait):

PAGE 1 — PORTADA EJECUTIVA:
- Header bar: dark background (#0d1218) with company name "MTC Validator" in green (#00d4a0)
- Title: "DICTAMEN DE VALIDACIÓN METALÚRGICA"
- Subtitle: norma_key + " — " + full norm name
- Large verdict badge: green box for APROBADO, red for RECHAZADO
- Metadata grid: Fecha, Norma, Archivo, Empresa, N° Elementos
- Horizontal divider line in accent green

PAGE 2 — RESULTADOS DETALLADOS:
- Section title: "ANÁLISIS POR ELEMENTO"
- Table with columns: Elemento | Valor MTC | Mínimo | Máximo | Resultado | Desviación
- Row colors: light green fill for APROBADO rows, light red for RECHAZADO rows
- Bold header row with dark background

CHART (inline in Page 2 after table):
- Use matplotlib to create a horizontal bar chart
- Each element is a bar showing the value relative to min/max range
- Bar color: green if within range, red if out of range
- Add vertical lines for min and max limits
- Title: "Posición de Valores vs. Tolerancias de Norma"
- Save chart as PNG bytes using BytesIO, embed in PDF with fpdf2

PAGE 2 FOOTER:
- "Documento generado automáticamente por MTC Validator — adaga.tech"
- Timestamp
- "Este dictamen es válido únicamente para el lote analizado"

Use FPDF2 (from fpdf import FPDF).
For the chart: import matplotlib.pyplot as plt, matplotlib use Agg backend.
Return PDF as bytes (use pdf.output() and convert to bytes if needed).
Handle the case where df_resultado has 'NO EN NORMA' or 'SIN VALOR' rows gracefully.
```

---

## PROMPT E — Agregar autenticación en `app.py` con streamlit-authenticator

```
Add user authentication to an existing app.py Streamlit MTC Validator.

Use the library: streamlit-authenticator

SETUP:
1. Add to requirements.txt: streamlit-authenticator>=0.3.0, PyYAML

2. Create a file called config.yaml in the project root with this structure:
credentials:
  usernames:
    username1:
      email: user1@example.com
      first_name: User
      last_name: One
      password: securepassword123  # Will be auto-hashed
      roles:
        - viewer
    admin:
      email: admin@example.com
      first_name: Admin
      last_name: User
      password: adminpassword456  # Will be hashed
      roles:
        - admin
cookie:
  expiry_days: 30
  key: your_secret_key_here
  name: mtc_validator_auth

3. In app.py, add authentication BEFORE any other content:

Import:
  import streamlit_authenticator as stauth
  import yaml
  from yaml.loader import SafeLoader

Load config from yaml file OR from st.secrets (for Streamlit Cloud):
  - Try to load from config.yaml first
  - If not found, load credentials from st.secrets['credentials'] (YAML string stored in secrets)

Authentication flow:
  - Create authenticator object
  - Show login form if not authenticated
  - If authentication_status is False: show error "Usuario o contraseña incorrectos"
  - If authentication_status is None: show info "Ingresa tus credenciales"
  - If authenticated: show the full app with logout button in sidebar

In the sidebar, after successful login show:
  - User's name and company
  - Logout button at the bottom

Pass the authenticated username to all database save operations so history is per-user.

For Streamlit Cloud deployment, add a note that credentials should be stored in
Streamlit Cloud Secrets as a YAML string under key 'credentials_yaml', NOT in GitHub.
```

---

## PROMPT F — Integración final en `app.py` (todo junto)

```
Refactor app.py to integrate all new modules into the existing MTC Validator Streamlit app.

MODULES TO INTEGRATE (all already exist):
- normas.py (now has 12 normas with label/descripcion)
- validator.py (bulletproof, unchanged)
- ocr_pdf.py (new — handles PDF extraction)
- database.py (new — SQLite history)
- report.py (improved — executive PDF with charts)
- Authentication via streamlit-authenticator (already added)

NEW FEATURES TO ADD IN app.py:

1. FILE UPLOAD: Accept both .xlsx and .pdf files
   - If PDF: call extract_from_pdf() from ocr_pdf.py
   - Show which extraction method was used: "Extraído con pdfplumber" or "Extraído con Mistral OCR"
   - If extraction found data, show it in an editable st.data_editor so user can correct values before validating
   - Show warning if extraction confidence is low

2. NORM SELECTOR: Update dropdown to show label instead of key
   - Display: "SAE 1045 — Acero Medio Carbono" 
   - Group normas in the selector: ASTM group, SAE group, API group, DIN/EN group, NMX group

3. HISTORY TAB: Add a second tab "📊 Historial" in main content
   - Call get_historial(usuario=current_user) from database.py
   - Show as styled dataframe with columns: Fecha, Norma, Archivo, Veredicto, Cumplimiento%
   - Show stats metrics from get_stats(usuario=current_user):
     Total validaciones, % aprobación, Norma más usada
   - Add a "🗑 Limpiar historial" button (with confirmation)

4. SAVE TO DB: After every successful validation, call save_validacion() automatically

5. REPORT: Update download button to use new generate_pdf() with empresa parameter
   - empresa = st.session_state.get('name', 'Piloto')

6. SIDEBAR: Add version badge "v0.3" and a small stats summary for the logged-in user

Keep ALL existing UI aesthetic (dark theme, JetBrains Mono, green accent #00d4a0).
Keep ALL existing bulletproof error handling.
Do NOT break any existing functionality.
```

---

## ARCHIVO EXTRA — `packages.txt` (requerido para pdf2image en Streamlit Cloud)

Crea un archivo llamado `packages.txt` en la raíz del repo con este contenido exacto:

```
poppler-utils
```

Esto instala poppler en el servidor de Streamlit Cloud, necesario para que pdf2image funcione.

---

## ORDEN DE IMPLEMENTACIÓN:

1. `packages.txt` — crear manualmente (1 línea)
2. PROMPT B — `normas.py` expandido
3. PROMPT C — `database.py`
4. PROMPT A — `ocr_pdf.py`
5. PROMPT D — `report.py` ejecutivo
6. PROMPT E — auth en `app.py`
7. PROMPT F — integración final `app.py`
8. Actualizar `requirements.txt`:
   ```
   streamlit>=1.32.0
   pandas>=2.0.0
   openpyxl>=3.1.0
   fpdf2>=2.7.0
   pdfplumber>=0.10.0
   pdf2image>=1.16.0
   requests>=2.31.0
   matplotlib>=3.7.0
   streamlit-authenticator>=0.3.0
   PyYAML>=6.0
   ```

## CONFIGURACIÓN STREAMLIT CLOUD SECRETS:

En Streamlit Cloud → App Settings → Secrets, agrega:

```toml
MISTRAL_API_KEY = "tu_api_key_de_mistral"  # gratis en console.mistral.ai

# Credenciales de usuarios (NUNCA subir config.yaml a GitHub con contraseñas reales)
[credentials]
# Agrega aquí tus usuarios piloto
```

## EMPRESAS PILOTO — MENSAJE DE PROSPECCIÓN (WhatsApp/Email):

```
Hola [nombre], soy Adrian García, estudiante de Ingeniería en Materiales en FIME-UANL.

Desarrollé una herramienta que automatiza la validación de certificados de calidad MTC 
contra normas ASTM/SAE — lo que normalmente toma 20-40 minutos por lote, 
lo hace en segundos con dictamen PDF incluido.

¿Puedo mostrarte un demo de 15 minutos con sus propios certificados?
Piloto completamente gratuito por 30 días.

Link: [tu URL de Streamlit]
```

Targets prioritarios en Monterrey:
- MetalMekanik: ventas@metalmekanik.com / (81) 2704 4051
- Industrias Unidas Sepúlveda: fundicionesenmonterrey.com (formulario de contacto)
- Alloy Steel Fussion: San Nicolás de los Garza NL
- CNI Tubes & Metalworking: Apodaca NL (Tier 2 automotriz)
