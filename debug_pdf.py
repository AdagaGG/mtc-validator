"""
Debug script para diagnosticar qué está extrayendo pdfplumber del PDF
"""

import pdfplumber
import io

pdf_path = r"C:\Users\adria\Downloads\Mill_test_Certificate_1_.pdf"

print("=" * 80)
print("DIAGNÓSTICO DE PDF")
print("=" * 80)

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"✓ PDF abierto: {len(pdf.pages)} página(s)")
        print()
        
        for page_idx, page in enumerate(pdf.pages):
            print(f"\n--- PÁGINA {page_idx + 1} ---")
            
            # Extraer tablas
            tables = page.extract_tables()
            print(f"Tablas encontradas: {len(tables) if tables else 0}")
            
            if tables:
                for table_idx, table in enumerate(tables):
                    print(f"\n  Tabla {table_idx + 1}:")
                    print(f"  - Filas: {len(table)}")
                    print(f"  - Columnas: {len(table[0]) if table else 0}")
                    print(f"  - Primeras 3 filas:")
                    for row_idx, row in enumerate(table[:3]):
                        print(f"    Fila {row_idx}: {row}")
            
            # Extraer texto
            text = page.extract_text()
            if text:
                print(f"\nTexto extraído ({len(text.split())} palabras):")
                print(text[:500] + "..." if len(text) > 500 else text)
            else:
                print("No se extrajo texto")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
