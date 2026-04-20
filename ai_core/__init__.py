# ai_core/__init__.py
"""
AI Core Module - Cyber Security Assistant Core Components

This module contains the core AI functionality for the Cyber Security Assistant:
- Agent: Main AI agent for processing messages
- Memory: Knowledge base and conversation memory
- Formatter: Response formatting utilities
- Prompts: System prompts for the AI

Exports:
    CyberAgent: Main AI agent class
    KnowledgeBase: Vector database for knowledge storage
    ConversationMemory: SQLite-based conversation history
    ResponseFormatter: Response formatting utilities
    formatter: Global formatter instance
    knowledge_base: Global knowledge base instance
    conversation_memory: Global conversation memory instance
"""

from ai_core.agent import CyberAgent
from ai_core.memory import KnowledgeBase, ConversationMemory, knowledge_base, conversation_memory
from ai_core.formatter import ResponseFormatter, formatter
from ai_core.prompts import SYSTEM_PROMPT

__version__ = "1.0.0"
__author__ = "Kamuna AI Team"
__all__ = [
    # Classes
    "CyberAgent",
    "KnowledgeBase", 
    "ConversationMemory",
    "ResponseFormatter",
    
    # Instances
    "knowledge_base",
    "conversation_memory",
    "formatter",
    
    # Constants
    "SYSTEM_PROMPT",
    
    # Version
    "__version__",
    "__author__"
]

# Module information
__description__ = """
Kamuna AI - Cyber Security Assistant
=====================================
An intelligent AI-powered cyber security assistant with:
- Local LLM support (Ollama + DeepSeek Coder)
- Vector knowledge base (ChromaDB)
- Conversation memory (SQLite)
- Security analysis tools
- Web interface

Usage:
    from ai_core import CyberAgent, knowledge_base
    
    agent = CyberAgent(ollama_client)
    response = agent.process_message("What is SQL injection?")
"""

# Initialize logging for the module
import logging
logger = logging.getLogger(__name__)
logger.debug(f"AI Core module v{__version__} initialized")