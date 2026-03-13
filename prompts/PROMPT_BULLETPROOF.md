# PROMPT COMPLETO — MTC Validator "Bulletproof" (Usuario Tonto)
# Copia TODO este bloque y pégalo en Copilot Chat (Ctrl+I en VS Code)
# NO modifica normas.py ni report.py

---

## INSTRUCCIÓN PARA COPILOT:

Refactoriza `validator.py` y `app.py` para hacer el sistema completamente
a prueba de errores del usuario. El usuario puede:
- Subir el Excel con la norma equivocada seleccionada
- Usar nombres de elementos distintos (Carbon, C, Carbono, C_%, etc.)
- Subir un Excel con columnas en orden diferente
- Subir un Excel con filas vacías o espacios extras
- No saber qué norma seleccionar

Implementa TODOS los fixes descritos abajo. No toques `normas.py` ni `report.py`.

---

## ARCHIVO 1 — Reemplaza `validator.py` completo:

```python
"""
MTC Validator — validator.py (Bulletproof Edition)
Maneja aliases, auto-detección de norma, y datos sucios del usuario.
"""

import pandas as pd

# ── Aliases de nombres de elementos ─────────────────────────────────────────
# El usuario puede usar cualquier variante — todas se mapean al nombre canónico
ALIASES = {
    # Carbono
    "c": "C_%", "c%": "C_%", "carbon": "C_%", "carbono": "C_%",
    "carbon %": "C_%", "carbon%": "C_%", "c %": "C_%",
    "%c": "C_%", "c_pct": "C_%",

    # Manganeso
    "mn": "Mn_%", "mn%": "Mn_%", "manganeso": "Mn_%", "manganese": "Mn_%",
    "mn %": "Mn_%", "manganese %": "Mn_%", "%mn": "Mn_%",

    # Fósforo
    "p": "P_%", "p%": "P_%", "fosforo": "P_%", "fósforo": "P_%",
    "phosphorus": "P_%", "phosphorus %": "P_%", "p %": "P_%", "%p": "P_%",

    # Azufre
    "s": "S_%", "s%": "S_%", "azufre": "S_%", "sulfur": "S_%",
    "sulfur %": "S_%", "s %": "S_%", "%s": "S_%",

    # Silicio
    "si": "Si_%", "si%": "Si_%", "silicio": "Si_%", "silicon": "Si_%",
    "si %": "Si_%", "%si": "Si_%",

    # Cromo
    "cr": "Cr_%", "cr%": "Cr_%", "cromo": "Cr_%", "chromium": "Cr_%",
    "chrome": "Cr_%", "cr %": "Cr_%", "%cr": "Cr_%",

    # Molibdeno
    "mo": "Mo_%", "mo%": "Mo_%", "molibdeno": "Mo_%", "molybdenum": "Mo_%",
    "mo %": "Mo_%", "%mo": "Mo_%",

    # Yield Strength
    "ys": "YS_MPa", "ys_mpa": "YS_MPa", "yield": "YS_MPa",
    "yield strength": "YS_MPa", "limite elastico": "YS_MPa",
    "límite elástico": "YS_MPa", "re": "YS_MPa", "rp0.2": "YS_MPa",
    "rp02": "YS_MPa", "proof stress": "YS_MPa", "ys (mpa)": "YS_MPa",
    "ys(mpa)": "YS_MPa",

    # Ultimate Tensile Strength
    "uts": "UTS_MPa", "uts_mpa": "UTS_MPa", "tensile": "UTS_MPa",
    "tensile strength": "UTS_MPa", "resistencia a la tension": "UTS_MPa",
    "resistencia tensil": "UTS_MPa", "rm": "UTS_MPa",
    "uts (mpa)": "UTS_MPa", "uts(mpa)": "UTS_MPa", "fu": "UTS_MPa",

    # Elongación
    "elong": "Elong_%", "elong_%": "Elong_%", "elongation": "Elong_%",
    "elongacion": "Elong_%", "elongación": "Elong_%", "el": "Elong_%",
    "a%": "Elong_%", "a %": "Elong_%", "elong %": "Elong_%",
    "elongation %": "Elong_%", "elongation%": "Elong_%",
}

# Nombres canónicos (pasan directo sin alias)
CANONICAL = {
    "C_%", "Mn_%", "P_%", "S_%", "Si_%", "Cr_%", "Mo_%",
    "YS_MPa", "UTS_MPa", "Elong_%"
}


def normalize_element_name(name: str) -> str:
    """
    Convierte cualquier variante de nombre a nombre canónico.
    Retorna el nombre original si no encuentra alias.
    """
    if name in CANONICAL:
        return name
    lookup = name.strip().lower()
    return ALIASES.get(lookup, name)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame crudo del usuario:
    - Detecta columnas 'elemento' y 'valor' sin importar posición o capitalización
    - Elimina filas vacías
    - Normaliza nombres de elementos
    - Convierte valores a numérico
    """
    # Normalizar nombres de columnas
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Buscar columna de elemento (puede llamarse elemento, element, name, chemical, etc.)
    elem_aliases = ["elemento", "element", "name", "chemical", "componente",
                    "component", "analisis", "análisis", "item", "property"]
    val_aliases = ["valor", "value", "resultado", "result", "medicion",
                   "medición", "measurement", "cantidad", "amount", "data"]

    elem_col = None
    val_col = None

    for col in df.columns:
        if any(a in col for a in elem_aliases) and elem_col is None:
            elem_col = col
        if any(a in col for a in val_aliases) and val_col is None:
            val_col = col

    # Si no encontró por nombre, asumir columna A = elemento, columna B = valor
    if elem_col is None or val_col is None:
        cols = list(df.columns)
        if len(cols) >= 2:
            elem_col = cols[0]
            val_col = cols[1]
        else:
            raise ValueError(
                "No se detectaron columnas válidas. "
                "El archivo debe tener al menos 2 columnas: elementos y valores."
            )

    # Extraer y limpiar
    df_clean = pd.DataFrame({
        "elemento": df[elem_col].astype(str).str.strip(),
        "valor": df[val_col],
    })

    # Eliminar filas vacías o con 'nan'
    df_clean = df_clean[
        df_clean["elemento"].notna() &
        (df_clean["elemento"] != "") &
        (df_clean["elemento"].str.lower() != "nan") &
        (df_clean["elemento"].str.lower() != "elemento") &
        (df_clean["elemento"].str.lower() != "element")
    ].reset_index(drop=True)

    # Normalizar nombres de elementos con aliases
    df_clean["elemento"] = df_clean["elemento"].apply(normalize_element_name)

    # Convertir valores a numérico
    df_clean["valor"] = pd.to_numeric(df_clean["valor"], errors="coerce")

    return df_clean


def detect_norma(df_clean: pd.DataFrame, normas_dict: dict) -> str:
    """
    Auto-detecta la norma más probable basándose en los valores del DataFrame.
    Calcula cuántos elementos de cada norma están dentro de tolerancia
    y retorna la norma con mayor porcentaje de cumplimiento.
    Útil como sugerencia cuando el usuario no sabe qué norma seleccionar.
    """
    best_norma = None
    best_score = -1

    elem_val = dict(zip(df_clean["elemento"], df_clean["valor"]))

    for norma_key, specs in normas_dict.items():
        matched = 0
        total = 0
        for elem, limits in specs.items():
            if elem in elem_val and pd.notna(elem_val[elem]):
                total += 1
                v = float(elem_val[elem])
                if limits["min"] <= v <= limits["max"]:
                    matched += 1
        score = matched / total if total > 0 else 0
        if score > best_score:
            best_score = score
            best_norma = norma_key

    return best_norma, round(best_score * 100)


def validate_mtc(df: pd.DataFrame, norma_key: str, normas_dict: dict) -> pd.DataFrame:
    """
    Valida elementos contra norma especificada.

    Args:
        df: DataFrame con columnas 'elemento' y 'valor' (ya limpio)
        norma_key: str - clave de la norma
        normas_dict: dict - diccionario de normas

    Returns:
        DataFrame con columnas 'resultado' y 'desviacion' agregadas
    """
    if norma_key not in normas_dict:
        raise ValueError(
            f"Norma '{norma_key}' no existe. "
            f"Disponibles: {list(normas_dict.keys())}"
        )

    norma = normas_dict[norma_key]
    df_resultado = df.copy()
    df_resultado["resultado"] = "NO EVALUADO"
    df_resultado["desviacion"] = ""

    for idx, row in df_resultado.iterrows():
        elemento = str(row["elemento"]).strip()
        valor = row["valor"]

        # Si el elemento no está en la norma, marcarlo como no evaluado
        if elemento not in norma:
            df_resultado.loc[idx, "resultado"] = "NO EN NORMA"
            df_resultado.loc[idx, "desviacion"] = (
                f"'{elemento}' no existe en {norma_key}. "
                f"Elementos válidos: {', '.join(norma.keys())}"
            )
            continue

        # Si el valor es NaN
        if pd.isna(valor):
            df_resultado.loc[idx, "resultado"] = "SIN VALOR"
            df_resultado.loc[idx, "desviacion"] = "Valor no numérico o vacío"
            continue

        valor_num = float(valor)
        min_val = norma[elemento]["min"]
        max_val = norma[elemento]["max"]

        if min_val <= valor_num <= max_val:
            df_resultado.loc[idx, "resultado"] = "APROBADO"
            df_resultado.loc[idx, "desviacion"] = ""
        else:
            df_resultado.loc[idx, "resultado"] = "RECHAZADO"
            if valor_num < min_val:
                df_resultado.loc[idx, "desviacion"] = (
                    f"Bajo mínimo: {valor_num} < {min_val}"
                )
            else:
                df_resultado.loc[idx, "desviacion"] = (
                    f"Sobre máximo: {valor_num} > {max_val}"
                )

    return df_resultado
```

