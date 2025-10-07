# 🔍 Group Scanner - Funcionalidad de Escaneo de Archivos Grandes

## 📋 Descripción

La nueva funcionalidad **Group Scanner** permite al bot de Telethon Downloader escanear grupos de Telegram en busca de archivos grandes (por defecto >100MB) y descargarlos automáticamente usando el mismo sistema de organización existente.

## 🚀 Características

- **Escaneo histórico**: Busca archivos grandes en el historial de mensajes de un grupo
- **Configurable**: Tamaño mínimo de archivo, días hacia atrás y límites personalizables
- **Dos modos**: Solo listar archivos o descargar automáticamente
- **Progreso en tiempo real**: Notificaciones del progreso del escaneo y descarga
- **Organización automática**: Los archivos se organizan usando las mismas reglas existentes del bot
- **Control de concurrencia**: Límite de descargas paralelas para evitar sobrecarga

## 🔧 Comandos Disponibles

### `/scanlarge <group_id> [days] [limit]`
Escanea un grupo y **descarga automáticamente** los archivos grandes encontrados.

**Parámetros:**
- `group_id` (requerido): ID del grupo de Telegram (formato: -1001234567890)
- `days` (opcional): Días hacia atrás para buscar (default: 30)
- `limit` (opcional): Máximo de mensajes a revisar (default: sin límite)

**Ejemplos:**
```
/scanlarge -1001234567890
/scanlarge -1001234567890 7
/scanlarge -1001234567890 30 1000
```

### `/scanlist <group_id> [days] [limit]`
Escanea un grupo y **solo lista** los archivos grandes sin descargarlos.

**Parámetros:** (Iguales que `/scanlarge`)

**Ejemplos:**
```
/scanlist -1001234567890
/scanlist -1001234567890 15 500
```

## ⚙️ Variables de Entorno

Agrega estas variables a tu `docker-compose.yml` para personalizar el comportamiento:

```yaml
environment:
  # Group Scanner Settings
  - SCAN_MIN_FILE_SIZE_MB=100      # Tamaño mínimo en MB (default: 100)
  - SCAN_MAX_PARALLEL=2            # Descargas paralelas máximas (default: 2)
  - SCAN_DEFAULT_DAYS=30           # Días por defecto hacia atrás (default: 30)
  - SCAN_MAX_DAYS=365              # Máximo de días permitidos (default: 365)
  - SCAN_DEFAULT_LIMIT=0           # Límite por defecto de mensajes (0 = sin límite)
```

## 📖 Cómo Usar

### 1. Obtener el ID del Grupo

Para obtener el ID de un grupo:
1. Agrega el bot al grupo como administrador
2. Envía `/id` en el grupo
3. El bot responderá con el ID del grupo (formato: -1001234567890)

### 2. Ejecutar el Escaneo

#### Modo Descarga (Recomendado)
```
/scanlarge -1001234567890 30
```
Esto escaneará los últimos 30 días del grupo y descargará automáticamente todos los archivos mayores a 100MB.

#### Modo Solo Lista (Para revisar primero)
```
/scanlist -1001234567890 7
```
Esto solo listará los archivos grandes de los últimos 7 días sin descargarlos.

### 3. Monitorear el Progreso

El bot enviará mensajes de estado durante el proceso:
- ✅ Confirmación del inicio del escaneo
- 🔄 Actualizaciones de progreso cada 100 mensajes revisados
- 📁 Notificación por cada archivo encontrado/descargado
- 📊 Resumen final con estadísticas

## 🎯 Casos de Uso

### Escenario 1: Backup de Grupo Activo
```
/scanlarge -1001234567890 7 500
```
Descarga archivos grandes de la última semana, limitando a 500 mensajes.

### Escenario 2: Recuperación Histórica
```
/scanlarge -1001234567890 90
```
Descarga todos los archivos grandes de los últimos 3 meses.

### Escenario 3: Análisis sin Descarga
```
/scanlist -1001234567890 30
```
Solo revisa qué archivos grandes hay disponibles antes de decidir descargar.

## 🔒 Consideraciones de Seguridad

- Solo usuarios autorizados pueden ejecutar estos comandos
- El bot debe tener permisos de lectura en el grupo objetivo
- Los archivos se descargan usando las mismas reglas de organización configuradas
- Respeta los límites de rate limiting de Telegram

## 🛠️ Solución de Problemas

### Error: "No se puede acceder al grupo"
- Verifica que el bot sea miembro del grupo
- Asegúrate de que el ID del grupo sea correcto
- El grupo debe permitir que los bots lean el historial

### Error: "Group ID debe ser un número válido"
- Los IDs de grupo siempre empiezan con `-100`
- Formato correcto: `-1001234567890`
- Usa `/id` en el grupo para obtener el ID correcto

### Descargas lentas o interrumpidas
- Ajusta `SCAN_MAX_PARALLEL` a un valor menor (ej: 1)
- Reduce el límite de mensajes por lote
- Verifica tu conexión a internet

## 📈 Estadísticas de Rendimiento

El bot proporciona estadísticas detalladas:
- Total de mensajes escaneados
- Archivos grandes encontrados
- Descargas exitosas vs fallidas
- Tiempo total de procesamiento

## 🔄 Integración con Funcionalidades Existentes

Los archivos descargados por el Group Scanner:
- Se organizan según las reglas configuradas en `config.ini`
- Respetan las configuraciones de permisos de archivos/carpetas
- Se descomprimen automáticamente si está habilitado
- Siguen las mismas rutas por extensión o regex configuradas
- Se procesan con el mismo sistema de logs

Esta funcionalidad extiende las capacidades del bot sin afectar el funcionamiento normal de descarga de archivos enviados directamente.