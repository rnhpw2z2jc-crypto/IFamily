# 🏥 App Familiar: Citas Médicas + Servicios

Aplicación web en **Python + Streamlit + Firebase Realtime Database** para que tú y tus hermanos:

- Registren y vean juntos las citas médicas de papá y mamá.
- Cuando una cita ya pasó, la marcan como "realizada" y queda guardada en un **historial clínico**: diagnóstico, tratamiento, recomendaciones y próxima cita sugerida. Así, antes de la siguiente consulta, cualquiera puede repasar qué pasó la última vez.
- Guarden en un solo lugar los códigos de pago de luz, agua, gas, internet, etc.

Todos los hermanos ven los mismos datos en tiempo real porque todo se guarda en Firebase, no en el navegador de cada uno.

## 🚀 Cómo desplegarla gratis (Streamlit Community Cloud)

### 1. Crear la base de datos en Firebase
1. Entra a [Firebase Console](https://console.firebase.google.com/) y crea un proyecto (gratis).
2. En el menú lateral, ve a **Realtime Database** → **Crear base de datos** → modo de prueba.
3. Copia la URL de la base de datos (algo como `https://tu-proyecto-default-rtdb.firebaseio.com/`).
4. Ve a **⚙️ Configuración del proyecto → Cuentas de servicio → Generar nueva clave privada**. Se descarga un archivo `.json`. Guárdalo, es la llave de acceso — no la compartas fuera de la familia.

### 2. Subir el código a GitHub
1. Crea un repositorio **privado** en GitHub (para que no cualquiera vea el código).
2. Sube los archivos: `app.py`, `requirements.txt`, `README.md` y la carpeta `.streamlit/`.
   - No subas tu `firebase_key.json` real ni el `secrets.toml` con datos reales — esos se cargan aparte, como secretos.

### 3. Desplegar en Streamlit Cloud
1. Entra a [share.streamlit.io](https://share.streamlit.io/) con tu cuenta de GitHub.
2. Elige "New app", selecciona tu repositorio y el archivo `app.py`.
3. Antes de desplegar, ve a **Advanced settings → Secrets** y pega:

```toml
FIREBASE_DB_URL = "https://tu-proyecto-default-rtdb.firebaseio.com/"
FIREBASE_KEY = 'PEGA_AQUI_TODO_EL_CONTENIDO_DEL_JSON_EN_UNA_SOLA_LINEA'
```

   Para obtener el JSON en una sola línea, puedes abrir el archivo descargado y copiar todo su contenido tal cual (Streamlit acepta el JSON como texto entre comillas simples).

4. Dale a **Deploy**. En un par de minutos tendrás un link que puedes compartir con tus hermanos (por WhatsApp, por ejemplo).

### 4. Probarla en tu computadora antes de subirla (opcional)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Para esto, coloca el archivo `firebase_key.json` descargado de Firebase en la misma carpeta que `app.py` (la app lo detecta automáticamente si no encuentra los secretos de Streamlit Cloud).

## 👨‍👩‍👧‍👦 Cómo la usan tus hermanos
- No hay usuarios ni contraseñas: apenas entran, escriben su nombre en la barra lateral. Eso solo sirve para saber quién registró cada cita o servicio, no restringe el acceso.
- Comparte el link de la app y listo, todos ven y editan la misma información en tiempo real.

## 🧠 Cómo funciona el historial clínico
1. Se agenda una cita en "🗓️ Próximas citas".
2. Después de que ocurre, cualquier hermano la abre y presiona **"✅ Marcar como realizada"**, llenando diagnóstico, tratamiento, recomendaciones y (si el doctor lo dijo) la fecha sugerida para la próxima cita.
3. Esa cita pasa automáticamente a la pestaña **"📖 Historial clínico"**, donde se puede filtrar por Papá o Mamá y repasar todo el historial antes de la siguiente visita al médico.

## 🔒 Nota de privacidad
Esta app guarda información médica y códigos de servicios de tus padres. Aunque es de uso familiar, se recomienda:
- Mantener el repositorio de GitHub **privado**.
- No compartir el link de la app fuera del grupo familiar.
- Revisar de vez en cuando las reglas de seguridad de Firebase Realtime Database (por defecto, el "modo de prueba" es abierto y conviene restringirlo más adelante si quieren mayor seguridad).