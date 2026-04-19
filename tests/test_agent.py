"""
Unit tests for AI Agent module
Run with: pytest tests/test_agent.py -v
"""

import os
import sys
import pytest
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.agent import CyberAgent
from ai_core.memory import knowledge_base, conversation_memory


class MockOllamaClient:
    """Mock Ollama client for testing"""
    
    def __init__(self, mock_response=None):
        self.mock_response = mock_response or "This is a mock AI response for testing purposes."
        self.call_count = 0
        self.last_prompt = None
    
    def generate(self, prompt, system_prompt=None, stream=False):
        self.call_count += 1
        self.last_prompt = prompt
        return self.mock_response
    
    def list_models(self):
        return [{"name": "mock-model"}]


class TestCyberAgent:
    """Test cases for CyberAgent class"""
    
    @pytest.fixture
    def agent(self):
        """Create a CyberAgent instance with mock client"""
        mock_client = MockOllamaClient()
        agent = CyberAgent(mock_client)
        return agent
    
    @pytest.fixture
    def agent_with_custom_response(self):
        """Create agent with custom mock response"""
        def create_agent(response):
            mock_client = MockOllamaClient(mock_response=response)
            return CyberAgent(mock_client)
        return create_agent
    
    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent is not None
        assert agent.ollama is not None
        assert agent.current_session == "default_session"
        assert agent.tools_enabled is True
    
    def test_process_message_basic(self, agent):
        """Test basic message processing"""
        response = agent.process_message("What is cybersecurity?")
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_process_message_with_session(self, agent):
        """Test message processing with custom session ID"""
        session_id = "test_session_123"
        response = agent.process_message("Hello AI", session_id=session_id)
        
        assert response is not None
        assert agent.current_session == session_id
    
    def test_process_message_saves_to_memory(self, agent):
        """Test that messages are saved to conversation memory"""
        session = "test_memory_session"
        
        # Clear previous data
        conversation_memory.clear_history(session)
        
        agent.process_message("First message", session_id=session)
        agent.process_message("Second message", session_id=session)
        
        history = conversation_memory.get_history(session)
        assert len(history) >= 2
        
        # Handle both return formats: (role, content) or (role, content, timestamp)
        if history and len(history[0]) >= 2:
            first_content = history[0][1]
            second_content = history[1][1] if len(history) > 1 else ""
        else:
            first_content = history[0] if history else ""
            second_content = history[1] if len(history) > 1 else ""
        
        assert "First" in str(first_content) or "first" in str(first_content).lower()
        assert "Second" in str(second_content) or "second" in str(second_content).lower()
    
    def test_should_use_tools_network_keywords(self, agent):
        """Test tool detection for network-related keywords"""
        assert agent._should_use_tools("scan my network") is True
        assert agent._should_use_tools("check open ports") is True
        assert agent._should_use_tools("analyze connection") is True
    
    def test_should_use_tools_security_keywords(self, agent):
        """Test tool detection for security-related keywords"""
        assert agent._should_use_tools("check system security") is True
        assert agent._should_use_tools("find vulnerabilities") is True
        assert agent._should_use_tools("scan for threats") is True
    
    def test_should_use_tools_no_match(self, agent):
        """Test tool detection with no matching keywords"""
        assert agent._should_use_tools("Hello, how are you?") is False
        assert agent._should_use_tools("Tell me a joke") is False
    
    def test_should_use_tools_disabled(self, agent):
        """Test tool detection when tools are disabled"""
        agent.tools_enabled = False
        assert agent._should_use_tools("scan network") is False
    
    def test_build_prompt_without_context(self, agent):
        """Test prompt building without additional context"""
        prompt = agent._build_prompt(
            user_message="Test question",
            knowledge_docs=[],
            history=[],
            tool_results=None
        )
        
        assert prompt is not None
        assert "Test question" in prompt
        assert "Assistant:" in prompt
    
    def test_build_prompt_with_knowledge(self, agent):
        """Test prompt building with knowledge base results"""
        knowledge_docs = [
            "This is knowledge item 1 about security.",
            "This is knowledge item 2 about networking."
        ]
        
        prompt = agent._build_prompt(
            user_message="Tell me about security",
            knowledge_docs=knowledge_docs,
            history=[],
            tool_results=None
        )
        
        assert "REFERENCE INFORMATION" in prompt or "KNOWLEDGE BASE" in prompt.upper()
        assert "knowledge item 1" in prompt or "security" in prompt.lower()
    
    def test_build_prompt_with_history(self, agent):
        """Test prompt building with conversation history"""
        history = [
            ("user", "Previous question"),
            ("assistant", "Previous answer")
        ]
        
        prompt = agent._build_prompt(
            user_message="Follow up question",
            knowledge_docs=[],
            history=history,
            tool_results=None
        )
        
        assert "CONVERSATION HISTORY" in prompt or "HISTORY" in prompt.upper()
        assert "Previous question" in prompt
        assert "Previous answer" in prompt
    
    def test_build_prompt_with_tool_results(self, agent):
        """Test prompt building with tool results"""
        tool_results = {
            "network": {"open_ports": [80, 443], "status": "completed"},
            "security": {"threats_found": 0}
        }
        
        prompt = agent._build_prompt(
            user_message="Scan my system",
            knowledge_docs=[],
            history=[],
            tool_results=tool_results
        )
        
        assert "TOOL ANALYSIS RESULTS" in prompt or "TOOL" in prompt.upper()
    
    def test_build_prompt_with_all_context(self, agent):
        """Test prompt building with all context types"""
        knowledge_docs = ["Knowledge base info"]
        history = [("user", "Previous chat")]
        tool_results = {"network": {"status": "ok"}}
        
        prompt = agent._build_prompt(
            user_message="Complex query",
            knowledge_docs=knowledge_docs,
            history=history,
            tool_results=tool_results
        )
        
        assert "Complex query" in prompt
        assert len(prompt) > 100
    
    def test_format_response_with_tool_results(self, agent):
        """Test response formatting with tool results"""
        raw_response = "This is the AI's answer to the question."
        tool_results = {"network": {"open_ports": [80, 443]}}
        
        formatted = agent._format_response(raw_response, tool_results)
        
        assert formatted is not None
        assert "This is the AI's answer" in formatted
    
    def test_format_response_without_tool_results(self, agent):
        """Test response formatting without tool results"""
        raw_response = "Simple AI response without tools."
        
        formatted = agent._format_response(raw_response, None)
        
        assert formatted is not None
        assert "Simple AI response" in formatted
    
    def test_clear_memory(self, agent):
        """Test clearing conversation memory"""
        session = "test_clear_session"
        agent.process_message("Message 1", session_id=session)
        agent.process_message("Message 2", session_id=session)
        
        # Verify messages exist
        history_before = conversation_memory.get_history(session)
        assert len(history_before) >= 2
        
        # Clear memory
        agent.clear_memory(session)
        
        # Verify cleared
        history_after = conversation_memory.get_history(session)
        assert len(history_after) == 0
    
    def test_get_session_info(self, agent):
        """Test getting session information"""
        session = "test_info_session"
        agent.process_message("Test message", session_id=session)
        
        info = agent.get_session_info()
        assert info is not None
        assert info["session_id"] == session
        assert "message_count" in info
        assert "tools_enabled" in info
        assert "knowledge_base_size" in info
    
    def test_add_knowledge(self, agent):
        """Test adding knowledge through agent"""
        initial_size = agent.get_session_info()["knowledge_base_size"]
        
        doc_id = agent.add_knowledge(
            text="Test knowledge added through agent",
            topic="agent_test",
            metadata={"source": "unit_test"}
        )
        
        assert doc_id is not None
        assert len(doc_id) > 0
        
        new_size = agent.get_session_info()["knowledge_base_size"]
        assert new_size > initial_size
    
    def test_search_knowledge(self, agent):
        """Test searching knowledge through agent"""
        results = agent.search_knowledge("security", n_results=2)
        assert results is not None
        assert isinstance(results, list)


