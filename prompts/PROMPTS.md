# Prompts Exactos para Copilot

## 1. normas.py

```
Create a Python dict called NORMAS with keys SAE1020, SAE1045, ASTM_A36, AISI4140. 
Each key maps to a dict of element names to dicts with min and max float values per ASTM/SAE standard.
```

**Estructura esperada:**
```python
NORMAS = {
    "SAE1020": {
        "C_%": {"min": 0.18, "max": 0.23},
        "Mn_%": {"min": 0.30, "max": 0.55},
        # ... más elementos
    },
    "SAE1045": {
        "C_%": {"min": 0.43, "max": 0.50},
        # ... más elementos
    },
    # ... más normas
}
```

---

## 2. validator.py

```
Write a function validate_mtc(df, norma_key, normas_dict) that takes a pandas DataFrame 
with columns 'elemento' and 'valor', checks each value against min/max in normas_dict[norma_key], 
and returns the df with new columns 'resultado' (APROBADO/RECHAZADO) and 'desviacion' 
(string describing the violation or empty string).
```

**Firma esperada:**
```python
def validate_mtc(df, norma_key, normas_dict):
    """
    Valida elementos contra norma especificada.
    
    Args:
        df: DataFrame con columnas 'elemento' y 'valor'
        norma_key: str - clave de la norma (SAE1020, SAE1045, etc.)
        normas_dict: dict - diccionario de normas (desde normas.py)
    
    Returns:
        DataFrame original + columnas 'resultado' y 'desviacion'
    """
    # Tu código aquí
```

---

## 3. app.py

```
Write a Streamlit app that lets user select a norma from a dropdown, upload an Excel file, 
calls validate_mtc(), displays the result DataFrame with conditional formatting (green/red), 
shows a verdict banner, and has a download button for a PDF report.
```

**Características esperadas:**
- Dropdown para seleccionar norma (SAE1020, SAE1045, ASTM_A36, AISI4140)
- Upload widget para `.xlsx`
- Tabla con columnas coloreadas (verde APROBADO, rojo RECHAZADO)
- Banner con veredicto final
- Botón "Descargar Dictamen"

---

## 4. report.py

```
Write a function generate_pdf(df_resultado, norma_key, verdict) using fpdf2 
that creates a professional PDF report with company header, validation date, 
verdict in large text, and a table of all elements with their values and 
APROBADO/RECHAZADO status. Return as bytes.
```

**Firma esperada:**
```python
def generate_pdf(df_resultado, norma_key, verdict):
    """
    Genera PDF de dictamen.
    
    Args:
        df_resultado: DataFrame with columnas elemento, valor, resultado, desviacion
        norma_key: str - norma utilizada
        verdict: str - 'LOTE APROBADO' o 'LOTE RECHAZADO'
    
    Returns:
        bytes - contenido del PDF listo para descargar
    """
    # Tu código aquí
```

---

## Tips para Usar los Prompts

1. **Copia el prompt** desde la sección correspondiente (1-4)
2. En VS Code, **crea el archivo vacío** (ej: `normas.py`)
3. **Presiona Ctrl+I** (o abre el chat de Copilot)
4. **Pega el prompt exacto**
5. **Presiona Enter** y déjalo generar el código
6. Revisa y ajusta si es necesario

## Orden Recomendado

1. ⏳ `normas.py` — primero (define la estructura de datos)
2. ⏳ `validator.py` — segundo (usa normas.py)
3. ⏳ `report.py` — tercero (usa el resultado de validator.py)
4. ⏳ `app.py` — cuarto (orquesta todo)
5. ⏳ `.streamlit/config.toml` — opcional (manual o Copilot)
