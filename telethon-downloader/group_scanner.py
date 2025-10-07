#!/usr/bin/env python3

import asyncio
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
from telethon.utils import get_peer_id
from datetime import datetime, timedelta
import logger


class GroupScanner:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.client = telegram_bot.client
        self.constants = telegram_bot.constants
        
        # Configuración desde variables de entorno
        self.MIN_FILE_SIZE = self.constants.get_variable("SCAN_MIN_FILE_SIZE_MB") * 1024 * 1024  # MB a bytes
        self.semaphore = asyncio.Semaphore(self.constants.get_variable("SCAN_MAX_PARALLEL"))
        self.DEFAULT_DAYS = self.constants.get_variable("SCAN_DEFAULT_DAYS")
        self.MAX_DAYS = self.constants.get_variable("SCAN_MAX_DAYS")
        self.DEFAULT_LIMIT = self.constants.get_variable("SCAN_DEFAULT_LIMIT")
        
    async def scan_group_for_large_files(self, group_id, days_back=30, limit=None):
        """
        Escanea un grupo en busca de archivos grandes
        
        Args:
            group_id: ID del grupo a escanear
            days_back: Días hacia atrás para buscar (default: 30)
            limit: Límite de mensajes a revisar (None = sin límite)
        """
        try:
            logger.logger.info(f"Iniciando escaneo de archivos grandes (>{self.constants.get_variable('SCAN_MIN_FILE_SIZE_MB')}MB) en grupo: {group_id}")
            
            # Obtener información del grupo
            try:
                entity = await self.client.get_entity(group_id)
                group_name = getattr(entity, 'title', f'Grupo_{group_id}')
                logger.logger.info(f"Escaneando grupo: {group_name}")
            except Exception as e:
                logger.logger.error(f"Error obteniendo entidad del grupo {group_id}: {e}")
                return []
            
            # Calcular fecha límite
            date_limit = datetime.now() - timedelta(days=days_back)
            
            large_files = []
            scanned_count = 0
            
            # Escanear mensajes del grupo
            async for message in self.client.iter_messages(
                entity, 
                limit=limit,
                offset_date=date_limit
            ):
                scanned_count += 1
                
                if scanned_count % 100 == 0:
                    logger.logger.info(f"Escaneados {scanned_count} mensajes...")
                
                # Verificar si el mensaje tiene un documento
                if (message.media and 
                    isinstance(message.media, MessageMediaDocument) and 
                    message.media.document):
                    
                    document = message.media.document
                    file_size = document.size
                    
                    # Verificar si el archivo es mayor a 100MB
                    if file_size >= self.MIN_FILE_SIZE:
                        # Obtener nombre del archivo
                        filename = "unknown_file"
                        for attr in document.attributes:
                            if isinstance(attr, DocumentAttributeFilename):
                                filename = attr.file_name
                                break
                        
                        file_info = {
                            'message_id': message.id,
                            'filename': filename,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'date': message.date,
                            'group_id': group_id,
                            'group_name': group_name,
                            'message': message
                        }
                        
                        large_files.append(file_info)
                        logger.logger.info(
                            f"Archivo grande encontrado: {filename} ({file_info['size_mb']} MB)"
                        )
            
            logger.logger.info(
                f"Escaneo completado. Encontrados {len(large_files)} archivos grandes "
                f"de {scanned_count} mensajes revisados"
            )
            
            return large_files
            
        except Exception as e:
            logger.logger.error(f"Error escaneando grupo {group_id}: {e}")
            return []
    
    async def download_large_files_from_scan(self, large_files, auto_download=True):
        """
        Descarga los archivos grandes encontrados en el escaneo
        
        Args:
            large_files: Lista de archivos encontrados por scan_group_for_large_files
            auto_download: Si True, descarga automáticamente. Si False, solo lista
        """
        try:
            if not large_files:
                logger.logger.info("No hay archivos grandes para descargar")
                return
            
            logger.logger.info(f"Procesando {len(large_files)} archivos grandes...")
            
            downloaded_count = 0
            failed_count = 0
            
            for file_info in large_files:
                try:
                    if auto_download:
                        # Usar el semáforo para limitar descargas concurrentes
                        async with self.semaphore:
                            logger.logger.info(
                                f"Descargando: {file_info['filename']} "
                                f"({file_info['size_mb']} MB)"
                            )
                            
                            # Crear un mensaje de respuesta ficticio para el progreso
                            progress_message = await self.client.send_message(
                                int(self.bot.TG_AUTHORIZED_USER_ID[0]),
                                f"🔄 Descargando archivo grande del grupo:\n"
                                f"📁 {file_info['filename']}\n"
                                f"📊 {file_info['size_mb']} MB\n"
                                f"🏷️ Grupo: {file_info['group_name']}"
                            )
                            
                            # Usar el método de descarga existente del bot
                            download_result = await self.bot.download_media_with_retries(
                                file_info['message'], 
                                message=progress_message
                            )
                            
                            if download_result and not download_result.get('exception'):
                                downloaded_count += 1
                                await progress_message.edit(
                                    f"✅ Descarga completada:\n"
                                    f"📁 {file_info['filename']}\n"
                                    f"📊 {file_info['size_mb']} MB\n"
                                    f"🏷️ Grupo: {file_info['group_name']}"
                                )
                            else:
                                failed_count += 1
                                await progress_message.edit(
                                    f"❌ Error en descarga:\n"
                                    f"📁 {file_info['filename']}\n"
                                    f"📊 {file_info['size_mb']} MB\n"
                                    f"🏷️ Grupo: {file_info['group_name']}"
                                )
                                
                    else:
                        # Solo listar archivo sin descargar
                        logger.logger.info(
                            f"Archivo encontrado: {file_info['filename']} "
                            f"({file_info['size_mb']} MB) - "
                            f"Grupo: {file_info['group_name']}"
                        )
                        
                except Exception as e:
                    failed_count += 1
                    logger.logger.error(
                        f"Error procesando archivo {file_info['filename']}: {e}"
                    )
            
            summary_message = (
                f"📊 Resumen del escaneo de archivos grandes:\n"
                f"🔍 Total encontrados: {len(large_files)}\n"
            )
            
            if auto_download:
                summary_message += (
                    f"✅ Descargados exitosamente: {downloaded_count}\n"
                    f"❌ Fallos en descarga: {failed_count}"
                )
            else:
                summary_message += "ℹ️ Modo solo listado (sin descargas)"
            
            # Enviar resumen al usuario autorizado
            await self.client.send_message(
                int(self.bot.TG_AUTHORIZED_USER_ID[0]),
                summary_message
            )
            
            logger.logger.info(summary_message.replace('📊', '').replace('🔍', '').replace('✅', '').replace('❌', '').replace('ℹ️', ''))
            
        except Exception as e:
            logger.logger.error(f"Error en download_large_files_from_scan: {e}")
    
    async def scan_and_download_group(self, group_id, days_back=30, limit=None, auto_download=True):
        """
        Función combinada que escanea y descarga archivos grandes de un grupo
        
        Args:
            group_id: ID del grupo
            days_back: Días hacia atrás para buscar
            limit: Límite de mensajes a revisar
            auto_download: Si descargar automáticamente o solo listar
        """
        try:
            # Notificar inicio del proceso
            await self.client.send_message(
                int(self.bot.TG_AUTHORIZED_USER_ID[0]),
                f"🔍 Iniciando escaneo de archivos grandes (>{self.constants.get_variable('SCAN_MIN_FILE_SIZE_MB')}MB)\n"
                f"🏷️ Grupo ID: {group_id}\n"
                f"📅 Últimos {days_back} días\n"
                f"🔄 Modo: {'Descargar' if auto_download else 'Solo listar'}"
            )
            
            # Escanear archivos grandes
            large_files = await self.scan_group_for_large_files(
                group_id, days_back, limit
            )
            
            # Procesar archivos encontrados
            await self.download_large_files_from_scan(large_files, auto_download)
            
        except Exception as e:
            error_msg = f"❌ Error en escaneo del grupo {group_id}: {e}"
            logger.logger.error(error_msg)
            await self.client.send_message(
                int(self.bot.TG_AUTHORIZED_USER_ID[0]),
                error_msg
            )