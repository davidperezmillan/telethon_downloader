from telethon.utils import get_peer_id, resolve_id
import telethon
import logger


class CommandHandler:
    def __init__(self, environments):
        self.command_dict = {
            "/help": self.handle_help,
            "/version": self.handle_version,
            "/telethon": self.handle_telethon_version,
            "/id": self.handle_id,
            "/scanlarge": self.handle_scan_large,
            "/scanlist": self.handle_scan_list,
            "/autostatus": self.handle_auto_status,
            "/autoadd": self.handle_auto_add_group,
            "/autoremove": self.handle_auto_remove_group,
        }

        self.environments = environments

    def process_command(self, message):
        try:
            command_parts = str(message.message).split()
            command = command_parts[0]
            args = command_parts[1:] if len(command_parts) > 1 else []
            
            logger.logger.info(f"process_command => command: {command}, args: {args}")

            handler_method = self.command_dict.get(command)

            if self._function_accepts_args(handler_method):
                return handler_method(message, args)
            else:
                return handler_method()

        except Exception as e:
            logger.logger.info(f"process_command => Exception: {e}")
            return f"Error processing command: {e}"

    def _function_accepts_args(self, func):
        # Verificar si la función acepta argumentos adicionales
        return hasattr(func, "__code__") and func.__code__.co_argcount > 1

    def handle_help(self):
        help_message = "Welcome to the bot!\n\n"
        help_message += "Available commands:\n\n"
        help_message += "/id - Shows the user/group ID\n"
        help_message += "/help - Displays the help message\n"
        help_message += "/rename - Change file name by replying or selecting the file and typing the new name\n"
        help_message += "/telethon - Displays the Telethon version\n"
        help_message += "/version - Displays the bot version\n\n"
        help_message += "🔍 Large File Scanner Commands:\n"
        help_message += f"/scanlarge <group_id> [days] [limit] - Scan and download large files (>{self.environments.constants.get_variable('SCAN_MIN_FILE_SIZE_MB')}MB) from a group\n"
        help_message += "   Example: /scanlarge -1001234567890 30 1000\n"
        help_message += "/scanlist <group_id> [days] [limit] - Only list large files without downloading\n"
        help_message += "   Example: /scanlist -1001234567890 7\n\n"
        help_message += "🤖 Auto Scanner Commands:\n"
        help_message += "/autostatus - Show auto scanner status and monitored groups\n"
        help_message += "/autoadd <group_id> - Add group to auto monitoring (runtime only)\n"
        help_message += "/autoremove <group_id> - Remove group from auto monitoring (runtime only)\n"
        help_message += "\nParameters:\n"
        help_message += "- group_id: Telegram group ID (required)\n"
        help_message += f"- days: Days back to search (optional, default: {self.environments.constants.get_variable('SCAN_DEFAULT_DAYS')})\n"
        help_message += f"- limit: Max messages to check (optional, default: {'no limit' if not self.environments.constants.get_variable('SCAN_DEFAULT_LIMIT') else self.environments.constants.get_variable('SCAN_DEFAULT_LIMIT')})\n\n"
        help_message += "ℹ️ Auto scanner monitors groups in real-time for large files"
        return help_message

    def handle_version(self):
        logger.logger.info(f"handle_version: {self.environments.VERSION}")
        return f"version: {self.environments.VERSION}"

    def handle_telethon_version(self):
        logger.logger.info(f"handle_telethon_version: {telethon.__version__}")
        return f"telethon version: {telethon.__version__}"

    def handle_id(self, message, args=None):
        real_id = get_peer_id(message.peer_id)
        logger.logger.info(f"commands => real_id: {real_id}")
        return f"id: {str(real_id)}"

    def handle_scan_large(self, message, args):
        """
        Maneja el comando /scanlarge para escanear y descargar archivos grandes
        Formato: /scanlarge <group_id> [days] [limit]
        """
        try:
            if not args or len(args) < 1:
                return ("❌ Error: Group ID requerido\n"
                       "Uso: /scanlarge <group_id> [days] [limit]\n"
                       "Ejemplo: /scanlarge -1001234567890 30 1000")
            
            group_id = args[0]
            days_back = int(args[1]) if len(args) > 1 and args[1].isdigit() else self.environments.constants.get_variable('SCAN_DEFAULT_DAYS')
            limit = int(args[2]) if len(args) > 2 and args[2].isdigit() else self.environments.constants.get_variable('SCAN_DEFAULT_LIMIT')
            
            # Validar group_id
            try:
                group_id = int(group_id)
            except ValueError:
                return "❌ Error: Group ID debe ser un número válido"
            
            # Validar parámetros
            max_days = self.environments.constants.get_variable('SCAN_MAX_DAYS')
            if days_back <= 0 or days_back > max_days:
                return f"❌ Error: Los días deben estar entre 1 y {max_days}"
            
            if limit is not None and (limit <= 0 or limit > 10000):
                return "❌ Error: El límite debe estar entre 1 y 10000"
            
            return {
                'action': 'scan_large',
                'group_id': group_id,
                'days_back': days_back,
                'limit': limit,
                'auto_download': True
            }
            
        except Exception as e:
            logger.logger.error(f"handle_scan_large error: {e}")
            return f"❌ Error procesando comando: {e}"

    def handle_scan_list(self, message, args):
        """
        Maneja el comando /scanlist para solo listar archivos grandes sin descargar
        Formato: /scanlist <group_id> [days] [limit]
        """
        try:
            if not args or len(args) < 1:
                return ("❌ Error: Group ID requerido\n"
                       "Uso: /scanlist <group_id> [days] [limit]\n"
                       "Ejemplo: /scanlist -1001234567890 7")
            
            group_id = args[0]
            days_back = int(args[1]) if len(args) > 1 and args[1].isdigit() else self.environments.constants.get_variable('SCAN_DEFAULT_DAYS')
            limit = int(args[2]) if len(args) > 2 and args[2].isdigit() else self.environments.constants.get_variable('SCAN_DEFAULT_LIMIT')
            
            # Validar group_id
            try:
                group_id = int(group_id)
            except ValueError:
                return "❌ Error: Group ID debe ser un número válido"
            
            # Validar parámetros
            max_days = self.environments.constants.get_variable('SCAN_MAX_DAYS')
            if days_back <= 0 or days_back > max_days:
                return f"❌ Error: Los días deben estar entre 1 y {max_days}"
            
            if limit is not None and (limit <= 0 or limit > 10000):
                return "❌ Error: El límite debe estar entre 1 y 10000"
            
            return {
                'action': 'scan_list',
                'group_id': group_id,
                'days_back': days_back,
                'limit': limit,
                'auto_download': False
            }
            
        except Exception as e:
            logger.logger.error(f"handle_scan_list error: {e}")
            return f"❌ Error procesando comando: {e}"

    def handle_auto_status(self, message, args=None):
        """
        Muestra el estado actual del auto scanner
        """
        try:
            status = self.environments.auto_scanner.get_status_info()
            
            status_message = "🤖 **Estado del Auto Scanner**\n\n"
            
            if status['enabled']:
                status_message += "✅ **Estado:** Habilitado\n"
                status_message += f"📊 **Tamaño mínimo:** {status['min_file_size_mb']} MB\n"
                status_message += f"🔔 **Notificaciones:** {'Habilitadas' if status['notify_user'] else 'Deshabilitadas'}\n"
                status_message += f"📋 **Modo lista:** {'Solo grupos listados' if status['whitelist_only'] else 'Todos excepto listados'}\n"
                status_message += f"🏷️ **Total grupos configurados:** {status['total_monitored_groups']}\n\n"
                
                if status['monitored_groups']:
                    status_message += "📝 **Grupos configurados:**\n"
                    for group_id in status['monitored_groups']:
                        status_message += f"   • {group_id}\n"
                else:
                    status_message += "📝 **No hay grupos configurados**\n"
                    
                status_message += "\nℹ️ *Use /autoadd y /autoremove para modificar en tiempo de ejecución*"
            else:
                status_message += "❌ **Estado:** Deshabilitado\n\n"
                status_message += "Para habilitar, configure AUTO_SCAN_ENABLED=true en las variables de entorno"
            
            return status_message
            
        except Exception as e:
            logger.logger.error(f"handle_auto_status error: {e}")
            return f"❌ Error obteniendo estado: {e}"

    def handle_auto_add_group(self, message, args):
        """
        Agrega un grupo al monitoreo automático (solo runtime)
        """
        try:
            if not args or len(args) < 1:
                return ("❌ Error: Group ID requerido\n"
                       "Uso: /autoadd <group_id>\n"
                       "Ejemplo: /autoadd -1001234567890")
            
            if not self.environments.auto_scanner.is_auto_scan_enabled():
                return "❌ Error: Auto scanner está deshabilitado. Configure AUTO_SCAN_ENABLED=true"
            
            try:
                group_id = int(args[0])
            except ValueError:
                return "❌ Error: Group ID debe ser un número válido"
            
            # Agregar grupo a la lista monitoreada (solo runtime)
            if group_id not in self.environments.auto_scanner.monitored_groups:
                self.environments.auto_scanner.monitored_groups.append(group_id)
                logger.logger.info(f"Added group {group_id} to auto monitoring")
                return f"✅ Grupo {group_id} agregado al monitoreo automático\n\nℹ️ *Cambio temporal - reiniciar el bot restaurará la configuración original*"
            else:
                return f"ℹ️ El grupo {group_id} ya está en la lista de monitoreo"
                
        except Exception as e:
            logger.logger.error(f"handle_auto_add_group error: {e}")
            return f"❌ Error agregando grupo: {e}"

    def handle_auto_remove_group(self, message, args):
        """
        Remueve un grupo del monitoreo automático (solo runtime)
        """
        try:
            if not args or len(args) < 1:
                return ("❌ Error: Group ID requerido\n"
                       "Uso: /autoremove <group_id>\n"
                       "Ejemplo: /autoremove -1001234567890")
            
            if not self.environments.auto_scanner.is_auto_scan_enabled():
                return "❌ Error: Auto scanner está deshabilitado. Configure AUTO_SCAN_ENABLED=true"
            
            try:
                group_id = int(args[0])
            except ValueError:
                return "❌ Error: Group ID debe ser un número válido"
            
            # Remover grupo de la lista monitoreada (solo runtime)
            if group_id in self.environments.auto_scanner.monitored_groups:
                self.environments.auto_scanner.monitored_groups.remove(group_id)
                logger.logger.info(f"Removed group {group_id} from auto monitoring")
                return f"✅ Grupo {group_id} removido del monitoreo automático\n\nℹ️ *Cambio temporal - reiniciar el bot restaurará la configuración original*"
            else:
                return f"ℹ️ El grupo {group_id} no está en la lista de monitoreo"
                
        except Exception as e:
            logger.logger.error(f"handle_auto_remove_group error: {e}")
            return f"❌ Error removiendo grupo: {e}"
