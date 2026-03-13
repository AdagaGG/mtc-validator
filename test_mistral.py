"""
Test script para verificar que Mistral OCR extrae datos correctamente
"""

import sys
sys.path.insert(0, r"c:\Users\adria\Desktop\Proyectos Personales\Validador MTC")

from ocr_pdf import extract_from_pdf

pdf_path = r"C:\Users\adria\Downloads\Mill_test_Certificate_1_.pdf"

print("=" * 80)
print("TEST MISTRAL OCR")
print("=" * 80)

try:
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    df, metodo = extract_from_pdf(pdf_bytes)
    
    print(f"\n✓ Método utilizado: {metodo}")
    print(f"✓ Elementos extraídos: {len(df)}")
    
    if not df.empty:
        print("\nDatos extraídos:")
        print(df.to_string())
    else:
        print("\n❌ DataFrame vacío")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
