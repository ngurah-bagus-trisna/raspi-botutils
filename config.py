import os
import logging
from typing import List
from dotenv import load_dotenv

# --- Configuration Loader ---
load_dotenv()

# Basic Config
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Security
try:
    ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv('ADMIN_USER_IDS', '').split(',') if x.strip()]
except ValueError:
    ADMIN_USER_IDS = []

ENABLE_SHELL_EXEC = os.getenv('ENABLE_SHELL_EXEC', 'false').lower() == 'true'

# Features Toggle
ENABLE_CAMERA = os.getenv('ENABLE_CAMERA', 'true').lower() == 'true'
ENABLE_DOCKER = os.getenv('ENABLE_DOCKER', 'true').lower() == 'true'

# Thresholds
ALERT_CPU_THRESHOLD = int(os.getenv('ALERT_CPU_THRESHOLD', 90))
ALERT_TEMP_THRESHOLD = int(os.getenv('ALERT_TEMP_THRESHOLD', 80))
ALERT_DISK_THRESHOLD = int(os.getenv('ALERT_DISK_THRESHOLD', 90))

# Paths
DB_FILE = os.getenv('DB_FILE', 'metrics.db')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Logging Setup
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE)
        ]
    )
    # Silence some noisy libs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    return logging.getLogger("RaspiBot")
