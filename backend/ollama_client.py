import requests
import json
from config import Config
from logger import logger

class OllamaClient:
    def __init__(self):
        # Colab API URL 
        self.colab_api_url = "https://always-desecrate-violator.ngrok-free.dev/chat"
        self.use_colab = True
    
    def generate(self, prompt: str, system_prompt: str = None, stream: bool = False):
        """Generate response from DeepSeek Coder via Colab API"""
        try:
            # Payload
            payload = {
                "message": prompt
            }
            
            # ngrok warning
            headers = {
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            }
            
            # API CALL
            response = requests.post(
                self.colab_api_url,
                json=payload,
                headers=headers,
                timeout=90  
            )
            
            # Checking
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from API")
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timeout. Please try again."
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Colab API. Make sure Colab is still running."
        except Exception as e:
            logger.error(f"Colab API error: {e}")
            return f"Error: {str(e)}"
    
    def list_models(self):
        """Return available models"""
        return [{"name": "DeepSeek Coder 1.3B (via Colab)"}]