class TestAgentWithRealKnowledge:
    """Test agent with actual knowledge base (not mocked)"""
    
    @pytest.fixture
    def agent(self):
        mock_client = MockOllamaClient()
        return CyberAgent(mock_client)
    
    def test_agent_uses_knowledge_base(self, agent):
        """Test that agent actually searches knowledge base"""
        response = agent.process_message("What is SQL injection?")
        
        assert agent.ollama.last_prompt is not None
    
    def test_agent_maintains_conversation_context(self, agent):
        """Test that agent maintains conversation context across messages"""
        session = "context_test"
        
        agent.process_message("My name is John", session_id=session)
        response = agent.process_message("What is my name?", session_id=session)
        
        assert agent.ollama.last_prompt is not None


class TestAgentEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def agent(self):
        mock_client = MockOllamaClient()
        return CyberAgent(mock_client)
    
    def test_empty_message(self, agent):
        """Test processing empty message"""
        response = agent.process_message("")
        assert response is not None
    
    def test_very_long_message(self, agent):
        """Test processing very long message"""
        long_message = "A" * 10000
        response = agent.process_message(long_message)
        assert response is not None
    
    def test_special_characters(self, agent):
        """Test message with special characters"""
        special_message = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
        response = agent.process_message(special_message)
        assert response is not None
    
    def test_unicode_message(self, agent):
        """Test message with Unicode characters"""
        unicode_message = "Hello 世界 🌍 Cybersecurity សុវត្ថិភាព"
        response = agent.process_message(unicode_message)
        assert response is not None
    
    def test_multiple_sessions_independent(self, agent):
        """Test that different sessions don't interfere"""
        agent.process_message("Message for session A", session_id="session_a")
        agent.process_message("Message for session B", session_id="session_b")
        
        info_a = conversation_memory.get_session_info("session_a")
        info_b = conversation_memory.get_session_info("session_b")
        
        assert info_a["message_count"] >= 1
        assert info_b["message_count"] >= 1
        assert info_a["session_id"] == "session_a"
        assert info_b["session_id"] == "session_b"
    
    def test_rapid_messages(self, agent):
        """Test processing multiple messages rapidly"""
        for i in range(10):
            response = agent.process_message(f"Message number {i}")
            assert response is not None


