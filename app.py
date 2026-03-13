"""
MTC Validator — Rediseño Industrial Precision
"""

import streamlit as st
import pandas as pd
from normas import NORMAS
from validator import validate_mtc
from report import generate_pdf

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MTC Validator",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Global — PRIMERO ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@400;600;700;800&display=swap');

:root {
  --bg: #080c10;
  --surface: #0d1218;
  --surface2: #111820;
  --border: #1e2835;
  --border2: #263040;
  --accent: #00d4a0;
  --accent2: #00a37a;
  --accent-glow: rgba(0,212,160,0.08);
  --red: #ff4d6a;
  --red-dim: rgba(255,77,106,0.10);
  --text: #c8d8e8;
  --muted: #4a6070;
  --muted2: #6a8090;
  --mono: 'JetBrains Mono', monospace;
  --display: 'Syne', sans-serif;
}

/* Reset Streamlit defaults */
html, body, [class*="css"] { font-family: var(--mono) !important; }
.main .block-container { padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: #0d1218 !important; border-bottom: 1px solid #1e2835; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: #0d1218 !important;
  border-right: 1px solid #1e2835 !important;
}
section[data-testid="stSidebar"] > div { background: #0d1218 !important; }

/* Selectbox */
div[data-baseweb="select"] > div {
  background: #080c10 !important;
  border: 1px solid #263040 !important;
  border-radius: 4px !important;
  font-family: var(--mono) !important;
  color: #00d4a0 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
  background: #0d1218 !important;
  border: 1px dashed #263040 !important;
  border-radius: 8px !important;
  padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: #00a37a !important;
}

/* Buttons */
.stDownloadButton > button, .stButton > button {
  background: #00d4a0 !important;
  color: #080c10 !important;
  border: none !important;
  border-radius: 4px !important;
  font-family: var(--mono) !important;
  font-weight: 600 !important;
  font-size: 0.8rem !important;
  letter-spacing: 0.06em !important;
  padding: 0.5rem 1.2rem !important;
  transition: opacity 0.15s !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
  opacity: 0.85 !important;
  background: #00d4a0 !important;
}

/* Metrics */
[data-testid="metric-container"] {
  background: #111820 !important;
  border: 1px solid #1e2835 !important;
  border-radius: 6px !important;
  padding: 0.75rem 1rem !important;
}
[data-testid="metric-container"] label {
  font-size: 0.65rem !important;
  letter-spacing: 0.1em !important;
  color: #4a6070 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: #00d4a0 !important;
  font-size: 1.4rem !important;
  font-weight: 600 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid #1e2835 !important;
  border-radius: 6px !important;
  overflow: hidden !important;
}

/* Expander */
details {
  background: #0d1218 !important;
  border: 1px solid #1e2835 !important;
  border-radius: 6px !important;
}

/* Info / error / success boxes */
[data-testid="stAlert"] {
  border-radius: 6px !important;
  font-family: var(--mono) !important;
  font-size: 0.8rem !important;
}

/* Divider */
hr { border-color: #1e2835 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080c10; }
::-webkit-scrollbar-thumb { background: #263040; border-radius: 2px; }

/* Custom classes */
.logo-header {
  margin-bottom: 1.5rem;
}
.section-title {
  margin-bottom: 1rem;
}
.metric-kpi {
  font-size: 0.65rem;
  color: #4a6070;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}
.verdict-banner {
  border-radius: 6px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}
.verdict-pass {
  background: rgba(0,212,160,0.07);
  border: 1px solid rgba(0,212,160,0.3);
}
.verdict-fail {
  background: rgba(255,77,106,0.10);
  border: 1px solid rgba(255,77,106,0.3);
}
</style>
""", unsafe_allow_html=True)


# ── Helpers HTML ─────────────────────────────────────────────────────────────
def logo_header():
    return """
    <div class="logo-header">
      <div style="font-size:0.6rem;color:#4a6070;letter-spacing:0.12em;margin-bottom:4px;">
        &gt; SISTEMA ACTIVO
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
                  color:#00d4a0;line-height:1;letter-spacing:-0.02em;">
        MTC<br>Validator
      </div>
      <div style="font-size:0.6rem;color:#4a6070;margin-top:4px;letter-spacing:0.06em;">
        ASTM / SAE / NMX — v0.1
      </div>
    </div>
    """

def section_title(text, sub=None):
    sub_html = f'<div style="font-size:0.7rem;color:#4a6070;margin-top:2px;">{sub}</div>' if sub else ""
    return f"""
    <div class="section-title">
      <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#c8d8e8;">
        {text}
      </div>
      {sub_html}
    </div>
    """

def verdict_banner(texto, subtexto, tipo="pass"):
    if tipo == "pass":
        color = "#00d4a0"
        dot_shadow = "0 0 8px rgba(0,212,160,0.5)"
        banner_class = "verdict-banner verdict-pass"
    else:
        color = "#ff4d6a"
        dot_shadow = "0 0 8px rgba(255,77,106,0.5)"
        banner_class = "verdict-banner verdict-fail"

    return f"""
    <div class="{banner_class}">
      <div style="width:10px;height:10px;border-radius:50%;background:{color};
                  box-shadow:{dot_shadow};flex-shrink:0;"></div>
      <div>
        <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;color:{color};">
          {texto}
        </div>
        <div style="font-size:0.7rem;color:#6a8090;margin-top:2px;">{subtexto}</div>
      </div>
    </div>
    """


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(logo_header(), unsafe_allow_html=True)
    st.markdown('<div class="metric-kpi">NORMA ACTIVA</div>', unsafe_allow_html=True)

    norma_seleccionada = st.selectbox(
        "Norma",
        options=list(NORMAS.keys()),
        index=1,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("ELEMENTOS", len(NORMAS[norma_seleccionada]))
    with col_b:
        st.metric("NORMA", norma_seleccionada.replace("_", " "))

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.6rem;color:#263040;letter-spacing:0.06em;padding-top:8px;'
        'border-top:1px solid #1e2835;">adaga.tech · IMT FIME UANL</div>',
        unsafe_allow_html=True
    )


# ── Main Layout ──────────────────────────────────────────────────────────────
st.markdown(section_title("Validador de Certificados MTC", "Normas ASTM / SAE — Control de Calidad Metalúrgico"), unsafe_allow_html=True)

col_upload, col_info = st.columns([2, 1], gap="large")

with col_upload:
    st.markdown('<div class="metric-kpi">CARGAR CERTIFICADO</div>', unsafe_allow_html=True)
    archivo_subido = st.file_uploader(
        "Certificado",
        type="xlsx",
        help="Columnas requeridas: 'elemento' y 'valor'. Sin celdas combinadas.",
        label_visibility="collapsed"
    )

    with st.expander("📋  Ver formato esperado del Excel"):
        st.markdown("""
        | elemento | valor |
        |----------|-------|
        | C_% | 0.46 |
        | Mn_% | 0.85 |
        | P_% | 0.018 |
        | S_% | 0.022 |
        | YS_MPa | 350 |
        | UTS_MPa | 610 |
        | Elong_% | 18.5 |

        **Reglas estrictas:**
        - Columna A: nombre exacto del elemento (sensible a mayúsculas)
        - Columna B: valor numérico decimal
        - Sin celdas combinadas · Sin logos · Sin colores de celda
        """)

with col_info:
    st.markdown('<div class="metric-kpi">REFERENCIA RÁPIDA</div>', unsafe_allow_html=True)
    norma_data = NORMAS[norma_seleccionada]
    ref_rows = []
    for elem, vals in norma_data.items():
        ref_rows.append({"Elemento": elem, "Mín": vals["min"], "Máx": vals["max"]})
    st.dataframe(
        pd.DataFrame(ref_rows),
        hide_index=True,
        use_container_width=True,
        height=280
    )


# ── Processing ───────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)

if archivo_subido is not None:
    try:
        df = pd.read_excel(archivo_subido)

        # Validar columnas
        required_columns = {"elemento", "valor"}
        if not required_columns.issubset(df.columns):
            st.error(f"❌  Columnas incorrectas. Encontradas: {list(df.columns)}. Requeridas: 'elemento', 'valor'")
            st.stop()

        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        if df["valor"].isna().any():
            st.error("❌  Valores no numéricos detectados en columna 'valor'")
            st.stop()

        # Validar
        df_resultado = validate_mtc(df, norma_seleccionada, NORMAS)

        # Veredicto
        hay_rechazos = (df_resultado["resultado"] == "RECHAZADO").any()
        veredicto = "LOTE RECHAZADO" if hay_rechazos else "LOTE APROBADO"
        n_fail = (df_resultado["resultado"] == "RECHAZADO").sum()
        n_pass = (df_resultado["resultado"] == "APROBADO").sum()

        if hay_rechazos:
            fallas = df_resultado[df_resultado["resultado"] == "RECHAZADO"]["elemento"].tolist()
            subtexto = f"{n_fail} parámetro(s) fuera de tolerancia · {', '.join(fallas)} · Norma {norma_seleccionada}"
            st.markdown(verdict_banner(veredicto, subtexto, "fail"), unsafe_allow_html=True)
        else:
            subtexto = f"{n_pass}/{n_pass} parámetros dentro de especificación · Norma {norma_seleccionada}"
            st.markdown(verdict_banner(veredicto, subtexto, "pass"), unsafe_allow_html=True)

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("TOTAL ELEMENTOS", len(df_resultado))
        with k2:
            st.metric("APROBADOS", n_pass)
        with k3:
            st.metric("RECHAZADOS", n_fail)
        with k4:
            pct = round((n_pass / len(df_resultado)) * 100)
            st.metric("CUMPLIMIENTO", f"{pct}%")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Tabla con colores
        st.markdown('<div class="metric-kpi">DETALLE POR ELEMENTO</div>', unsafe_allow_html=True)

        def color_resultado(val):
            if val == "APROBADO":
                return "background-color: rgba(0,212,160,0.08); color: #00d4a0"
            elif val == "RECHAZADO":
                return "background-color: rgba(255,77,106,0.10); color: #ff4d6a"
            return ""

        df_display = df_resultado[["elemento", "valor", "resultado", "desviacion"]].copy()
        df_display.columns = ["Elemento", "Valor MTC", "Resultado", "Desviación"]

        styled = df_display.style.map(color_resultado, subset=["Resultado"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # PDF download
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

        with st.expander("🔧  Datos crudos del DataFrame"):
            st.dataframe(df_resultado, use_container_width=True)

    except Exception as e:
        st.error(f"❌  Error procesando archivo: {str(e)}")

else:
    st.markdown(
        '<div style="background:#0d1218;border:1px solid #1e2835;border-radius:6px;'
        'padding:20px;text-align:center;color:#4a6070;font-size:0.8rem;">'
        '&gt; Carga un archivo Excel para iniciar la validación_'
        '</div>',
        unsafe_allow_html=True
    )
