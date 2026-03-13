"""
Función de validación de elementos metalúrgicos contra normas ASTM/SAE
"""

import pandas as pd


def validate_mtc(df, norma_key, normas_dict):
    """
    Valida elementos contra norma especificada.
    
    Recibe un DataFrame con columnas 'elemento' y 'valor', verifica cada valor 
    contra los rangos min/max en la norma seleccionada, y retorna el DataFrame 
    enriquecido con columnas 'resultado' (APROBADO/RECHAZADO) y 'desviacion' 
    (descripción del fallo o vacío).
    
    Args:
        df: DataFrame con columnas 'elemento' y 'valor'
        norma_key: str - clave de la norma (SAE1020, SAE1045, ASTM_A36, AISI4140)
        normas_dict: dict - diccionario de normas (desde normas.py)
    
    Returns:
        DataFrame original + columnas 'resultado' y 'desviacion'
    
    Raises:
        ValueError: Si la norma no existe o un elemento no está en la norma
        TypeError: Si los valores no son numéricos
    """
    
    # Validar que la norma existe
    if norma_key not in normas_dict:
        raise ValueError(f"Norma '{norma_key}' no existe. Disponibles: {list(normas_dict.keys())}")
    
    norma = normas_dict[norma_key]
    
    # Crear copia para no modificar el original
    df_resultado = df.copy()
    
    # Inicializar columnas
    df_resultado['resultado'] = ''
    df_resultado['desviacion'] = ''
    
    # Procesar cada fila
    for idx, row in df_resultado.iterrows():
        elemento = str(row['elemento']).strip()
        valor = row['valor']
        
        # Validar que el elemento existe en la norma
        if elemento not in norma:
            raise ValueError(f"Elemento '{elemento}' no existe en norma '{norma_key}'")
        
        # Convertir valor a numérico
        try:
            valor_num = float(valor)
        except (ValueError, TypeError):
            raise TypeError(f"El valor '{valor}' para elemento '{elemento}' no es numérico")
        
        # Obtener tolerancias
        min_val = norma[elemento]['min']
        max_val = norma[elemento]['max']
        
        # Validar
        if min_val <= valor_num <= max_val:
            df_resultado.loc[idx, 'resultado'] = 'APROBADO'
            df_resultado.loc[idx, 'desviacion'] = ''
        else:
            df_resultado.loc[idx, 'resultado'] = 'RECHAZADO'
            
            # Generar mensaje de desviación
            if valor_num < min_val:
                desviacion = f"Por debajo del mínimo: {valor_num} (mín: {min_val})"
            else:
                desviacion = f"Por encima del máximo: {valor_num} (máx: {max_val})"
            
            df_resultado.loc[idx, 'desviacion'] = desviacion
    
    return df_resultado
