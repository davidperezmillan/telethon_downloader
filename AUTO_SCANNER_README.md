# 🤖 Auto Scanner - Monitoreo Automático en Tiempo Real

## 📋 Descripción

El **Auto Scanner** es una funcionalidad que permite al bot monitorear automáticamente grupos de Telegram en tiempo real y descargar archivos grandes tan pronto como se publiquen, sin necesidad de comandos manuales.

## 🚀 Diferencias con Group Scanner

| Característica | Group Scanner | Auto Scanner |
|---|---|---|
| **Activación** | Manual con comandos | Automático en tiempo real |
| **Funcionamiento** | Escanea historial | Monitorea mensajes nuevos |
| **Configuración** | Por comando | Por variables de entorno |
| **Uso típico** | Recuperar archivos antiguos | Descargar archivos nuevos |

## ⚙️ Configuración

### Variables de Entorno Principales

```yaml
environment:
  # Habilitar/deshabilitar el auto scanner
  - AUTO_SCAN_ENABLED=true                         # true/false
  
  # Lista de grupos a monitorear (separados por comas)
  - AUTO_SCAN_GROUPS=-1001234567890,-1001987654321
  
  # Tamaño mínimo de archivo para descarga automática (MB)
  - AUTO_SCAN_MIN_SIZE_MB=100
  
  # Notificar al usuario cuando se descarga automáticamente
  - AUTO_SCAN_NOTIFY_USER=true                     # true/false
  
  # Modo de lista: true=solo grupos listados, false=todos excepto listados
  - AUTO_SCAN_WHITELIST_ONLY=true                  # true/false
```

### Ejemplo de Configuración Completa

```yaml
services:
  telethon_downloader:
    image: jsavargas/telethon_downloader
    environment:
      # Configuración básica del bot
      - TG_AUTHORIZED_USER_ID=123456789
      - TG_API_ID=your_api_id
      - TG_API_HASH=your_api_hash
      - TG_BOT_TOKEN=your_bot_token
      
      # Auto Scanner habilitado
      - AUTO_SCAN_ENABLED=true
      - AUTO_SCAN_GROUPS=-1001234567890,-1001987654321,-1001567891234
      - AUTO_SCAN_MIN_SIZE_MB=150
      - AUTO_SCAN_NOTIFY_USER=true
      - AUTO_SCAN_WHITELIST_ONLY=true
```

## 📖 Cómo Funciona

### 1. Monitoreo Automático
- El bot escucha **todos los mensajes nuevos** en tiempo real
- Verifica si el mensaje proviene de un grupo monitoreado
- Analiza si contiene un archivo mayor al tamaño configurado
- Descarga automáticamente si cumple los criterios

### 2. Flujo de Procesamiento
```
Mensaje nuevo → ¿Es un grupo monitoreado? → ¿Archivo grande? → Descargar automáticamente
```

### 3. Organización Automática
- Los archivos se organizan usando las **mismas reglas** que el bot normal
- Respeta configuraciones de `config.ini`
- Aplica permisos de archivos y carpetas
- Descomprime automáticamente si está habilitado

## 🔧 Comandos de Gestión

### `/autostatus`
Muestra el estado actual del auto scanner:
```
🤖 Estado del Auto Scanner

✅ Estado: Habilitado
📊 Tamaño mínimo: 100 MB
🔔 Notificaciones: Habilitadas
📋 Modo lista: Solo grupos listados
🏷️ Total grupos configurados: 3

📝 Grupos configurados:
   • -1001234567890
   • -1001987654321
   • -1001567891234
```

### `/autoadd <group_id>`
Agrega un grupo al monitoreo en tiempo de ejecución:
```
/autoadd -1001234567890
✅ Grupo -1001234567890 agregado al monitoreo automático
```

### `/autoremove <group_id>`
Remueve un grupo del monitoreo en tiempo de ejecución:
```
/autoremove -1001234567890
✅ Grupo -1001234567890 removido del monitoreo automático
```

## 🎯 Modos de Operación

### Modo Whitelist (Recomendado)
```yaml
- AUTO_SCAN_WHITELIST_ONLY=true
- AUTO_SCAN_GROUPS=-1001234567890,-1001987654321
```
**Comportamiento:** Solo monitorea los grupos específicamente listados.

### Modo Blacklist
```yaml
- AUTO_SCAN_WHITELIST_ONLY=false
- AUTO_SCAN_GROUPS=-1001111111111,-1002222222222
```
**Comportamiento:** Monitorea todos los grupos EXCEPTO los listados.