---

## ARCHIVO 2 — Reemplaza `app.py` completo:

```python
"""
MTC Validator — app.py (Bulletproof Edition)
UI a prueba de errores del usuario.
"""

import streamlit as st
import pandas as pd
import io
from normas import NORMAS
from validator import validate_mtc, clean_dataframe, detect_norma
from report import generate_pdf

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MTC Validator",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@400;600;700;800&display=swap');
:root {
  --accent: #00d4a0; --red: #ff4d6a; --yellow: #f5a623;
  --surface: #0d1218; --border: #1e2835;
  --mono: 'JetBrains Mono', monospace; --display: 'Syne', sans-serif;
}
html, body, [class*="css"] { font-family: var(--mono) !important; }
.main .block-container { padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: #0d1218 !important; border-bottom: 1px solid #1e2835; }
section[data-testid="stSidebar"] { background: #0d1218 !important; border-right: 1px solid #1e2835 !important; }
section[data-testid="stSidebar"] > div { background: #0d1218 !important; }
div[data-baseweb="select"] > div {
  background: #080c10 !important; border: 1px solid #263040 !important;
  border-radius: 4px !important; font-family: var(--mono) !important; color: #00d4a0 !important;
}
[data-testid="metric-container"] {
  background: #111820 !important; border: 1px solid #1e2835 !important;
  border-radius: 6px !important; padding: 0.75rem 1rem !important;
}
[data-testid="metric-container"] label { font-size: 0.65rem !important; letter-spacing: 0.1em !important; color: #4a6070 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00d4a0 !important; font-size: 1.4rem !important; font-weight: 600 !important; }
.stDownloadButton > button, .stButton > button {
  background: #00d4a0 !important; color: #080c10 !important; border: none !important;
  border-radius: 4px !important; font-family: var(--mono) !important;
  font-weight: 600 !important; font-size: 0.8rem !important; letter-spacing: 0.06em !important;
}
[data-testid="stDataFrame"] { border: 1px solid #1e2835 !important; border-radius: 6px !important; }
hr { border-color: #1e2835 !important; }
::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-thumb { background: #263040; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def verdict_banner(texto, subtexto, tipo="pass"):
    cfg = {
        "pass":    ("#00d4a0", "rgba(0,212,160,0.07)",  "rgba(0,212,160,0.3)",  "0 0 8px rgba(0,212,160,0.5)"),
        "fail":    ("#ff4d6a", "rgba(255,77,106,0.10)", "rgba(255,77,106,0.3)", "0 0 8px rgba(255,77,106,0.5)"),
        "warning": ("#f5a623", "rgba(245,166,35,0.08)", "rgba(245,166,35,0.3)", "0 0 8px rgba(245,166,35,0.5)"),
    }
    color, bg, border, shadow = cfg.get(tipo, cfg["pass"])
    return f"""
    <div style="background:{bg};border:1px solid {border};border-radius:6px;
                padding:14px 18px;display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
      <div style="width:10px;height:10px;border-radius:50%;background:{color};
                  box-shadow:{shadow};flex-shrink:0;"></div>
      <div>
        <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;color:{color};">
          {texto}
        </div>
        <div style="font-size:0.7rem;color:#6a8090;margin-top:2px;">{subtexto}</div>
      </div>
    </div>"""


def generate_template(norma_key: str) -> bytes:
    """Genera Excel plantilla descargable con los elementos de la norma seleccionada."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    wb = Workbook()
    ws = wb.active
    ws.title = "MTC"
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 30

    # Headers
    for col, val in [("A1", "elemento"), ("B1", "valor"), ("C1", "referencia")]:
        ws[col] = val
        ws[col].font = Font(bold=True, color="00D4A0", name="Courier New")
        ws[col].fill = PatternFill("solid", start_color="0D1218")
        ws[col].alignment = Alignment(horizontal="center")

    # Filas con elementos de la norma
    norma = NORMAS[norma_key]
    for i, (elem, limits) in enumerate(norma.items(), start=2):
        ws[f"A{i}"] = elem
        ws[f"B{i}"] = ""  # El usuario llena aquí
        ws[f"C{i}"] = f"Min: {limits['min']} | Max: {limits['max']}"
        ws[f"A{i}"].font = Font(name="Courier New", size=10)
        ws[f"B{i}"].font = Font(name="Courier New", size=10, bold=True)
        ws[f"C{i}"].font = Font(name="Courier New", size=9, color="4A6070")
        ws[f"B{i}"].alignment = Alignment(horizontal="right")

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
      <div style="font-size:0.6rem;color:#4a6070;letter-spacing:0.12em;margin-bottom:4px;">&gt; SISTEMA ACTIVO</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#00d4a0;line-height:1;letter-spacing:-0.02em;">MTC<br>Validator</div>
      <div style="font-size:0.6rem;color:#4a6070;margin-top:4px;letter-spacing:0.06em;">ASTM / SAE / NMX — v0.2</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.6rem;color:#4a6070;letter-spacing:0.1em;margin-bottom:6px;">NORMA A VALIDAR</div>', unsafe_allow_html=True)

    norma_seleccionada = st.selectbox(
        "Norma", options=list(NORMAS.keys()), index=0, label_visibility="collapsed"
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Métricas
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("ELEMENTOS", len(NORMAS[norma_seleccionada]))
    with col_b:
        st.metric("VERSIÓN", "0.2")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Plantilla descargable
    st.markdown('<div style="font-size:0.6rem;color:#4a6070;letter-spacing:0.1em;margin-bottom:6px;">PLANTILLA EXCEL</div>', unsafe_allow_html=True)
    template_bytes = generate_template(norma_seleccionada)
    st.download_button(
        label="↓ Descargar Plantilla",
        data=template_bytes,
        file_name=f"plantilla_mtc_{norma_seleccionada}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        help="Descarga la plantilla con los elementos de esta norma. Solo llena la columna 'valor'."
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Tabla de referencia de tolerancias
    st.markdown('<div style="font-size:0.6rem;color:#4a6070;letter-spacing:0.1em;margin-bottom:6px;">TOLERANCIAS — ' + norma_seleccionada + '</div>', unsafe_allow_html=True)
    ref_data = [{"Elemento": k, "Mín": v["min"], "Máx": v["max"]} for k, v in NORMAS[norma_seleccionada].items()]
    st.dataframe(pd.DataFrame(ref_data), hide_index=True, use_container_width=True, height=250)

    st.markdown('<div style="font-size:0.6rem;color:#263040;letter-spacing:0.06em;padding-top:8px;border-top:1px solid #1e2835;">adaga.tech · IMT FIME UANL</div>', unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#c8d8e8;">
    Validador de Certificados MTC
  </div>
  <div style="font-size:0.7rem;color:#4a6070;margin-top:2px;">
    Normas ASTM / SAE — Control de Calidad Metalúrgico
  </div>
</div>
""", unsafe_allow_html=True)

# ── Instrucciones claras antes del upload ─────────────────────────────────────
with st.expander("📋  ¿Cómo usar? Lee esto primero (30 segundos)", expanded=False):
    st.markdown(f"""
    **Paso 1 — Selecciona la norma** en el panel izquierdo.
    > ¿No sabes cuál? Descarga la plantilla y el sistema sugerirá la norma más probable.

    **Paso 2 — Prepara tu Excel** con 2 columnas:
    | elemento | valor |
    |----------|-------|
    | C_% | 0.22 |
    | Mn_% | 0.85 |
    | ... | ... |

    > **Alternativa:** Descarga la plantilla `plantilla_mtc_{norma_seleccionada}.xlsx` desde el panel izquierdo.
    > Solo llena la columna **valor** con los datos de tu certificado.

    **Paso 3 — Sube el archivo** y descarga el dictamen PDF.

    **Nombres de elementos aceptados** (el sistema reconoce variantes automáticamente):
    - Carbono: `C`, `C_%`, `Carbon`, `Carbono`, `Carbon %`
    - Manganeso: `Mn`, `Mn_%`, `Manganese`, `Manganeso`
    - Fósforo: `P`, `P_%`, `Phosphorus`, `Fosforo`
    - Azufre: `S`, `S_%`, `Sulfur`, `Azufre`
    - Yield Strength: `YS`, `YS_MPa`, `Yield`, `Re`, `Rp0.2`
    - Tensile Strength: `UTS`, `UTS_MPa`, `Tensile`, `Rm`
    - Elongación: `Elong`, `Elong_%`, `Elongation`, `El`, `A%`
    """)

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:0.65rem;color:#4a6070;letter-spacing:0.1em;margin-bottom:8px;">CARGAR CERTIFICADO (.xlsx)</div>', unsafe_allow_html=True)

archivo_subido = st.file_uploader(
    "Certificado",
    type=["xlsx", "xls"],
    help="Sube el Excel con los datos del certificado de tu proveedor. Si no tienes el formato correcto, descarga la plantilla desde el panel izquierdo.",
    label_visibility="collapsed"
)

# ── Processing ────────────────────────────────────────────────────────────────
if archivo_subido is not None:
    try:
        # Leer Excel crudo
        df_raw = pd.read_excel(archivo_subido)

        if df_raw.empty:
            st.error("❌  El archivo está vacío. Verifica que tenga datos.")
            st.stop()

        # Limpiar y normalizar
        try:
            df_clean = clean_dataframe(df_raw)
        except ValueError as e:
            st.error(f"❌  Error en el formato del archivo: {str(e)}")
            with st.expander("Ver contenido crudo del archivo"):
                st.dataframe(df_raw)
            st.stop()

        if df_clean.empty:
            st.error("❌  No se encontraron datos válidos en el archivo después de limpiar filas vacías.")
            st.stop()

        # ── Auto-detección de norma ───────────────────────────────────────────
        norma_detectada, score = detect_norma(df_clean, NORMAS)

        if norma_detectada != norma_seleccionada and score >= 60:
            st.warning(
                f"⚠️  Los datos parecen corresponder a **{norma_detectada}** "
                f"({score}% de elementos dentro de tolerancia), "
                f"pero tienes seleccionada **{norma_seleccionada}**. "
                f"¿Es correcta la norma seleccionada?"
            )

        # ── Validar ───────────────────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)

        df_resultado = validate_mtc(df_clean, norma_seleccionada, NORMAS)

        # Contar resultados
        n_total    = len(df_resultado)
        n_aprobado = (df_resultado["resultado"] == "APROBADO").sum()
        n_rechazado = (df_resultado["resultado"] == "RECHAZADO").sum()
        n_no_norma = (df_resultado["resultado"] == "NO EN NORMA").sum()
        n_sin_valor = (df_resultado["resultado"] == "SIN VALOR").sum()
        hay_rechazos = n_rechazado > 0

        veredicto = "LOTE RECHAZADO" if hay_rechazos else "LOTE APROBADO"

        # ── Banner veredicto ─────────────────────────────────────────────────
        if hay_rechazos:
            fallas = df_resultado[df_resultado["resultado"] == "RECHAZADO"]["elemento"].tolist()
            subtexto = f"{n_rechazado} parámetro(s) fuera de tolerancia · {', '.join(fallas)} · Norma {norma_seleccionada}"
            st.markdown(verdict_banner(veredicto, subtexto, "fail"), unsafe_allow_html=True)
        else:
            subtexto = f"{n_aprobado}/{n_total} parámetros dentro de especificación · Norma {norma_seleccionada}"
            st.markdown(verdict_banner(veredicto, subtexto, "pass"), unsafe_allow_html=True)

        # Advertencias adicionales
        if n_no_norma > 0:
            elementos_extra = df_resultado[df_resultado["resultado"] == "NO EN NORMA"]["elemento"].tolist()
            st.warning(f"⚠️  {n_no_norma} elemento(s) no reconocidos en {norma_seleccionada}: `{', '.join(elementos_extra)}` — no fueron evaluados.")

        if n_sin_valor > 0:
            st.warning(f"⚠️  {n_sin_valor} elemento(s) sin valor numérico — verifica el archivo.")

        # ── KPIs ─────────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("TOTAL", n_total)
        with k2: st.metric("APROBADOS", n_aprobado)
        with k3: st.metric("RECHAZADOS", n_rechazado)
        with k4:
            evaluados = n_aprobado + n_rechazado
            pct = round((n_aprobado / evaluados) * 100) if evaluados > 0 else 0
            st.metric("CUMPLIMIENTO", f"{pct}%")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Tabla con colores ─────────────────────────────────────────────────
        st.markdown('<div style="font-size:0.65rem;color:#4a6070;letter-spacing:0.1em;margin-bottom:8px;">DETALLE POR ELEMENTO</div>', unsafe_allow_html=True)

        def color_resultado(val):
            if val == "APROBADO":     return "background-color: rgba(0,212,160,0.08); color: #00d4a0"
            elif val == "RECHAZADO":  return "background-color: rgba(255,77,106,0.10); color: #ff4d6a"
            elif val == "NO EN NORMA": return "background-color: rgba(245,166,35,0.08); color: #f5a623"
            elif val == "SIN VALOR":  return "background-color: rgba(245,166,35,0.08); color: #f5a623"
            return ""

        df_display = df_resultado[["elemento", "valor", "resultado", "desviacion"]].copy()
        df_display.columns = ["Elemento", "Valor MTC", "Resultado", "Desviación"]
        styled = df_display.style.map(color_resultado, subset=["Resultado"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # ── PDF Download ──────────────────────────────────────────────────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        try:
            pdf_bytes = generate_pdf(df_resultado, norma_seleccionada, veredicto)
            st.download_button(
                label="↓  DESCARGAR DICTAMEN PDF",
                data=pdf_bytes,
                file_name=f"dictamen_mtc_{norma_seleccionada}.pdf",
                mime="application/pdf",
                use_container_width=False,
            )
        except Exception as e:
            st.error(f"❌  Error generando PDF: {str(e)}")

        with st.expander("🔧  Datos procesados (debug)"):
            st.dataframe(df_resultado, use_container_width=True)

    except Exception as e:
        st.error(f"❌  Error inesperado: {str(e)}")
        st.info("💡  Si el error persiste, descarga la plantilla desde el panel izquierdo y úsala para ingresar tus datos.")

else:
    st.markdown(
        '<div style="background:#0d1218;border:1px solid #1e2835;border-radius:6px;'
        'padding:20px;text-align:center;color:#4a6070;font-size:0.8rem;">'
        '&gt; Carga un archivo Excel para iniciar la validación_'
        '</div>',
        unsafe_allow_html=True
    )
```

---

## PASO 3 — Instala dependencias y corre:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## QUÉ HACE ESTE SISTEMA AHORA (a prueba de usuario tonto):

### Problemas que ya no pueden ocurrir:
- ✅ Usuario sube Excel con norma equivocada → sistema AVISA automáticamente
- ✅ Usuario escribe "Carbon" en vez de "C_%" → alias lo mapea automáticamente
- ✅ Usuario tiene filas vacías en el Excel → se limpian automáticamente
- ✅ Usuario pone el header en mayúsculas → se normaliza automáticamente
- ✅ Usuario no sabe el formato → plantilla descargable con los campos pre-llenados
- ✅ Usuario sube Excel con columnas en orden distinto → se detectan por nombre
- ✅ Elemento no existe en la norma → se marca "NO EN NORMA" sin romper la app
- ✅ Valor no numérico → se marca "SIN VALOR" sin romper la app
- ✅ applymap deprecated → reemplazado por .map() (Pandas 2.0+)

### Lo que el usuario ve si se equivoca:
- Banner amarillo de advertencia con explicación clara
- Botón de plantilla descargable siempre visible en sidebar
- Instrucciones expandibles con ejemplos de nombres aceptados
- Mensaje de error con sugerencia de solución, nunca pantalla rota
