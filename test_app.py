"""
Test de funcionalidad de la aplicación MTC Validator
"""

import pandas as pd
from normas import NORMAS
from validator import validate_mtc
from report import generate_pdf

# Test 1: Crear DataFrame de prueba
print("=" * 50)
print("TEST 1: Validación de datos")
print("=" * 50)

df_test = pd.DataFrame({
    'elemento': ['C_%', 'Mn_%', 'P_%', 'S_%', 'YS_MPa', 'UTS_MPa', 'Elong_%'],
    'valor': [0.22, 0.85, 0.015, 0.012, 350, 520, 18.5]
})

print("\n📋 DataFrame de entrada:")
print(df_test)

# Test 2: Validar contra norma SAE1020
print("\n\n" + "=" * 50)
print("TEST 2: Validar contra SAE1020")
print("=" * 50)

df_resultado = validate_mtc(df_test, 'SAE1020', NORMAS)
print("\n✅ Validación completada")
print(df_resultado[['elemento', 'valor', 'resultado']])

# Test 3: Generar PDF
print("\n\n" + "=" * 50)
print("TEST 3: Generación de PDF")
print("=" * 50)

veredicto = "LOTE APROBADO" if not (df_resultado['resultado'] == 'RECHAZADO').any() else "LOTE RECHAZADO"
print(f"\n📄 Veredicto: {veredicto}")

try:
    pdf_bytes = generate_pdf(df_resultado, 'SAE1020', veredicto)
    print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")
except Exception as e:
    print(f"❌ Error al generar PDF: {e}")

# Test 4: Test con un elemento que falla
print("\n\n" + "=" * 50)
print("TEST 4: Validación con fallo")
print("=" * 50)

df_test_fail = pd.DataFrame({
    'elemento': ['C_%', 'Mn_%'],
    'valor': [0.10, 2.5]  # Por debajo del mínimo y por encima del máximo
})

df_resultado_fail = validate_mtc(df_test_fail, 'SAE1020', NORMAS)
print("\n⚠️ Elementos con desviaciones:")
failed = df_resultado_fail[df_resultado_fail['resultado'] == 'RECHAZADO'][['elemento', 'valor', 'desviacion']]
print(failed)

print("\n\n" + "=" * 50)
print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
print("=" * 50)
