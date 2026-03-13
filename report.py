"""
Generación de PDF de dictamen de validación MTC
"""

from io import BytesIO
from datetime import datetime
from fpdf import FPDF
import pandas as pd
from normas import NORMAS


def generate_pdf(df_resultado, norma_key, verdict):
    """
    Genera PDF de dictamen de validación.
    
    Crea un reporte profesional en PDF con encabezado, fecha, veredicto y tabla 
    de elementos validados. Retorna los bytes del PDF listo para descargar.
    
    Args:
        df_resultado: DataFrame con columnas elemento, valor, resultado, desviacion
        norma_key: str - norma utilizada (SAE1020, SAE1045, ASTM_A36, AISI4140)
        verdict: str - 'LOTE APROBADO' o 'LOTE RECHAZADO'
    
    Returns:
        bytes - contenido del PDF listo para descargar
    """
    
    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Encabezado
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(0, 10, "DICTAMEN DE VALIDACION MTC", ln=True, align="C")
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, "", ln=True)  # Espacio
    
    # Fecha y norma
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Fecha de Validación: {fecha}", ln=True)
    pdf.cell(0, 5, f"Norma Aplicada: {norma_key}", ln=True)
    pdf.cell(0, 5, "", ln=True)  # Espacio
    
    # Veredicto en grande
    pdf.set_font("Arial", "B", size=14)
    
    # Color según veredicto
    if "APROBADO" in verdict:
        pdf.set_text_color(0, 150, 0)  # Verde
    else:
        pdf.set_text_color(200, 0, 0)  # Rojo
    
    pdf.cell(0, 10, f"VEREDICTO: {verdict}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)  # Reset a negro
    
    pdf.cell(0, 5, "", ln=True)  # Espacio
    
    # Tabla de elementos
    pdf.set_font("Arial", "B", size=9)
    
    # Headers de tabla
    col_widths = [40, 25, 25, 40, 45]
    headers = ["Elemento", "Valor", "Resultado", "Min", "Max"]
    
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 7, header, border=1, align="C")
    pdf.ln()
    
    # Datos de tabla
    pdf.set_font("Arial", size=8)
    
    for idx, row in df_resultado.iterrows():
        elemento = str(row['elemento'])
        valor = f"{row['valor']:.2f}" if isinstance(row['valor'], (int, float)) else str(row['valor'])
        resultado = str(row['resultado'])
        
        # Obtener min/max desde el diccionario de normas
        specs = NORMAS.get(norma_key, {}).get(str(row['elemento']), {})
        min_val = str(specs.get('min', '-'))
        max_val = str(specs.get('max', '-'))
        
        # Colorear fila según resultado
        if "APROBADO" in resultado:
            pdf.set_fill_color(200, 255, 200)  # Verde claro
        else:
            pdf.set_fill_color(255, 200, 200)  # Rojo claro
        
        pdf.cell(col_widths[0], 6, elemento, border=1, fill=True)
        pdf.cell(col_widths[1], 6, valor, border=1, align="R", fill=True)
        pdf.cell(col_widths[2], 6, resultado, border=1, align="C", fill=True)
        pdf.cell(col_widths[3], 6, min_val, border=1, align="C", fill=True)
        pdf.cell(col_widths[4], 6, max_val, border=1, align="C", fill=True)
        pdf.ln()
    
    # Pie de página
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "", ln=True)
    pdf.cell(0, 5, "Documento generado automáticamente por MTC Validator", 
             align="C")
    
    # Retornar como bytes
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output