## 📱 Notificaciones

Cuando el auto scanner descarga un archivo, envía una notificación como esta:

```
🤖 Descarga Automática Detectada

📁 Archivo: movie_2024.mkv
📊 Tamaño: 2.5 GB
🏷️ Grupo: Movies Channel
🔍 Motivo: Archivo grande detectado automáticamente

ℹ️ El archivo se descargará usando las reglas de organización configuradas
```

## 🔒 Consideraciones de Seguridad

### Permisos Necesarios
- El bot debe ser **miembro** de los grupos que quieres monitorear
- Debe tener permisos de **lectura de mensajes**
- No necesita ser administrador

### Autenticación
- Solo **usuarios autorizados** pueden usar comandos de gestión
- El monitoreo automático funciona independientemente de la autorización
- Solo se notifica a usuarios autorizados configurados

## 🛠️ Configuración Paso a Paso

### 1. Obtener IDs de Grupos
```bash
# Agrega el bot al grupo y envía:
/id
# Respuesta: id: -1001234567890
```

### 2. Configurar Variables de Entorno
```yaml
- AUTO_SCAN_ENABLED=true
- AUTO_SCAN_GROUPS=-1001234567890,-1001987654321
- AUTO_SCAN_MIN_SIZE_MB=100
```

### 3. Reiniciar el Bot
```bash
docker-compose down
docker-compose up -d
```

### 4. Verificar Estado
```bash
# Envía al bot:
/autostatus
```

### 5. Probar Funcionamiento
- Sube un archivo >100MB al grupo monitoreado
- El bot debería detectarlo y descargarlo automáticamente
- Recibirás una notificación

## 📊 Casos de Uso

### Caso 1: Canal de Contenido
```yaml
# Monitorear solo canales específicos de películas/series
- AUTO_SCAN_GROUPS=-1001234567890,-1001987654321
- AUTO_SCAN_MIN_SIZE_MB=500  # Solo archivos muy grandes
- AUTO_SCAN_WHITELIST_ONLY=true
```

### Caso 2: Backup Automático
```yaml
# Monitorear todos los grupos excepto spam
- AUTO_SCAN_GROUPS=-1001111111111,-1002222222222  # IDs de grupos spam
- AUTO_SCAN_MIN_SIZE_MB=50   # Archivos más pequeños también
- AUTO_SCAN_WHITELIST_ONLY=false  # Modo blacklist
```

### Caso 3: Monitoreo Selectivo
```yaml
# Solo documentos importantes
- AUTO_SCAN_GROUPS=-1001234567890  # Grupo de trabajo
- AUTO_SCAN_MIN_SIZE_MB=10         # Documentos pequeños también
- AUTO_SCAN_NOTIFY_USER=true       # Notificar siempre
```

## 🔧 Solución de Problemas

### ❌ "Auto scanner está deshabilitado"
- Verifica: `AUTO_SCAN_ENABLED=true`
- Reinicia el contenedor

### ❌ No se detectan archivos
- Verifica que el grupo esté en `AUTO_SCAN_GROUPS`
- Confirma que `AUTO_SCAN_WHITELIST_ONLY` esté configurado correctamente
- Revisa que el archivo sea mayor a `AUTO_SCAN_MIN_SIZE_MB`

### ❌ Bot no está en el grupo
- Agrega el bot al grupo como miembro
- Asegúrate de que puede leer mensajes

### ❌ Descargas no se organizan correctamente
- El auto scanner usa las mismas reglas que el bot normal
- Revisa tu `config.ini` y configuración de paths

## 🎨 Personalización Avanzada

### Ajustar Sensibilidad
```yaml
# Más sensible (archivos más pequeños)
- AUTO_SCAN_MIN_SIZE_MB=50

# Menos sensible (solo archivos muy grandes)
- AUTO_SCAN_MIN_SIZE_MB=500
```

### Controlar Notificaciones
```yaml
# Sin notificaciones (modo silencioso)
- AUTO_SCAN_NOTIFY_USER=false

# Con notificaciones (recomendado)
- AUTO_SCAN_NOTIFY_USER=true
```

## 🔄 Integración con Group Scanner

Ambas funcionalidades pueden usarse juntas:

- **Auto Scanner**: Para archivos nuevos en tiempo real
- **Group Scanner**: Para recuperar archivos históricos

```bash
# Recuperar historial
/scanlarge -1001234567890 30

# El auto scanner seguirá monitoreando archivos nuevos automáticamente
```

Esta combinación te da cobertura completa: archivos pasados y futuros.