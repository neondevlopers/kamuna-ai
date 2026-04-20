# backend/config.py
"""
Configuration module for KAMUNA AI
Loads settings from environment variables or uses defaults
"""

import os
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()


class Config:
    """
    Main configuration class for the application
    """
    
    # ============================================
    # Ollama Settings
    # ============================================
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'deepseek-coder:1.3b-instruct-q2_K')
    
    # ============================================
    # Colab API Settings
    # ============================================
    COLAB_API_URL = os.getenv('COLAB_API_URL', 'link-api')
    USE_COLAB = os.getenv('USE_COLAB', 'True').lower() == 'true'
    
    # ============================================
    # Flask Server Settings
    # ============================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'kamuna-ai-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # ============================================
    # Database Settings
    # ============================================
    SQLITE_PATH = os.getenv('SQLITE_PATH', 'memory_db/sqlite.db')
    CHROMA_PATH = os.getenv('CHROMA_PATH', 'memory_db/chroma_db')
    
    # ============================================
    # Data Directories
    # ============================================
    LOGS_DIR = os.getenv('LOGS_DIR', 'data/logs')
    SCANS_DIR = os.getenv('SCANS_DIR', 'data/scans')
    EXPORTS_DIR = os.getenv('EXPORTS_DIR', 'data/exports')
    
    # Create directories if they don't exist
    @classmethod
    def create_directories(cls):
        """Create all necessary directories"""
        dirs = [cls.LOGS_DIR, cls.SCANS_DIR, cls.EXPORTS_DIR, 'memory_db']
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    # ============================================
    # API Settings
    # ============================================
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 90))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    # ============================================
    # Security Settings
    # ============================================
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 10000))
    MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', 10))


# Create directories when config is imported
Config.create_directories()

# For backward compatibility
config = Config