# Formato del Excel de Entrada

## Requisitos Estrictos

### Headers (Fila 1)
- **Columna A:** `elemento`
- **Columna B:** `valor`

⚠️ **Reglas:**
- Sin celdas combinadas
- Sin logos ni imágenes
- Exactamente como se especifica

### Columna A: Elemento
**Debe contener exactamente los nombres definidos en `normas.py`**

Ejemplos:
- `C_%`
- `Mn_%`
- `P_%`
- `S_%`
- `YS_MPa`
- `UTS_MPa`
- `Elong_%`

### Columna B: Valor
- **Tipo:** Número decimal
- **Formato:** Separador decimal según SO (. o ,)
- **Ejemplo:** `0.25`, `1050.5`, `18.5`

## Ejemplo de Excel Válido

| elemento | valor |
|----------|-------|
| C_% | 0.22 |
| Mn_% | 0.85 |
| P_% | 0.015 |
| S_% | 0.012 |
| YS_MPa | 350 |
| UTS_MPa | 520 |
| Elong_% | 18.5 |

## Validación en Carga

El app.py debe:
1. ✅ Validar que las columnas sean exactamente "elemento" y "valor"
2. ✅ Validar que los nombres de elementos existan en la norma seleccionada
3. ✅ Convertir "valor" a numérico (lanzar error si no es posible)
4. ❌ Rechazar si hay celdas combinadas o imágenes

## Consideraciones Técnicas

```python
# En app.py - validación recomendada:
required_columns = {"elemento", "valor"}
if not required_columns.issubset(df.columns):
    st.error("El Excel debe tener columnas 'elemento' y 'valor'")

# Convertir a numérico
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
if df['valor'].isna().any():
    st.error("Algunos valores no son numéricos")
```
