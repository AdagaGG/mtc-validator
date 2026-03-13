# Setup Streamlit Cloud Secrets

## Para Streamlit Cloud Deployment

Cuando desployes tu app en Streamlit Cloud, necesitas configurar las credenciales a través de Streamlit Secrets Manager.

### Pasos:

1. **Abre tu app en Streamlit Cloud**
   - Ve a https://share.streamlit.io/
   - Localiza tu app "mtc-validator"

2. **Accede a Settings**
   - Click en los 3 puntos (⋮) → Settings
   - O ve a la URL: `https://share.streamlit.io/[tu-usuario]/mtc-validator/main`

3. **Agrega Secrets**
   - Click en "Secrets" en la barra lateral izquierda
   - Agrega el siguiente contenido en formato TOML:

```toml
[credentials]
[credentials.usernames]

[credentials.usernames.piloto_empresa1]
email = "contacto@empresa1.com"
first_name = "Piloto"
last_name = "Empresa1"
password = "piloto2024"

[credentials.usernames.admin]
email = "hola@adaga.tech"
first_name = "Adrian"
last_name = "Admin"
password = "admin2024"

[credentials.usernames.tester]
email = "test@mtcvalidator.com"
first_name = "Test"
last_name = "User"
password = "test2024"

[cookie]
expiry_days = 30
key = "mtc_validator_secret_key_2024"
name = "mtc_validator_auth"

[[pre-authorized]]
```

4. **Guarda y redeploy**
   - Click en "Save"
   - Streamlit Cloud automáticamente reiniciará tu app
   - Ahora debería funcionar sin errores de config.yaml

### Para Desarrollo Local

Para desarrollo local, copia `config.yaml.example` a `config.yaml`:

```bash
cp config.yaml.example config.yaml
```

Luego editalo con tus credenciales de desarrollo.

**IMPORTANTE:** Nunca commits `config.yaml` con credenciales reales a Git.

## Seguridad

- ✅ `config.yaml` está en `.gitignore` (no se sube a GitHub)
- ✅ Streamlit Cloud Secrets están encriptadas
- ✅ El código soporta ambos métodos automáticamente
