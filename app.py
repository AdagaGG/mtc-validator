"""
Aplicación Streamlit para validación de especificaciones metalúrgicas MTC
"""

import streamlit as st
import pandas as pd
from normas import NORMAS
from validator import validate_mtc
from report import generate_pdf


# Configuración del layout
st.set_page_config(
    page_title="MTC Validator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🔍 MTC Validator")
st.markdown("Validador de especificaciones metalúrgicas según normas ASTM/SAE")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    
    # Selector de norma
    norma_seleccionada = st.selectbox(
        "Selecciona la norma a validar:",
        options=list(NORMAS.keys()),
        help="Elige la norma contra la cual validar los elementos"
    )
    
    st.divider()
    
    st.info(
        f"**Norma activa:** {norma_seleccionada}\n\n"
        f"**Elementos requeridos:** {len(NORMAS[norma_seleccionada])}"
    )

# Área principal
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.subheader("Cargar archivo Excel")
    
    # Widget de carga
    archivo_subido = st.file_uploader(
        "Sube tu archivo .xlsx",
        type="xlsx",
        help="El archivo debe tener columnas 'elemento' y 'valor'"
    )
    
    # Mostrar información del formato esperado
    with st.expander("📋 Ver formato esperado"):
        st.markdown("""
        | elemento | valor |
        |----------|-------|
        | C_% | 0.22 |
        | Mn_% | 0.85 |
        | P_% | 0.015 |
        
        **Reglas:**
        - Columna A: nombre de elemento (exacto)
        - Columna B: valor numérico
        - Sin celdas combinadas
        - Sin logos ni imágenes
        """)

with col2:
    st.subheader("Info")
    st.metric("Norma activa", norma_seleccionada)
    st.metric("Elementos", len(NORMAS[norma_seleccionada]))

# Procesamiento
if archivo_subido is not None:
    try:
        # Leer Excel
        df = pd.read_excel(archivo_subido)
        
        # Validar columnas
        required_columns = {"elemento", "valor"}
        if not required_columns.issubset(df.columns):
            st.error(
                f"❌ El Excel debe tener columnas exactamente: 'elemento' y 'valor'\n\n"
                f"Columnas encontradas: {list(df.columns)}"
            )
            st.stop()
        
        # Convertir valores a numérico
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        if df['valor'].isna().any():
            st.error("❌ Algunos valores en la columna 'valor' no son numéricos")
            st.stop()
        
        # Validar
        st.divider()
        st.subheader("📊 Resultados de Validación")
        
        try:
            df_resultado = validate_mtc(df, norma_seleccionada, NORMAS)
        except Exception as e:
            st.error(f"❌ Error en validación: {str(e)}")
            st.stop()
        
        # Determinar veredicto
        hay_rechazos = (df_resultado['resultado'] == 'RECHAZADO').any()
        veredicto = "LOTE RECHAZADO" if hay_rechazos else "LOTE APROBADO"
        
        # Mostrar veredicto en banner
        if hay_rechazos:
            st.error(f"### 🔴 {veredicto}", icon="🔴")
        else:
            st.success(f"### 🟢 {veredicto}", icon="🟢")
        
        st.divider()
        
        # Mostrar tabla con formatos condicionales
        st.subheader("📋 Detalle de Elementos")
        
        # Función para colorear
        def color_resultado(valor):
            if valor == 'APROBADO':
                return 'background-color: #90EE90'  # Verde claro
            else:
                return 'background-color: #FFB6C6'  # Rojo claro
        
        # Mostrar tabla
        df_display = df_resultado[['elemento', 'valor', 'resultado', 'desviacion']].copy()
        
        # Aplicar estilos
        styled_df = df_display.style.applymap(
            lambda x: color_resultado(x) if x in ['APROBADO', 'RECHAZADO'] else '',
            subset=['resultado']
        )
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Botón de descarga PDF
        st.divider()
        st.subheader("📥 Descargar Dictamen")
        
        try:
            pdf_bytes = generate_pdf(df_resultado, norma_seleccionada, veredicto)
            
            st.download_button(
                label="📄 Descargar PDF",
                data=pdf_bytes,
                file_name=f"dictamen_mtc_{norma_seleccionada}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Error generando PDF: {str(e)}")
        
        # Mostrar datos crudos si lo desea
        with st.expander("🔧 Ver datos crudos"):
            st.dataframe(df_resultado)
    
    except Exception as e:
        st.error(f"❌ Error al procesar archivo: {str(e)}")
else:
    st.info("👆 Carga un archivo Excel para comenzar")
