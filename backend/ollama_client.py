# backend/ollama_client.py
import sys
import os
import requests
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import config from backend
from backend.config import Config

# Import logger
try:
    from backend.logger import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self):
        # Use config values
        self.colab_api_url = Config.COLAB_API_URL
        self.use_colab = Config.USE_COLAB
        self.timeout = Config.API_TIMEOUT
    
    def generate(self, prompt: str, system_prompt: str = None, stream: bool = False):
        """Generate response from Colab API"""
        try:
            payload = {"message": prompt}
            
            headers = {
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            }
            
            response = requests.post(
                self.colab_api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from API")
            else:
                return f"API Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timeout. Please try again."
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Colab API. Make sure Colab is still running."
        except Exception as e:
            logger.error(f"API error: {e}")
            return f"Error: {str(e)}"
    
    def list_models(self):
        return [{"name": "DeepSeek Coder (via Colab)"}]