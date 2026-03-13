# Flujo de Datos — Pipeline Completo

## Flujo Principal

```
Usuario sube .xlsx
    ↓
app.py lee norma seleccionada
    ↓
pd.read_excel()
    ↓
validator.py
    ↓
DataFrame + col PASS/FAIL
    ↓
st.dataframe() con colores
    ↓
report.py → PDF descargable
```

## Detalle de Cada Etapa

### 1. Carga del Archivo
- Usuario selecciona **norma** en dropdown
- Usuario carga archivo `.xlsx`
- **App.py** lee el Excel con `pd.read_excel()`

### 2. Validación
- **validator.py** recibe:
  - DataFrame (columnas: elemento, valor)
  - Clave de norma (SAE1020, SAE1045, etc.)
  - Diccionario de normas (desde normas.py)
- Valida cada elemento contra min/max tolerancias

### 3. Resultado Intermedio
- DataFrame enriquecido con:
  - Columna `resultado`: APROBADO / RECHAZADO
  - Columna `desviacion`: descripción del fallo (o vacío si pasó)

### 4. Visualización
- **st.dataframe()** con formato condicional
  - Verde para APROBADO
  - Rojo para RECHAZADO
- **Verdict banner** (LOTE APROBADO / RECHAZADO)
  - Lógica: `ANY(resultado == RECHAZADO) → LOTE RECHAZADO`

### 5. Exportación
- Botón "Descargar Dictamen"
- **report.py** genera PDF
- Usuario descarga bytes del PDF

## Transformación de Datos

| Etapa | Entrada | Salida |
|-------|---------|--------|
| Read | .xlsx | DataFrame (elemento, valor) |
| Validate | DataFrame + norma_key | DataFrame + resultado + desviacion |
| Display | DataFrame validado | HTML table (coloreado) |
| Export | DataFrame + verdict | PDF (bytes) |
