"""
MTC Validator — report.py v2
Professional executive PDF reports with charts
"""

import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import io
from datetime import datetime
from normas import NORMAS


def generate_pdf(df_resultado, norma_key, veredicto, empresa="", archivo="") -> bytes:
    """
    Generate professional executive PDF report with charts.
    
    Args:
        df_resultado: DataFrame with validation results (columns: elemento, valor, resultado, desviacion)
        norma_key: str — norm key (e.g., 'SAE1045')
        veredicto: str — 'LOTE APROBADO' or 'LOTE RECHAZADO'
        empresa: str — company name (optional)
        archivo: str — original filename (optional)
    
    Returns:
        bytes — PDF content
    """
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # ── PAGE 1 — COVER ───────────────────────────────────────────────────────────
    # Header bar
    pdf.set_fill_color(13, 28, 24)  # #0d1218
    pdf.cell(210, 25, "", fill=True, ln=True)
    
    pdf.set_text_color(0, 212, 160)  # #00d4a0 accent green
    pdf.set_font("Courier", "B", 20)
    pdf.set_xy(10, 8)
    pdf.cell(190, 8, "MTC VALIDATOR", ln=True, align="L")
    
    # Title
    pdf.set_text_color(50, 50, 50)  # Dark gray
    pdf.set_font("Courier", "B", 18)
    pdf.set_xy(10, 35)
    pdf.cell(190, 10, "DICTAMEN DE VALIDACION", ln=True, align="C")
    pdf.set_font("Courier", "", 12)
    pdf.cell(190, 8, "METALURGICA", ln=True, align="C")
    
    # Norm info
    norma_label = NORMAS.get(norma_key, {}).get("label", norma_key)
    pdf.set_font("Courier", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(190, 6, f"{norma_label}", ln=True, align="C")
    
    # Verdict badge
    pdf.ln(8)
    n_aprobado = (df_resultado["resultado"] == "APROBADO").sum()
    n_total = len(df_resultado)
    
    if veredicto == "LOTE APROBADO":
        color = (0, 212, 160)  # Green
    else:
        color = (255, 77, 106)  # Red
    
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Courier", "B", 16)
    pdf.multi_cell(190, 15, veredicto, align="C", fill=True)
    
    # Metadata grid
    pdf.ln(8)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Courier", "B", 9)
    
    col_width = 95
    pdf.set_xy(10, pdf.get_y())
    pdf.cell(col_width, 6, "Fecha", border=1, align="L")
    pdf.cell(col_width, 6, datetime.now().strftime("%Y-%m-%d %H:%M"), border=1, ln=True)
    
    pdf.set_xy(10, pdf.get_y())
    pdf.cell(col_width, 6, "Norma", border=1, align="L")
    pdf.cell(col_width, 6, norma_key, border=1, ln=True)
    
    pdf.set_xy(10, pdf.get_y())
    pdf.cell(col_width, 6, "Archivo", border=1, align="L")
    pdf.cell(col_width, 6, archivo[:40] if archivo else "Manual", border=1, ln=True)
    
    pdf.set_xy(10, pdf.get_y())
    pdf.cell(col_width, 6, "Empresa", border=1, align="L")
    pdf.cell(col_width, 6, empresa[:40] if empresa else "Piloto", border=1, ln=True)
    
    pdf.set_xy(10, pdf.get_y())
    pdf.cell(col_width, 6, f"Elementos", border=1, align="L")
    pdf.cell(col_width, 6, f"{n_total} evaluados", border=1, ln=True)
    
    # ── PAGE 2 — DETAILED RESULTS ────────────────────────────────────────────────
    pdf.add_page()
    
    pdf.set_font("Courier", "B", 12)
    pdf.set_text_color(0, 212, 160)
    pdf.cell(190, 8, "ANALISIS POR ELEMENTO", ln=True)
    
    # Results table header
    pdf.set_font("Courier", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(13, 28, 24)  # Dark header
    
    col_widths = [25, 20, 20, 20, 25, 80]  # elemento, valor, min, max, resultado, desviacion
    
    pdf.cell(col_widths[0], 6, "Elemento", border=1, fill=True, align="C")
    pdf.cell(col_widths[1], 6, "Valor", border=1, fill=True, align="C")
    pdf.cell(col_widths[2], 6, "Minimo", border=1, fill=True, align="C")
    pdf.cell(col_widths[3], 6, "Maximo", border=1, fill=True, align="C")
    pdf.cell(col_widths[4], 6, "Resultado", border=1, fill=True, align="C")
    pdf.cell(col_widths[5], 6, "Desviacion", border=1, fill=True, ln=True, align="C")
    
    # Results rows
    pdf.set_font("Courier", "", 7)
    
    for idx, row in df_resultado.iterrows():
        elemento = row["elemento"]
        valor = row["valor"]
        resultado = row["resultado"]
        desviacion = row["desviacion"][:30] if row["desviacion"] else ""  # Truncate
        
        # Get min/max from NORMAS
        norma_spec = NORMAS.get(norma_key, {})
        elem_spec = norma_spec.get(elemento, {})
        min_val = elem_spec.get("min", "-") if elem_spec else "-"
        max_val = elem_spec.get("max", "-") if elem_spec else "-"
        
        # Color based on result
        if resultado == "APROBADO":
            pdf.set_fill_color(200, 240, 220)  # Light green
            pdf.set_text_color(0, 100, 50)
        elif resultado == "RECHAZADO":
            pdf.set_fill_color(255, 220, 220)  # Light red
            pdf.set_text_color(200, 0, 0)
        else:
            pdf.set_fill_color(255, 250, 200)  # Light yellow
            pdf.set_text_color(150, 100, 0)
        
        # Format values
        valor_str = f"{valor:.4f}" if isinstance(valor, float) else str(valor)
        min_str = f"{min_val:.2f}" if isinstance(min_val, (int, float)) else str(min_val)
        max_str = f"{max_val:.2f}" if isinstance(max_val, (int, float)) else str(max_val)
        
        pdf.cell(col_widths[0], 6, str(elemento)[:20], border=1, fill=True)
        pdf.cell(col_widths[1], 6, valor_str, border=1, fill=True, align="C")
        pdf.cell(col_widths[2], 6, min_str, border=1, fill=True, align="C")
        pdf.cell(col_widths[3], 6, max_str, border=1, fill=True, align="C")
        pdf.cell(col_widths[4], 6, resultado[:8], border=1, fill=True, align="C")
        pdf.cell(col_widths[5], 6, desviacion, border=1, fill=True, ln=True)
    
    # Chart
    pdf.ln(8)
    try:
        chart_bytes = _generate_chart(df_resultado, norma_key)
        if chart_bytes:
            chart_image = io.BytesIO(chart_bytes)
            pdf.image(chart_image, x=15, w=180)
    except Exception as e:
        print(f"Error generating chart: {e}")
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Courier", "", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(190, 4, "Documento generado automaticamente por MTC Validator — adaga.tech", ln=True, align="C")
    pdf.cell(190, 4, "Este dictamen es valido unicamente para el lote analizado", ln=True, align="C")
    
    # Return as bytes
    return pdf.output(dest="S").encode("latin-1")


def _generate_chart(df_resultado, norma_key) -> bytes:
    """
    Generate horizontal bar chart showing values vs tolerances.
    Returns PNG bytes or None on error.
    """
    try:
        # Filter only evaluated elements
        df_chart = df_resultado[df_resultado["resultado"].isin(["APROBADO", "RECHAZADO"])].copy()
        
        if df_chart.empty:
            return None
        
        # Prepare data
        elementos = []
        valores = []
        min_vals = []
        max_vals = []
        colores = []
        
        for idx, row in df_chart.iterrows():
            elem = row["elemento"]
            val = row["valor"]
            resultado = row["resultado"]
            
            spec = NORMAS.get(norma_key, {}).get(elem, {})
            min_v = spec.get("min", 0)
            max_v = spec.get("max", 100)
            
            elementos.append(elem)
            valores.append(val if isinstance(val, (int, float)) else 0)
            min_vals.append(min_v)
            max_vals.append(max_v)
            
            if resultado == "APROBADO":
                colores.append("#00d4a0")  # Green
            else:
                colores.append("#ff4d6a")  # Red
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        y_pos = range(len(elementos))
        
        # Plot min-max range as background
        for i, (minv, maxv) in enumerate(zip(min_vals, max_vals)):
            ax.barh(i, maxv - minv, left=minv, height=0.3, color="#e0e0e0", alpha=0.5)
        
        # Plot actual values
        ax.barh(y_pos, valores, color=colores, alpha=0.8, height=0.6)
        
        # Add value labels
        for i, (val, minv, maxv) in enumerate(zip(valores, min_vals, max_vals)):
            ax.text(val, i, f" {val:.2f}", va="center", fontsize=8, fontweight="bold")
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(elementos, fontsize=9)
        ax.set_xlabel("Valor / Rango de Tolerancia", fontsize=10)
        ax.set_title("Posicion de Valores vs. Tolerancias de Norma", fontsize=12, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)
        
        plt.tight_layout()
        
        # Save as PNG bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        
        return buf.getvalue()
    except Exception as e:
        print(f"Error in chart generation: {e}")
        return None
    pdf.cell(0, 5, "Documento generado automáticamente por MTC Validator", 
             align="C")
    
    # Retornar como bytes
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    return pdf_output
