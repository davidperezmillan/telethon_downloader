#!/bin/bash

# Auto Scanner - Configuración Rápida
# Este script ayuda a configurar el Auto Scanner paso a paso

echo "🤖 Auto Scanner - Configuración Rápida"
echo "======================================"

echo ""
echo "📋 ¿Qué es el Auto Scanner?"
echo "El Auto Scanner monitorea grupos de Telegram en tiempo real y descarga"
echo "automáticamente archivos grandes tan pronto como se publiquen."
echo ""

echo "🔧 Configuración en docker-compose.yml:"
echo "---------------------------------------"
echo ""
echo "Agrega estas variables a tu docker-compose.yml:"
echo ""

cat << 'EOF'
environment:
  # Configuración básica (ya existente)
  - TG_AUTHORIZED_USER_ID=tu_user_id
  - TG_API_ID=tu_api_id
  - TG_API_HASH=tu_api_hash
  - TG_BOT_TOKEN=tu_bot_token
  
  # AUTO SCANNER - Monitoreo automático
  - AUTO_SCAN_ENABLED=true                         # Habilitar auto scanner
  - AUTO_SCAN_GROUPS=-1001234567890,-1001987654321 # IDs de grupos a monitorear
  - AUTO_SCAN_MIN_SIZE_MB=100                      # Tamaño mínimo (MB)
  - AUTO_SCAN_NOTIFY_USER=true                     # Notificar descargas
  - AUTO_SCAN_WHITELIST_ONLY=true                  # Solo grupos listados
EOF

echo ""
echo ""
echo "📋 Pasos para configurar:"
echo "------------------------"

echo ""
echo "1️⃣  Obtener IDs de grupos:"
echo "   a) Agrega el bot al grupo como miembro"
echo "   b) Envía el comando: /id"
echo "   c) El bot responderá con: id: -1001234567890"
echo "   d) Repite para cada grupo que quieras monitorear"

echo ""
echo "2️⃣  Configurar docker-compose.yml:"
echo "   a) Edita tu archivo docker-compose.yml"
echo "   b) Agrega las variables mostradas arriba"
echo "   c) Reemplaza los IDs de ejemplo con los reales"

echo ""
echo "3️⃣  Reiniciar el bot:"
echo "   docker-compose down"
echo "   docker-compose up -d"

echo ""
echo "4️⃣  Verificar configuración:"
echo "   Envía al bot: /autostatus"

echo ""
echo "🎯 Ejemplos de configuración:"
echo "----------------------------"

echo ""
echo "📺 Para canales de películas/series:"
cat << 'EOF'
- AUTO_SCAN_ENABLED=true
- AUTO_SCAN_GROUPS=-1001234567890,-1001987654321
- AUTO_SCAN_MIN_SIZE_MB=500    # Solo archivos muy grandes
- AUTO_SCAN_NOTIFY_USER=true
- AUTO_SCAN_WHITELIST_ONLY=true
EOF

echo ""
echo "📚 Para grupos de documentos:"
cat << 'EOF'
- AUTO_SCAN_ENABLED=true
- AUTO_SCAN_GROUPS=-1001234567890
- AUTO_SCAN_MIN_SIZE_MB=50     # Documentos más pequeños también
- AUTO_SCAN_NOTIFY_USER=true
- AUTO_SCAN_WHITELIST_ONLY=true
EOF

echo ""
echo "🏢 Para backup general (todos los grupos):"
cat << 'EOF'
- AUTO_SCAN_ENABLED=true
- AUTO_SCAN_GROUPS=-1001111111111  # Grupos a EXCLUIR (spam, etc)
- AUTO_SCAN_MIN_SIZE_MB=100
- AUTO_SCAN_NOTIFY_USER=false      # Sin notificaciones para evitar spam
- AUTO_SCAN_WHITELIST_ONLY=false   # Modo blacklist: todos excepto listados
EOF

echo ""
echo "🔍 Comandos útiles:"
echo "------------------"
echo "/autostatus          - Ver estado actual"
echo "/autoadd -1001234567890    - Agregar grupo temporalmente"
echo "/autoremove -1001234567890 - Remover grupo temporalmente"
echo "/help                - Ver todos los comandos"

echo ""
echo "💡 Consejos:"
echo "------------"
echo "• Usa /autostatus para verificar que todo esté configurado"
echo "• Los cambios con /autoadd y /autoremove son temporales"
echo "• Para cambios permanentes, modifica docker-compose.yml"
echo "• El bot debe ser miembro de los grupos que quieres monitorear"
echo "• Los archivos se organizan igual que las descargas normales"

echo ""
echo "🔄 Flujo típico:"
echo "---------------"
echo "1. Alguien sube un archivo grande al grupo"
echo "2. Auto scanner lo detecta automáticamente"
echo "3. Descarga el archivo usando las reglas configuradas"
echo "4. Te notifica de la descarga (si está habilitado)"
echo "5. El archivo queda organizado en tu sistema"

echo ""
echo "✅ ¡Listo! Con esta configuración tendrás descarga automática"
echo "   de archivos grandes en tiempo real."

echo ""
echo "📖 Para más detalles, revisa AUTO_SCANNER_README.md"