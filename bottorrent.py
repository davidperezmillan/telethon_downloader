#!/usr/bin/env python3
LICENCIA = """
BOT.Torrent - 3.1 :
Este programa es software GRATUITO: puedes redistribuirlo y/o modificar
bajo los términos de la Licencia Pública General GNU publicada por
la Free Software Foundation, ya sea la versión 3 de la Licencia, o
(a su elección) cualquier versión posterior.

Este programa se distribuye con la esperanza de que sea útil,
pero SIN NINGUNA GARANTÍA, ni RESPONSABILIDAD; sin siquiera la garantía implícita de
COMERCIABILIDAD o APTITUD PARA UN PROPÓSITO PARTICULAR. Ver el
Licencia pública general GNU para obtener más detalles <https://www.gnu.org/licenses/>.

El USUARIO de este programa, es el UNICO RESPONSABLE, de que el USO del mismo, 
se limita, al estricto cumplimiento, de cualquier LEY, aplicable.
"""
INSTALACION = """
BOT.Torrent - 3.1 :
*** Guía para instalar el bot ***
BOT.torrent es un sencillo script, para un BOT de Telegram, escrito en Python. 
Su función, es descargar ficheros, reenviados al BOT, en un directorio de nuestra elección.
Este BOT está especialmente pensado, para ejecutarse en un NAS.
Instalación:
1: Crear nuestro BOT en Telegram y obtener su TOKEN (Guías multiples en la red)
2: Crear nuestra App en Telegram y obtener su api_id y api_hash. (Si no las tenemos)
--> https://my.telegram.org/auth (Guías multiples en la red)
3: Instalar python3, en nuestro NAS. (Si no lo tenemos ya instalado. No es necesario en DSM7)
4: Instalar pip en nuestro NAS, abriendo una sesión SSH, (Si no lo tenemos ya instalado) 
--> sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
--> sudo python3 get-pip.py
5: Instalar telethon --> sudo python3 -m pip install telethon
6: Instalar cryptg --> sudo python3 -m pip install cryptg
7: Copiar BOT.torrent.py, en nuestro NAS y editar las variables propias DE CADA USUARIO. 
8: Ejecutar BOT de forma interactiva --> python3 -u BOT.torrent.py (Por supuesto, se puede arrancar, también en background y de formar automatizada)
A disfrutar ;-)

DekkaR - 2021
"""
AYUDA = """BOT.Torrent - 3.1 :
/ayuda      : Esta pantalla.
/start      : LICENCIA GPL, de este programa.
/instalar   : Guía para instalar este programa.  
"""
import re
import os
import shutil
import sys
import time
import asyncio
import cryptg
# Imports Telethon
from telethon import TelegramClient, events
from telethon.tl import types
from telethon.utils import get_extension

import logging

import watchdog.events
import watchdog.observers
import threading

'''
LOGGER
'''

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)-7s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Variables de cada usuario ######################
# This is a helper method to access environment variables or
# prompt the user to type them in the terminal if missing.
def get_env(name, message, cast=str):
    if name in os.environ:
        print("os.environ[name]",name,os.environ[name])
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)

# Define some variables so the code reads easier
session = os.environ.get('TG_SESSION', 'bottorrent_downloader')
api_id = get_env('TG_API_ID', 'Enter your API ID: ', int)
api_hash = get_env('TG_API_HASH', 'Enter your API hash: ')
bot_token = get_env('TG_BOT_TOKEN', 'Enter your Telegram BOT token: ')
TG_AUTHORIZED_USER_ID = get_env('TG_AUTHORIZED_USER_ID', 'Enter your Telegram BOT token: ')
#TG_DOWNLOAD_PATH = get_env('TG_DOWNLOAD_PATH', 'Enter full path to downloads directory: ')
TG_DOWNLOAD_PATH = os.getenv('TG_DOWNLOAD_PATH', '/download')
TG_DOWNLOAD_PATH_TORRENTS = os.getenv('TG_DOWNLOAD_PATH_TORRENTS', '/watch')

