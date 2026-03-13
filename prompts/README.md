# Documentación del Proyecto MTC Validator

## 📋 Archivos de esta Carpeta

Esta carpeta `prompts/` contiene toda la documentación para construir el **MTC Validator** — una aplicación Streamlit para validar especificaciones metalúrgicas.

### Documentos

| Archivo | Descripción |
|---------|-------------|
| [**PROMPTS.md**](PROMPTS.md) | ✅ **COMIENZA AQUÍ** — Prompts exactos para copiar/pegar en Copilot |
| [**ESTRUCTURA.md**](ESTRUCTURA.md) | Estructura de archivos y organización del proyecto |
| [**FLUJO_DATOS.md**](FLUJO_DATOS.md) | Pipeline completo: entrada → validación → salida |
| [**EXCEL_FORMAT.md**](EXCEL_FORMAT.md) | Formato exacto del Excel que carga el usuario |
| [**VALIDATOR_LOGIC.md**](VALIDATOR_LOGIC.md) | Lógica detallada de las validaciones |

---

## 🚀 Guía Rápida de Inicio

### Paso 1: Crear Archivos Base
Crea estos archivos en carpeta raíz (`mtc-validator/`):
```
app.py
normas.py
validator.py
report.py
requirements.txt
.streamlit/config.toml (opcional)
```

### Paso 2: Generar Código con Copilot
1. Abre [**PROMPTS.md**](PROMPTS.md)
2. Copia el primer prompt (`normas.py`)
3. Presiona **Ctrl+I** en VS Code
4. Pega el prompt
5. Deja que Copilot genere el código
6. Repite para cada archivo (en orden recomendado)

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar
```bash
streamlit run app.py
```

---

## 📦 Stack Tecnológico

- **Streamlit** — UI interactiva
- **Pandas** — procesamiento de datos
- **openpyxl** — lectura de Excel
- **fpdf2** — generación de PDF

---

## 🔄 Flujo de Datos (Resumen)

```
.xlsx (usuario) 
  ↓
app.py (lee)
  ↓
validator.py (validación)
  ↓
DataFrame + resultado/desviacion
  ↓
UI coloreada (Streamlit)
  ↓
report.py (PDF)
  ↓
Descarga PDF
```

Para detalles completos, ver [**FLUJO_DATOS.md**](FLUJO_DATOS.md).

---

## 📝 Formato de Entrada

El usuario carga un `.xlsx` con:
- **Columna A:** nombre del elemento (C_%, Mn_%, P_%, S_%, YS_MPa, UTS_MPa, Elong_%)
- **Columna B:** valor numérico

Ejemplo:
| elemento | valor |
|----------|-------|
| C_% | 0.22 |
| Mn_% | 0.85 |

Ver [**EXCEL_FORMAT.md**](EXCEL_FORMAT.md) para detalles.

---

## ✅ Normas Soportadas

- SAE 1020
- SAE 1045
- ASTM A36
- AISI 4140

Definidas en `normas.py` con tolerancias min/max por elemento.

---

## 🎯 Resultado

- ✅ **LOTE APROBADO** — todos los elementos cumplen tolerancias
- ❌ **LOTE RECHAZADO** — al menos un elemento falla
- PDF descargable con dictamen y detalles

---

## 📖 Documentación Detallada

- **Lógica de validaciones:** [VALIDATOR_LOGIC.md](VALIDATOR_LOGIC.md)
- **Pipeline completo:** [FLUJO_DATOS.md](FLUJO_DATOS.md)
- **Estructura del proyecto:** [ESTRUCTURA.md](ESTRUCTURA.md)

---

## 🆘 ¿Necesitas Ayuda?

Cada documento es independiente:
1. Busca el tema que necesitas
2. Lee la sección correspondiente
3. Si necesitas el prompt exacto para Copilot, ve a [PROMPTS.md](PROMPTS.md)

---

**Generado:** Marcos para construir un validador MTC profesional con Copilot en menos de 1 hora.
