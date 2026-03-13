# Lógica Clave — validator.py

## Especificación Funcional

### Entrada
- **df:** DataFrame con columnas `elemento` y `valor`
- **norma_key:** Clave de la norma (ej: "SAE1020")
- **normas_dict:** Diccionario de normas desde normas.py

**Formato esperado de df:**

| elemento | valor |
|----------|-------|
| C_% | 0.22 |
| Mn_% | 0.85 |
| YS_MPa | 350 |

### Proceso de Validación

**Para cada fila (elemento):**

```
1. Obtener valor reportado: df.loc[i, 'valor']
2. Buscar min/max en: normas_dict[norma_key][elemento]
3. Aplicar máscara booleana:
   - CUMPLE si: (valor >= min) AND (valor <= max)
   - FALLA si: valor < min OR valor > max
4. Registrar desviación:
   - Si CUMPLE: ''
   - Si FALLA: 'Por debajo del mínimo: X (mín: Y)' 
             o 'Por encima del máximo: X (máx: Y)'
```

### Salida
**DataFrame enriquecido con dos columnas nuevas:**

#### Columna `resultado`
- **Valor:** `"APROBADO"` o `"RECHAZADO"`
- **Lógica:** 
  - APROBADO si: (valor >= min) AND (valor <= max)
  - RECHAZADO si: valor < min OR valor > max

#### Columna `desviacion`
- **Tipo:** String
- **Valor si pasa:** `""`(vacío)
- **Valor si falla:** Mensaje descriptivo del fallo
  - Ejemplo: `"Por debajo del mínimo: 0.18 (mín: 0.20)"`
  - Ejemplo: `"Por encima del máximo: 2.5 (máx: 2.0)"`

**DataFrame resultante ejemplo:**

| elemento | valor | resultado | desviacion |
|----------|-------|-----------|-----------|
| C_% | 0.22 | APROBADO | |
| Mn_% | 3.0 | RECHAZADO | Por encima del máximo: 3.0 (máx: 2.0) |
| P_% | 0.015 | APROBADO | |

### Veredicto Final

```python
# En app.py o report.py:
if (df_resultado['resultado'] == 'RECHAZADO').any():
    veredicto = "LOTE RECHAZADO"
else:
    veredicto = "LOTE APROBADO"
```

## Reglas de Negocio

1. **Sin elementos faltantes:** Si el Excel no incluye un elemento requerido por la norma, lanzar error
2. **Tolerancias inclusivas:** min ≤ valor ≤ max (includes both boundaries)
3. **Atomic result:** Cada elemento es independiente; el fallo de uno no afecta a otros
4. **Lote atómico:** El lote completo es APROBADO solo si TODOS los elementos pasan

## Manejo de Errores

| Situación | Acción |
|-----------|--------|
| Elemento no existe en norma | Retornar error claro |
| Valor no es numérico | Retornar error claro |
| norma_key no existe | Retornar error claro |
| Todos los elementos pasan | resultado = APROBADO para todos |
| Un elemento falla | resultado = RECHAZADO para ese elemento + mensaje |