download_path = TG_DOWNLOAD_PATH
download_path_torrent = TG_DOWNLOAD_PATH_TORRENTS # Directorio bajo vigilancia de DSDownload u otro.

logger.info('TG_API_ID: %s',api_id)
logger.info('TG_API_HASH: %s',api_hash)
logger.info('TG_BOT_TOKEN: %s',bot_token)
logger.info('TG_DOWNLOAD_PATH: %s',download_path)
logger.info('DOWNLOAD_PATH_TORRENTS: %s',download_path_torrent)

#api_id = 161 # Vuestro api_id. Cambiar
#api_hash = '3ef04ad'
#bot_token = '3945:09m-p4'
#download_path = '/download'
#download_path_torrent = '/volume1/vuestros directorios' # Directorio bajo vigilancia de DSDownload u otro.
#usuarios = {6537361:'yo'} # <--- IDs de usuario autorizados. Los mismos de la versión 2.1. Cambiar
usuarios = list(map(int, TG_AUTHORIZED_USER_ID.replace(" ", "").split(','))) 
logger.info('TG_AUTHORIZED_USER_ID: %s',usuarios)

##################################################
################# LOG
#f = open( 'log.txt', 'a')
# Creación del logger que muestra la información únicamente por fichero.
#logging.basicConfig(format = '[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',	level = logging.DEBUG, filename = 'logs_info.txt', filemode = 'a')
#logger = logging.getLogger(__name__)
################# LOG
# Cola de descargas.
queue = asyncio.Queue()
number_of_parallel_downloads = int(os.environ.get('TG_MAX_PARALLEL',4))
maximum_seconds_per_download = int(os.environ.get('TG_DL_TIMEOUT',3600))

# Directorio temporal
tmp_path = os.path.join(download_path,'tmp')
completed_path = os.path.join(download_path,'completed')
temp_completed_path = ''

os.makedirs(tmp_path, exist_ok = True)
os.makedirs(completed_path, exist_ok = True)
os.makedirs(os.path.join(download_path,'mp3'), exist_ok = True)
os.makedirs(os.path.join(download_path,'pdf'), exist_ok = True)
os.makedirs(os.path.join(download_path,'torrent'), exist_ok = True)
os.makedirs(os.path.join(download_path,'sendFiles'), exist_ok = True)

FOLDER_GROUP = ''



async def tg_send_message(msg):
    await client.send_message(usuarios[0], msg)
    return True

async def tg_send_file(file,name=''):
    #await client.send_file(6537360, file)
    async with client.action(usuarios[0], 'document') as action:
    	await client.send_file(usuarios[0], file,caption=name,force_document=True,progress_callback=action.progress)
	#await client.send_message(6537360, file)

