#!/usr/bin/env python3

import asyncio
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
from telethon.utils import get_peer_id
import logger


class AutoScanner:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.client = telegram_bot.client
        self.constants = telegram_bot.constants
        
        # Configuración del auto scanner
        self.enabled = self.constants.get_variable("AUTO_SCAN_ENABLED")
        self.monitored_groups = [int(gid) for gid in self.constants.get_variable("AUTO_SCAN_GROUPS") if gid.strip() and gid.strip() != ""]
        self.min_file_size = self.constants.get_variable("AUTO_SCAN_MIN_SIZE_MB") * 1024 * 1024  # MB a bytes
        self.notify_user = self.constants.get_variable("AUTO_SCAN_NOTIFY_USER")
        self.whitelist_only = self.constants.get_variable("AUTO_SCAN_WHITELIST_ONLY")
        
        logger.logger.info(f"AutoScanner initialized:")
        logger.logger.info(f"  - Enabled: {self.enabled}")
        logger.logger.info(f"  - Monitored groups: {self.monitored_groups}")
        logger.logger.info(f"  - Min file size: {self.constants.get_variable('AUTO_SCAN_MIN_SIZE_MB')}MB")
        logger.logger.info(f"  - Notify user: {self.notify_user}")
        logger.logger.info(f"  - Whitelist only: {self.whitelist_only}")
    
    def is_auto_scan_enabled(self):
        """Verifica si el auto scan está habilitado"""
        return self.enabled
    
    def is_group_monitored(self, group_id):
        """
        Verifica si un grupo está en la lista de monitoreo
        
        Args:
            group_id: ID del grupo a verificar
            
        Returns:
            bool: True si el grupo debe ser monitoreado
        """
        if not self.enabled:
            return False
            
        # Si whitelist_only está habilitado, solo monitorear grupos en la lista
        if self.whitelist_only:
            return group_id in self.monitored_groups
        
        # Si whitelist_only está deshabilitado, monitorear todos menos los que están en lista negra
        # (En este caso usamos la lista como blacklist)
        return group_id not in self.monitored_groups
    
    def is_large_file(self, message):
        """
        Verifica si un mensaje contiene un archivo grande
        
        Args:
            message: Mensaje de Telegram a verificar
            
        Returns:
            dict: Información del archivo si es grande, None si no
        """
        try:
            if not (message.media and isinstance(message.media, MessageMediaDocument)):
                return None
            
            document = message.media.document
            if not document:
                return None
            
            file_size = document.size
            
            # Verificar si el archivo es suficientemente grande
            if file_size < self.min_file_size:
                return None
            
            # Obtener nombre del archivo
            filename = "unknown_file"
            for attr in document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    filename = attr.file_name
                    break
            
            # Obtener información del grupo
            group_id = get_peer_id(message.peer_id)
            group_name = "Unknown Group"
            
            return {
                'filename': filename,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'group_id': group_id,
                'group_name': group_name,
                'message': message
            }
            
        except Exception as e:
            logger.logger.error(f"Error checking if file is large: {e}")
            return None
    
    async def should_auto_download(self, message):
        """
        Determina si un mensaje debe ser descargado automáticamente
        
        Args:
            message: Mensaje de Telegram
            
        Returns:
            dict: Información del archivo si debe descargarse, None si no
        """
        try:
            if not self.is_auto_scan_enabled():
                return None
            
            # Obtener ID del grupo/chat
            group_id = get_peer_id(message.peer_id)
            
            # Verificar si el grupo está siendo monitoreado
            if not self.is_group_monitored(group_id):
                logger.logger.debug(f"Group {group_id} not in monitoring list")
                return None
            
            # Verificar si es un archivo grande
            file_info = self.is_large_file(message)
            if not file_info:
                return None
            
            # Obtener nombre del grupo para logging
            try:
                entity = await self.client.get_entity(group_id)
                group_name = getattr(entity, 'title', f'Group_{group_id}')
                file_info['group_name'] = group_name
            except Exception as e:
                logger.logger.warning(f"Could not get group name for {group_id}: {e}")
            
            logger.logger.info(
                f"Auto-scan detected large file: {file_info['filename']} "
                f"({file_info['size_mb']} MB) in group {file_info['group_name']}"
            )
            
            return file_info
            
        except Exception as e:
            logger.logger.error(f"Error in should_auto_download: {e}")
            return None
    
    async def notify_auto_download(self, file_info):
        """
        Notifica al usuario sobre una descarga automática
        
        Args:
            file_info: Información del archivo que se está descargando
        """
        try:
            if not self.notify_user:
                return
            
            notification_message = (
                f"🤖 **Descarga Automática Detectada**\n\n"
                f"📁 **Archivo:** {file_info['filename']}\n"
                f"📊 **Tamaño:** {file_info['size_mb']} MB\n"
                f"🏷️ **Grupo:** {file_info['group_name']}\n"
                f"🔍 **Motivo:** Archivo grande detectado automáticamente\n\n"
                f"ℹ️ *El archivo se descargará usando las reglas de organización configuradas*"
            )
            
            await self.client.send_message(
                int(self.bot.TG_AUTHORIZED_USER_ID[0]),
                notification_message
            )
            
        except Exception as e:
            logger.logger.error(f"Error sending auto-download notification: {e}")
    
    async def process_auto_download(self, message):
        """
        Procesa la descarga automática de un archivo grande
        
        Args:
            message: Mensaje con el archivo a descargar
            
        Returns:
            bool: True si se procesó la descarga, False si no
        """
        try:
            # Verificar si debe descargarse automáticamente
            file_info = await self.should_auto_download(message)
            if not file_info:
                return False
            
            # Notificar al usuario si está habilitado
            await self.notify_auto_download(file_info)
            
            # Iniciar la descarga usando el sistema existente del bot
            logger.logger.info(f"Starting auto-download for: {file_info['filename']}")
            
            # Crear una tarea asíncrona para la descarga
            asyncio.create_task(
                self.bot.download_media_with_retries(message)
            )
            
            return True
            
        except Exception as e:
            logger.logger.error(f"Error in process_auto_download: {e}")
            return False
    
    def get_status_info(self):
        """
        Obtiene información del estado actual del auto scanner
        
        Returns:
            dict: Información del estado
        """
        return {
            'enabled': self.enabled,
            'monitored_groups': self.monitored_groups,
            'min_file_size_mb': self.constants.get_variable('AUTO_SCAN_MIN_SIZE_MB'),
            'notify_user': self.notify_user,
            'whitelist_only': self.whitelist_only,
            'total_monitored_groups': len(self.monitored_groups)
        }