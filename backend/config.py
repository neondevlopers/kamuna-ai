import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Colab API
    COLAB_API_URL = os.getenv('COLAB_API_URL', 'https://your-url.ngrok-free.dev/chat')
    USE_COLAB = os.getenv('USE_COLAB', 'True').lower() == 'true'
    
    # Data directories
    LOGS_DIR = 'data/logs'
    SCANS_DIR = 'data/scans'
    EXPORTS_DIR = 'data/exports'
    
    # Create directories
    for dir_path in [LOGS_DIR, SCANS_DIR, EXPORTS_DIR]:
        os.makedirs(dir_path, exist_ok=True)