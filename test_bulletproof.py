"""
Test para validar la refactorización bulletproof
"""
import pandas as pd
from validator import validate_mtc, clean_dataframe, detect_norma, normalize_element_name
from normas import NORMAS

print("=" * 60)
print("TEST BULLETPROOF — MTC Validator v0.2")
print("=" * 60)

# ── Test 1: Aliases ──────────────────────────────────────────────────────────
print("\n✓ TEST 1: Alias normalization")
test_aliases = [
    ("c", "C_%"),
    ("carbon", "C_%"),
    ("mn", "Mn_%"),
    ("carbono", "C_%"),
    ("ys", "YS_MPa"),
    ("yield", "YS_MPa"),
    ("uts", "UTS_MPa"),
    ("tensile", "UTS_MPa"),
    ("elong", "Elong_%"),
]

for input_name, expected in test_aliases:
    result = normalize_element_name(input_name)
    status = "✔" if result == expected else "✘"
    print(f"  {status} {input_name:12} → {result:12} (expected: {expected})")

# ── Test 2: Clean DataFrame ───────────────────────────────────────────────────
print("\n✓ TEST 2: DataFrame cleaning & alias mapping")
df_messy = pd.DataFrame({
    "ELEMENTO": ["Carbon", "mn", "Fósforo", "azufre", "YS"],
    "VALOR": [0.22, 0.85, 0.018, 0.022, 350],
})

try:
    df_clean = clean_dataframe(df_messy)
    print(f"  ✔ Cleaned {len(df_messy)} rows → {len(df_clean)} rows")
    print("  Elements mapped:")
    for elem in df_clean["elemento"]:
        print(f"    · {elem}")
except Exception as e:
    print(f"  ✘ Error: {e}")

# ── Test 3: Auto-detection norma ──────────────────────────────────────────────
print("\n✓ TEST 3: Auto-detection de norma")
df_test = pd.DataFrame({
    "elemento": ["C_%", "Mn_%", "P_%", "S_%", "YS_MPa", "UTS_MPa", "Elong_%"],
    "valor": [0.46, 0.75, 0.018, 0.022, 345, 620, 17.5],
})

detected, score = detect_norma(df_test, NORMAS)
print(f"  ✔ Detected: {detected} (confidence: {score}%)")

# ── Test 4: Validation con NO EN NORMA ────────────────────────────────────────
print("\n✓ TEST 4: Validation with unknown elements")
df_test_unknown = pd.DataFrame({
    "elemento": ["C_%", "UNKNOWN_ELEMENT", "YS_MPa"],
    "valor": [0.46, 999, 345],
})

result = validate_mtc(df_test_unknown, "SAE1045", NORMAS)
print(f"  Elements in result:")
for idx, row in result.iterrows():
    estado = row["resultado"]
    elemento = row["elemento"]
    print(f"    · {elemento:20} → {estado}")

# ── Test 5: Values without numbers ────────────────────────────────────────────
print("\n✓ TEST 5: Handling NaN values")
df_test_nan = pd.DataFrame({
    "elemento": ["C_%", "Mn_%", "P_%"],
    "valor": [0.46, None, 0.018],
})

result = validate_mtc(df_test_nan, "SAE1045", NORMAS)
print(f"  Elements with NaN:")
for idx, row in result.iterrows():
    estado = row["resultado"]
    elemento = row["elemento"]
    print(f"    · {elemento:20} → {estado}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED ✔")
print("=" * 60)
