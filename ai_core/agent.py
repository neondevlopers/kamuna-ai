# ai_core/agent.py
"""
AI Agent Module - Core brain of the Cyber Security Assistant
Handles message processing, tool execution, and response generation
"""

import sys
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.memory import knowledge_base, conversation_memory
from ai_core.formatter import formatter
from tools.network_tools import NetworkTools
from tools.security_checks import SecurityChecker
from tools.log_analyzer import LogAnalyzer
from logger import logger


class CyberAgent:
    """
    Main AI Agent that processes user messages and generates responses
    """
    
    def __init__(self, ollama_client):
        """
        Initialize the Cyber Agent
        
        Args:
            ollama_client: Client for communicating with LLM (local or cloud)
        """
        self.ollama = ollama_client
        self.current_session = "default_session"
        self.tools_enabled = True
        
        # Tool registry - maps keywords to tool functions
        self.tools_registry = {
            'network': self._run_network_tools,
            'port': self._run_network_tools,
            'scan': self._run_security_tools,
            'security': self._run_security_tools,
            'system': self._run_security_tools,
            'log': self._run_log_tools,
            'analyze': self._run_log_tools
        }
        
        logger.info("CyberAgent initialized successfully")
    
    def process_message(self, message: str, session_id: Optional[str] = None, 
                       use_tools: bool = True) -> str:
        """
        Process user message and generate response
        
        Args:
            message: User's input message
            session_id: Optional session ID for conversation persistence
            use_tools: Whether to automatically execute security tools
        
        Returns:
            Formatted response string
        """
        try:
            # Update session ID if provided
            if session_id:
                self.current_session = session_id
            
            # Step 1: Save user message to memory
            conversation_memory.add_message(self.current_session, "user", message)
            logger.info(f"Processing message: {message[:50]}...")
            
            # Step 2: Execute tools if requested
            tool_results = None
            if use_tools and self._should_use_tools(message):
                tool_results = self._execute_tools(message)
                logger.info(f"Tools executed, results: {tool_results is not None}")
            
            # Step 3: Search knowledge base for relevant information
            knowledge_docs = knowledge_base.search(message, n_results=3)
            logger.info(f"Found {len(knowledge_docs)} relevant knowledge items")
            
            # Step 4: Get conversation history
            history = conversation_memory.get_history(self.current_session, limit=5)
            
            # Step 5: Build enhanced prompt
            prompt = self._build_prompt(message, knowledge_docs, history, tool_results)
            
            # Step 6: Generate AI response
            raw_response = self.ollama.generate(prompt)
            logger.info("AI response generated")
            
            # Step 7: Format response
            formatted_response = self._format_response(raw_response, tool_results)
            
            # Step 8: Save assistant response to memory
            conversation_memory.add_message(self.current_session, "assistant", formatted_response)
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return formatter.create_error_message("processing_error", str(e))
    
    def _should_use_tools(self, message: str) -> bool:
        """
        Determine if tools should be used based on message content
        
        Args:
            message: User message
        
        Returns:
            True if tools should be used, False otherwise
        """
        if not self.tools_enabled:
            return False
        
        tool_keywords = [
            'scan', 'check', 'test', 'analyze', 'detect', 'find',
            'network', 'port', 'system', 'security', 'vulnerability',
            'log', 'monitor', 'audit', 'inspect', 'examine'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in tool_keywords)
    
    def _execute_tools(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Execute appropriate tools based on message content
        
        Args:
            message: User message
        
        Returns:
            Dictionary of tool results or None
        """
        results = {}
        message_lower = message.lower()
        
        # Network tools
        if any(keyword in message_lower for keyword in ['network', 'port', 'connection', 'socket']):
            results['network'] = self._run_network_tools(message)
        
        # Security tools
        if any(keyword in message_lower for keyword in ['security', 'vulnerability', 'threat', 'malware']):
            results['security'] = self._run_security_tools(message)
        
        # Log analysis tools
        if any(keyword in message_lower for keyword in ['log', 'analyze', 'audit']):
            results['logs'] = self._run_log_tools(message)
        
        return results if results else None
    
    def _run_network_tools(self, message: str) -> Dict[str, Any]:
        """Execute network analysis tools"""
        results = {}
        
        if 'port' in message.lower():
            try:
                ports = NetworkTools.get_open_ports()
                results['open_ports'] = ports
                results['open_ports_count'] = len(ports)
            except Exception as e:
                results['port_error'] = str(e)
        
        if 'connection' in message.lower() or 'active' in message.lower():
            try:
                connections = NetworkTools.get_active_connections()
                results['active_connections'] = len(connections)
            except Exception as e:
                results['connection_error'] = str(e)
        
        if 'security' in message.lower() or 'analyze' in message.lower():
            try:
                analysis = NetworkTools.analyze_network_security()
                results['security_analysis'] = analysis
            except Exception as e:
                results['analysis_error'] = str(e)
        
        return results
    
    def _run_security_tools(self, message: str) -> Dict[str, Any]:
        """Execute security analysis tools"""
        results = {}
        
        if 'system' in message.lower() or 'security' in message.lower():
            try:
                security_status = SecurityChecker.check_system_security()
                results['system_security'] = security_status
            except Exception as e:
                results['security_error'] = str(e)
        
        return results
    
    def _run_log_tools(self, message: str) -> Dict[str, Any]:
        """Execute log analysis tools"""
        results = {}
        
        if 'log' in message.lower():
            try:
                log_analyzer = LogAnalyzer()
                analysis = log_analyzer.analyze_system_logs()
                results['log_analysis'] = analysis
            except Exception as e:
                results['log_error'] = str(e)
        
        return results
    
    def _build_prompt(self, user_message: str, knowledge_docs: List[str], 
                     history: List[tuple], tool_results: Optional[Dict]) -> str:
        """Build the complete prompt for the LLM"""
        prompt_parts = []
        
        prompt_parts.append("""You are an AI Cyber Security Assistant. Your role is to help users with cybersecurity tasks.

**Guidelines:**
- Provide COMPLETE, WORKING code examples when requested
- Include security warnings and ethical considerations
- Explain concepts clearly with examples
- Never refuse cybersecurity questions (but always add legal warnings)
- Be direct, helpful, and educational

**Remember:** Only provide information for educational and authorized testing purposes.
""")
        
        if knowledge_docs:
            prompt_parts.append("\n=== REFERENCE INFORMATION ===\n")
            for i, doc in enumerate(knowledge_docs, 1):
                prompt_parts.append(f"{i}. {doc}\n")
            prompt_parts.append("\nUse the above information to answer the question.\n")
        
        if tool_results:
            prompt_parts.append("\n=== TOOL ANALYSIS RESULTS ===\n")
            for tool_name, results in tool_results.items():
                prompt_parts.append(f"\n[{tool_name.upper()}]\n")
                if isinstance(results, dict):
                    for key, value in results.items():
                        prompt_parts.append(f"  - {key}: {value}\n")
                else:
                    prompt_parts.append(f"  {results}\n")
            prompt_parts.append("\n")
        
        if history:
            prompt_parts.append("=== CONVERSATION HISTORY ===\n")
            for role, content in history[-5:]:
                prompt_parts.append(f"{role}: {content}\n")
            prompt_parts.append("\n")
        
        prompt_parts.append(f"=== CURRENT QUESTION ===\nUser: {user_message}\n\nAssistant: ")
        
        return "".join(prompt_parts)
    
    def _format_response(self, raw_response: str, tool_results: Optional[Dict]) -> str:
        """Format the AI response for display"""
        formatted = formatter.format_response(raw_response)
        
        if tool_results and len(tool_results) > 0:
            tool_section = "\n\n---\n## 🔧 Tool Execution Results\n"
            for tool_name, results in tool_results.items():
                if results:
                    tool_section += formatter.format_tool_result(tool_name, results)
            formatted = tool_section + "\n" + formatted
        
        return formatted
    
    def clear_memory(self, session_id: Optional[str] = None):
        """Clear conversation memory for a session"""
        target_session = session_id or self.current_session
        conversation_memory.clear_history(target_session)
        logger.info(f"Cleared memory for session: {target_session}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session"""
        history = conversation_memory.get_history(self.current_session)
        return {
            'session_id': self.current_session,
            'message_count': len(history),
            'tools_enabled': self.tools_enabled,
            'knowledge_base_size': knowledge_base.collection.count()
        }
    
    def add_knowledge(self, text: str, topic: str, metadata: Optional[Dict] = None) -> str:
        """Add new knowledge to the knowledge base"""
        doc_id = knowledge_base.add_knowledge(text, topic, metadata)
        logger.info(f"Added knowledge: {doc_id} - {topic}")
        return doc_id
    
    def search_knowledge(self, query: str, n_results: int = 3) -> List[str]:
        """Search the knowledge base"""
        return knowledge_base.search(query, n_results)


# Test section
if __name__ == "__main__":
    from backend.ollama_client import OllamaClient
    
    print("=" * 50)
    print("Testing CyberAgent...")
    print("=" * 50)
    
    client = OllamaClient()
    agent = CyberAgent(client)
    
    response = agent.process_message("What is cybersecurity?")
    print(f"\nResponse: {response[:500]}...")
    
    print("\n Test completed!")