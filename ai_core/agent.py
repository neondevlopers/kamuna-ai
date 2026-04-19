# ai_core/agent.py
from ai_core.memory import knowledge_base, conversation_memory
from logger import logger

class CyberAgent:
    def __init__(self, ollama_client):
        self.ollama = ollama_client
        self.current_session = "default"
    
    def process_message(self, message, session_id=None):
        """Running"""
        if session_id:
            self.current_session = session_id
        
        conversation_memory.add_message(self.current_session, "user", message)
        
        documents, metadatas, distances = knowledge_base.search(message, n_results=3)
        
        history = conversation_memory.get_history(self.current_session, limit=3)
        
        enhanced_prompt = self._build_prompt(message, documents, history)
        
        response = self.ollama.generate(enhanced_prompt)
        
        conversation_memory.add_message(self.current_session, "assistant", response)
        
        return response
    
    def _build_prompt(self, user_message, knowledge_docs, history):
        """ prompt with knowledge"""
        
        prompt_parts = []
        
        # Knowledge base
        if knowledge_docs:
            prompt_parts.append("=== KNOWLEDGE BASE INFORMATION ===\n")
            for i, doc in enumerate(knowledge_docs, 1):
                prompt_parts.append(f"{i}. {doc}\n")
            prompt_parts.append("\nUse the above information to answer the question.\n\n")
        
        # Conversation history
        if history:
            prompt_parts.append("=== CONVERSATION HISTORY ===\n")
            for role, content in history:
                prompt_parts.append(f"{role}: {content}\n")
            prompt_parts.append("\n")
        
        # Current question
        prompt_parts.append(f"=== QUESTION ===\nUser: {user_message}\n\nAssistant: ")
        
        return "".join(prompt_parts)