async def worker(name):
	while True:
		# Esperando una unidad de trabajo.

		queue_item = await queue.get()
		update = queue_item[0]
		message = queue_item[1]
		FOLDER_TO_GROUP = queue_item[2] if queue_item[2] else ''

		# Comprobación de usuario
		if message.peer_id.user_id not in usuarios:
			logger.info('USUARIO: %s NO AUTORIZADO', message.peer_id.user_id)
			print('Usuario ', message.peer_id.user_id, ' no autorizado.')
			continue
		###
		file_path = tmp_path;
		file_name = 'Fichero ...';
		if isinstance(update.message.media, types.MessageMediaPhoto):
			file_name = '{}{}'.format(update.message.media.photo.id, get_extension(update.message.media))
		else:
			attributes = update.message.media.document.attributes
			for attr in attributes:
				if isinstance(attr, types.DocumentAttributeFilename):
					file_name = attr.file_name
				elif update.message.message:
					file_name = re.sub(r'[^A-Za-z0-9 -!\[\]\(\)]+', ' ', update.message.message)
				else:
					file_name = time.strftime('%Y%m%d %H%M%S', time.localtime())
					file_name = '{}{}'.format(update.message.media.document.id, get_extension(update.message.media))
		file_path = os.path.join(file_path, file_name)
		await message.edit('Descargando ... ')
		mensaje = 'DESCARGA INICIADA %s [%s] por %s ...' % (time.strftime('%d/%m/%Y %H:%M:%S', time.localtime()), file_path , (message.peer_id.user_id))
		logger.info(mensaje)
		try:
			loop = asyncio.get_event_loop()
			task = loop.create_task(client.download_media(update.message, file_path))
			download_result = await asyncio.wait_for(task, timeout = maximum_seconds_per_download)
			end_time = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
			end_time_short = time.strftime('%H:%M', time.localtime())
			filename = os.path.split(download_result)[1]
			final_path = os.path.join(completed_path, filename)
			
			if FOLDER_TO_GROUP:
				final_path = os.path.join(FOLDER_TO_GROUP, filename)
				os.makedirs(FOLDER_TO_GROUP, exist_ok = True)
			else:
				# Ficheros .mp3 y .flac,
				if filename.endswith('.mp3') or filename.endswith('.flac'): final_path = os.path.join(download_path,"mp3", filename)
				# Ficheros .pdf y .cbr
				if filename.endswith('.pdf') or filename.endswith('.cbr'): final_path = os.path.join(download_path,"pdf", filename)
				# Ficheros .jpg
				if filename.endswith('.jpg'): 
					os.makedirs(os.path.join(download_path,'jpg'), exist_ok = True)
					final_path = os.path.join(download_path,"jpg", filename)
				# Ficheros .torrent
				if filename.endswith('.torrent'): final_path = os.path.join(download_path_torrent, filename)
			######
			logger.info("RENAME/MOVE [%s] [%s]" % (download_result, final_path) )
			shutil.move(download_result, final_path)
			######
			mensaje = 'DESCARGA TERMINADA %s [%s]' % (end_time, file_name)
			logger.info(mensaje)
			await message.edit('Descarga %s terminada %s' % (file_name,end_time_short))
		except asyncio.TimeoutError:
			print('[%s] Tiempo excedido %s' % (file_name, time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())))
			await message.edit('Error!')
			message = await update.reply('ERROR: Tiempo excedido descargando este fichero')
		except Exception as e:
			logger.critical(e)
			print('[EXCEPCION]: %s' % (str(e)))
			print('[%s] Excepcion %s' % (file_name, time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())))
			await message.edit('Error!')
			message = await update.reply('ERROR: %s descargando : %s' % (e.__class__.__name__, str(e)))

		# Unidad de trabajo terminada.
		queue.task_done()

client = TelegramClient(session, api_id, api_hash, proxy = None, request_retries = 10, flood_sleep_threshold = 120)

