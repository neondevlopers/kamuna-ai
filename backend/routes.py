# backend/routes.py
from flask import request, jsonify, render_template
from ollama_client import OllamaClient
from logger import logger

ollama_client = OllamaClient()

def register_routes(app):
    
    @app.route('/')
    def index():
        """Web UI"""
        return render_template('index.html')
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """API Call AI"""
        try:
            data = request.json
            message = data.get('message', '')
            use_tools = data.get('use_tools', False)
            
            if not message:
                return jsonify({'error': 'Empty message'}), 400
            
            # ហៅ AI
            response = ollama_client.generate(message)
            
            return jsonify({
                'response': response,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """show server"""
        return jsonify({
            'status': 'healthy',
            'api_connected': ollama_client.use_colab
        })
    
    @app.route('/api/models', methods=['GET'])
    def list_models():
        """show model """
        return jsonify({
            'models': ollama_client.list_models()
        })