import logging
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient, events
import importlib

# Указываем папку modules в системном пути
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Загружаем переменные из .env файла
load_dotenv()

# Извлекаем данные из .env
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Устанавливаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем клиента
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Папка с модулями
modules_path = './modules'

# Функция для динамической загрузки всех модулей из папки 'modules'
def load_modules():
    # Проходим по всем файлам в папке modules
    for filename in os.listdir(modules_path):
        if filename.endswith('.py') and filename != '__init__.py':  # исключаем __init__.py
            module_name = filename[:-3]  # Убираем '.py' из имени
            try:
                # импортируем модули и их обработчики к основному файлу (необходимо в связи с тем, что скрипты должны вызываться из основного файла)
                module = importlib.import_module(f'modules.{module_name}')
                if hasattr(module, 'register_get_id_handler'):
                    module.register_get_id_handler(client)
                if hasattr(module, 'register_create_role_handler'):
                    module.register_create_role_handler(client)
                if hasattr(module, 'register_get_delete_role_handler'):
                    module.register_get_delete_role_handler(client)
                if hasattr(module, 'register_assign_role_handler'):
                    module.register_assign_role_handler(client)
                if hasattr(module, 'register_revoke_role_handler'):
                    module.register_revoke_role_handler(client)
                if hasattr(module, 'register_admin_list_handler'):
                    module.register_admin_list_handler(client)  
                logger.info(f"Модуль {module_name} успешно загружен.")
                

            except Exception as e:
                logger.error(f"Ошибка при загрузке модуля {module_name}: {e}")

# Загружаем все модули
load_modules()

# Запускаем клиента
if __name__ == '__main__':
    logger.info("Бот запущен!")
    client.run_until_disconnected()
