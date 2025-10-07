#!/bin/bash

# Ejemplo de configuración y uso del Group Scanner
# Este script muestra cómo configurar y usar la nueva funcionalidad

echo "🔍 Group Scanner - Configuración y Ejemplos de Uso"
echo "================================================="

echo ""
echo "📋 1. Configuración en docker-compose.yml:"
echo "-------------------------------------------"
cat << 'EOF'
environment:
  # Configuración existente...
  - TG_AUTHORIZED_USER_ID=123456789
  - TG_API_ID=your_api_id
  - TG_API_HASH=your_api_hash
  - TG_BOT_TOKEN=your_bot_token
  
  # Nueva configuración para Group Scanner
  - SCAN_MIN_FILE_SIZE_MB=100        # Archivos de 100MB o más
  - SCAN_MAX_PARALLEL=2              # Máximo 2 descargas simultáneas
  - SCAN_DEFAULT_DAYS=30             # Buscar en los últimos 30 días por defecto
  - SCAN_MAX_DAYS=365                # Máximo 1 año hacia atrás
  - SCAN_DEFAULT_LIMIT=0             # Sin límite de mensajes por defecto
EOF

echo ""
echo "🚀 2. Comandos de ejemplo:"
echo "-------------------------"

echo ""
echo "📁 Obtener ID de grupo:"
echo "   1. Agrega el bot al grupo como administrador"
echo "   2. Envía: /id"
echo "   3. El bot responderá con algo como: id: -1001234567890"

echo ""
echo "🔍 Escanear y descargar (últimos 30 días):"
echo "   /scanlarge -1001234567890"

echo ""
echo "📝 Solo listar archivos (últimos 7 días):"
echo "   /scanlist -1001234567890 7"

echo ""
echo "⚡ Escaneo rápido (últimos 5 días, máximo 500 mensajes):"
echo "   /scanlarge -1001234567890 5 500"

echo ""
echo "🏛️ Escaneo histórico (últimos 90 días):"
echo "   /scanlarge -1001234567890 90"

echo ""
echo "📊 3. Flujo de trabajo recomendado:"
echo "----------------------------------"
echo "   1. Primero usa /scanlist para ver qué archivos hay:"
echo "      /scanlist -1001234567890 7"
echo ""
echo "   2. Si te gusta lo que ves, usa /scanlarge para descargar:"
echo "      /scanlarge -1001234567890 7"
echo ""
echo "   3. Para grupos muy activos, usa límites:"
echo "      /scanlarge -1001234567890 30 1000"

echo ""
echo "🎯 4. Casos de uso específicos:"
echo "------------------------------"

echo ""
echo "📚 Backup de canal educativo:"
echo "   /scanlarge -1001234567890 60  # Últimos 2 meses"

echo ""
echo "🎬 Descargar películas recientes:"
echo "   /scanlist -1001234567890 14   # Ver últimas 2 semanas"
echo "   /scanlarge -1001234567890 14  # Descargar si hay algo interesante"

echo ""
echo "🔄 Sincronización semanal:"
echo "   /scanlarge -1001234567890 7   # Solo lo de esta semana"

echo ""
echo "⚠️  5. Consideraciones importantes:"
echo "----------------------------------"
echo "   • El bot debe ser miembro del grupo con permisos de lectura"
echo "   • Los archivos se organizan según tu config.ini existente"
echo "   • Usa /scanlist primero en grupos grandes para estimar tiempo"
echo "   • Los archivos descargados siguen las mismas reglas de organización"

echo ""
echo "📈 6. Monitoreo del progreso:"
echo "----------------------------"
echo "   El bot enviará mensajes como:"
echo "   🔍 Iniciando escaneo..."
echo "   📊 Escaneados 100 mensajes..."
echo "   📁 Archivo encontrado: video.mkv (2.5 GB)"
echo "   ✅ Descarga completada: video.mkv"
echo "   📊 Resumen: 5 archivos encontrados, 4 descargados"

echo ""
echo "✅ ¡Listo! Ya puedes usar la funcionalidad Group Scanner"
echo "   Para más detalles, revisa GROUP_SCANNER_README.md"