# Estructura de Archivos del Proyecto

**Raíz:** `mtc-validator/`

## Archivos Principales

### `app.py` — CORE
- **Descripción:** Punto de entrada Streamlit
- **Responsabilidad:** UI, lógica de routing entre pantallas
- **Dependencias:** streamlit, pandas

### `normas.py` — DATA
- **Descripción:** Diccionario de tolerancias por norma
- **Contenido:** SAE 1020, SAE 1045, ASTM A36, AISI 4140
- **Rol:** La "base de datos" del MVP

### `validator.py` — CORE
- **Descripción:** Función pura de validación
- **Entrada:** DataFrame + norma
- **Salida:** DataFrame con columna "resultado" (PASS/FAIL)
- **Tipo:** Lógica sin efectos secundarios

### `report.py` — OUTPUT
- **Descripción:** Genera el PDF de dictamen
- **Librería:** fpdf2
- **Flujo:** DataFrame validado → bytes del PDF descargable

### `requirements.txt`
```
streamlit
pandas
openpyxl
fpdf2
```

### `.streamlit/config.toml`
- Tema oscuro tipo terminal
- Opcional pero profesional

## Estructura Esperada del Directorio

```
mtc-validator/
├── app.py
├── normas.py
├── validator.py
├── report.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```
