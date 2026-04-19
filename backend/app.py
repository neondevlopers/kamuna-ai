# backend/app.py
import sys
import os

# បន្ថែម root directory ទៅ sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.logger import logger
from backend.ollama_client import OllamaClient
from ai_core.agent import CyberAgent

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)
CORS(app)

ollama_client = OllamaClient()
agent = CyberAgent(ollama_client)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        response = agent.process_message(message, session_id)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/search', methods=['POST'])
def search_knowledge_api():
    from tools.knowledge_tools import search_knowledge
    data = request.json
    query = data.get('query', '')
    result = search_knowledge(query)
    return jsonify({'result': result})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    logger.info("Starting AI Cyber Assistant with ChromaDB...")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)