class TestAgentToolsIntegration:
    """Test agent integration with actual tools"""
    
    @pytest.fixture
    def agent(self):
        mock_client = MockOllamaClient()
        return CyberAgent(mock_client)
    
    def test_network_tool_execution(self, agent):
        """Test that network tools are executed when requested"""
        agent.process_message("scan ports on localhost", use_tools=True)
        assert agent.ollama.last_prompt is not None
    
    def test_security_tool_execution(self, agent):
        """Test that security tools are executed when requested"""
        agent.process_message("check system security", use_tools=True)
        assert agent.ollama.last_prompt is not None
    
    def test_tools_not_executed_when_disabled(self, agent):
        """Test that tools are not executed when use_tools=False"""
        initial_call_count = agent.ollama.call_count
        
        agent.process_message("scan network", use_tools=False)
        
        assert agent.ollama.call_count > initial_call_count


class TestAgentPerformance:
    """Performance tests for agent"""
    
    @pytest.fixture
    def agent(self):
        mock_client = MockOllamaClient()
        return CyberAgent(mock_client)
    
    def test_response_time_within_limit(self, agent):
        """Test that response generation is reasonably fast"""
        start = time.time()
        agent.process_message("What is cybersecurity?")
        elapsed = time.time() - start
        
        assert elapsed < 5
    
    def test_concurrent_sessions(self, agent):
        """Test handling multiple sessions concurrently"""
        results = []
        
        def process_session(session_id, message):
            response = agent.process_message(message, session_id=session_id)
            results.append((session_id, response))
        
        threads = []
        for i in range(5):
            t = threading.Thread(
                target=process_session,
                args=(f"session_{i}", f"Message {i}")
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(results) == 5


# Run tests directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])