@events.register(events.NewMessage)
async def handler(update):
	global temp_completed_path
	global FOLDER_GROUP

	if update.message.media is not None and update.message.peer_id.user_id in usuarios:
		if FOLDER_GROUP != update.message.date:
			temp_completed_path  = ''

	if update.message.media is not None and update.message.peer_id.user_id in usuarios:
		file_name = 'sin nombre';

		if isinstance(update.message.media, types.MessageMediaPhoto):
			file_name = '{}{}'.format(update.message.media.photo.id, get_extension(update.message.media))
			logger.info("MessageMediaPhoto  [%s]" % file_name)
		else:	
			attributes = update.message.media.document.attributes
			for attr in attributes:
				if isinstance(attr, types.DocumentAttributeFilename):
					file_name = attr.file_name
				elif update.message.message:
					file_name = re.sub(r'[^A-Za-z0-9 -!\[\]\(\)]+', ' ', update.message.message)

		mensaje = 'DESCARGA EN COLA %s [%s] ' % (time.strftime('%d/%m/%Y %H:%M:%S', time.localtime()),file_name)
		logger.info(mensaje)
		message = await update.reply('En cola...')
		await queue.put([update, message,temp_completed_path])
	elif update.message.peer_id.user_id in usuarios:
		if update.message.message == '/ayuda':
			message = await update.reply(AYUDA) 
			await queue.put([update, message])
		elif update.message.message == '/start': 
			message = await update.reply(LICENCIA)
			await queue.put([update, message])
		elif update.message.message == '/instalar': 
			message = await update.reply(INSTALACION)
			await queue.put([update, message,temp_completed_path])
		else: 
			time.sleep(2)
			if '/folder' in update.message.message:
				folder = update.message.message
				FOLDER_GROUP = update.message.date
				temp_completed_path  = os.path.join(TG_DOWNLOAD_PATH,'completed',folder.replace('/folder ','')) # SI VIENE EL TEXTO '/folder NAME_FOLDER' ESTE CREARÁ UNA CARPETA Y METERÁ ADENTRO TODOS LOS ARCHIVOS A CONTINUACION 
				logger.info("DOWNLOAD FILE IN :[%s]",temp_completed_path)
			elif ((update.message.message).startswith('/SENDFILES')):
				os.makedirs(os.path.join(download_path,'sendFiles'), exist_ok = True)
				ignored = {"*._process"}
				basepath = os.path.join(download_path,'sendFiles')
				for root, subFolder, files in os.walk(basepath):
					subFolder.sort()
					files.sort()
					for item in files:
						if item.endswith('_process') :
							#skip directories
							continue
						fileNamePath = str(os.path.join(root,item))
						logger.info("SEND FILE :[%s]", fileNamePath)
						loop = asyncio.get_event_loop()
						task = loop.create_task(tg_send_file(fileNamePath,item))
						download_result = await asyncio.wait_for(task, timeout = maximum_seconds_per_download)
						#message = await tg_send_file(fileNamePath)
						shutil.move(fileNamePath, fileNamePath + "_process")
					#path = os.path.join(basepath, files)
			elif ((update.message.message).startswith('#')):
				folder = update.message.message
				FOLDER_GROUP = update.message.date
				temp_completed_path  = os.path.join(TG_DOWNLOAD_PATH,'completed',folder.replace('#','')) # SI VIENE EL TEXTO '/folder NAME_FOLDER' ESTE CREARÁ UNA CARPETA Y METERÁ ADENTRO TODOS LOS ARCHIVOS A CONTINUACION 
				logger.info("DOWNLOAD FILE IN :[%s]",temp_completed_path)
			else:
				message = await update.reply('reply Keep-Alive: ' + update.message.message)
				await queue.put([update, message])
				logger.info("Eco del BOT :[%s]",message)
				
			#print('Eco del BOT: ' + update.message.message)
	else:
		logger.info('USUARIO: %s NO AUTORIZADO', update.message.peer_id.user_id)


try:
	# Crear cola de procesos concurrentes.
	tasks = []
	for i in range(number_of_parallel_downloads):
		loop = asyncio.get_event_loop()
		task = loop.create_task(worker('worker-{%i}' %i))
		tasks.append(task)

	# Arrancamos bot con token
	client.start(bot_token=str(bot_token))
	client.add_event_handler(handler)

	# Pulsa Ctrl+C para detener
	print('Arranque correcto!! (Pulsa Ctrl+C para detener)')
	loop.run_until_complete(tg_send_message("START BOT TORRENT DOWNLOADER"))
	logger.info("********** START BOT_TORRENT_DOWNLOADER **********")




	client.run_until_disconnected()
finally:
	# Cerrando trabajos.
	
#f.close()
	for task in tasks:
		task.cancel()
	# Cola cerrada
	# Stop Telethon
	client.disconnect()
	print(' Parado!!! ')
	
