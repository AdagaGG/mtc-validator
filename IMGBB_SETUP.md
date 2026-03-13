# Configuración de OCR Fallback con Mistral + imgbb

## Problema resuelto

El PDF del test es **escaneado** (imagen), no digital. Por lo tanto:
- ✅ `pdfplumber` no puede extraer datos (detectado correctamente)
- ✅ Fallback a **Mistral Pixtral 12b** para OCR
- ✅ La imagen se sube a **imgbb** para obtener URL pública (Mistral requiere esto)

## Instalación

Las dependencias ya están en `requirements.txt`:
- `pdfplumber` — PDFs digitales
- `requests` — API calls
- `PyMuPDF (fitz)` — Convertir PDF escaneado a imagen
- `Pillow` — Procesamiento de imagen

## Configuración de API Keys

### 1. Mistral API Key (ya tienes)
- ✅ Configurada en `.streamlit/secrets.toml`
- Ya funciona con `test_api_simple.py`

### 2. imgbb API Key (necesitas obtener)

**Pasos:**
1. Ve a https://api.imgbb.com/
2. Click en **Sign up** (free plan)
3. Verifica tu email
4. Copia tu **API Key** (en el dashboard)
5. Pégalo en `.streamlit/secrets.toml`:

```toml
MISTRAL_API_KEY = "kSh23thqlPbBtR1A0EKhm7qvmk8t32gr"
IMGBB_API_KEY = "your_api_key_aqui"
```

## Flujo actual

```
PDF escaneado
    ↓
pdfplumber (intento 1) → No extrae (es imagen)
    ↓
Mistral + imgbb (fallback):
    1. Convertir PDF → JPEG con PyMuPDF + PIL
    2. Subir imagen a imgbb → obtener URL pública
    3. Enviar URL a Mistral Pixtral 12b
    4. Mistral extrae datos en JSON
    5. Retornar DataFrame
```

## Test

Primero, actualiza tu API key de imgbb en este archivo:

```bash
# Edita test_mistral_imgbb.py y reemplaza:
api_key_imgbb = "your_api_key_aqui"

# Luego corre:
python test_mistral_imgbb.py
```

Si funciona, verás:
```
✓ Image uploaded: https://ibb.co/xxxxx
✓ Status: 200
5. Parsed JSON: 10 items
   - {'elemento': 'C_%', 'valor': 0.46}
   - {'elemento': 'Mn_%', 'valor': 0.78}
   ...
```

## Límites

- **imgbb gratis**: 30 subidas/hora, imágenes de máx 32 MB
- **Datos se borran**: Después de 600 segundos (10 min) si usas expiration
- **Mistral**: Soporta imágenes JPEG, PNG, WebP (hasta ~20 MB)

## Alternativas si imgbb falla

1. **Usar imgur**: https://imgur.com/api
2. **Usar AWS S3 presigned URLs**: Más profesional para producción
3. **Usar CloudFlare Images**: https://www.cloudflare.com/products/cloudflare-images/

## Próximos pasos

1. ✅ Implementar OCR dual (digital + escaneado)
2. ✅ Configurar fallback con Mistral + imgbb
3. ⏳ Pedir que el usuario configure IMGBB_API_KEY
4. ⏳ Testear con PDF real
5. ⏳ Subir cambios a GitHub
