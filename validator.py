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
    if name is None or name == "":
        return ""
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


def detect_norma(df_clean: pd.DataFrame, normas_dict: dict) -> tuple:
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
            # Skip metadata keys like "label" and "descripcion"
            if not isinstance(limits, dict) or "min" not in limits or "max" not in limits:
                continue
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

        # Check if elemento is a valid spec (dict with "min" and "max"), not metadata
        is_valid_element = elemento in norma and isinstance(norma[elemento], dict) and "min" in norma[elemento] and "max" in norma[elemento]
        
        if not is_valid_element:
            # Get valid elements for error message
            valid_elements = [k for k, v in norma.items() if isinstance(v, dict) and "min" in v and "max" in v]
            df_resultado.loc[idx, "resultado"] = "NO EN NORMA"
            df_resultado.loc[idx, "desviacion"] = (
                f"'{elemento}' no existe en {norma_key}. "
                f"Elementos válidos: {', '.join(valid_elements)}"
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
