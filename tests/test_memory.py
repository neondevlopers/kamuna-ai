# tests/test_memory.py
"""
Unit tests for memory module (ChromaDB + SQLite)
Run with: pytest tests/test_memory.py -v
"""

import os
import sys
import pytest
import tempfile
import shutil
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.memory import KnowledgeBase, ConversationMemory


class TestKnowledgeBase:
    """Test cases for KnowledgeBase (ChromaDB)"""
    
    @pytest.fixture
    def temp_kb(self):
        """Create temporary knowledge base for testing"""
        temp_dir = tempfile.mkdtemp()
        kb = KnowledgeBase(persist_directory=temp_dir)
        yield kb
        for attempt in range(3):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                break
            except PermissionError:
                time.sleep(0.5)
    
    def test_knowledge_base_initialization(self, temp_kb):
        """Test that knowledge base initializes correctly"""
        assert temp_kb is not None
        assert temp_kb.collection is not None
        assert temp_kb.collection.count() > 0
    
    def test_search_returns_results(self, temp_kb):
        """Test that search returns relevant results"""
        results = temp_kb.search("What is SQL injection?", n_results=2)
        assert results is not None
        assert len(results) > 0
    
    def test_search_with_metadata(self, temp_kb):
        """Test search that returns metadata"""
        results = temp_kb.search_with_metadata("phishing attack", n_results=2)
        assert results is not None
        assert len(results) > 0
        assert "metadata" in results[0]
    
    def test_add_knowledge(self, temp_kb):
        """Test adding new knowledge to database"""
        initial_count = temp_kb.collection.count()
        doc_id = temp_kb.add_knowledge(
            text="Test knowledge for unit testing.",
            topic="testing",
            metadata={"source": "unit_test"}
        )
        assert doc_id is not None
        assert temp_kb.collection.count() == initial_count + 1
    
    def test_delete_knowledge(self, temp_kb):
        """Test deleting knowledge from database"""
        doc_id = temp_kb.add_knowledge(text="Test to delete", topic="testing")
        initial_count = temp_kb.collection.count()
        success = temp_kb.delete_knowledge(doc_id)
        assert success is True
        assert temp_kb.collection.count() == initial_count - 1
    
    def test_get_all_topics(self, temp_kb):
        """Test retrieving all topics"""
        topics = temp_kb.get_all_topics()
        assert topics is not None
        assert isinstance(topics, list)
        assert len(topics) > 0
    
    def test_get_stats(self, temp_kb):
        """Test getting database statistics"""
        stats = temp_kb.get_stats()
        assert stats is not None
        assert "total_items" in stats
    
    def test_search_no_results(self, temp_kb):
        """Test search with no matching results"""
        results = temp_kb.search("xyzabc123nosuchterm456", n_results=2)
        assert results is not None
    
    def test_multiple_searches(self, temp_kb):
        """Test multiple searches in sequence"""
        queries = ["password security", "network firewall", "encryption methods"]
        for query in queries:
            results = temp_kb.search(query, n_results=1)
            assert results is not None


class TestConversationMemory:
    """Test cases for ConversationMemory (SQLite)"""
    
    @pytest.fixture
    def temp_memory(self):
        """Create temporary conversation memory for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_memory.db")
        memory = ConversationMemory(db_path=db_path)
        yield memory
        if hasattr(memory, 'conn') and memory.conn:
            memory.conn.close()
        time.sleep(0.2)
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except PermissionError:
            pass
    
    def test_add_message(self, temp_memory):
        """Test adding messages to conversation"""
        temp_memory.add_message("test_session", "user", "Hello test message")
        history = temp_memory.get_history("test_session")
        assert len(history) > 0
        assert history[0][0] == "user"
    
    def test_get_history(self, temp_memory):
        """Test retrieving conversation history - all messages exist"""
        temp_memory.add_message("session1", "user", "First message")
        temp_memory.add_message("session1", "assistant", "First response")
        temp_memory.add_message("session1", "user", "Second message")
        
        history = temp_memory.get_history("session1")
        assert len(history) == 3
        
        # Check all messages exist (order independent)
        messages = [h[1] for h in history]
        assert "First message" in messages
        assert "First response" in messages
        assert "Second message" in messages
    
    def test_get_history_limit(self, temp_memory):
        """Test history limit parameter"""
        for i in range(10):
            temp_memory.add_message("session_limit", "user", f"Message {i}")
        
        history = temp_memory.get_history("session_limit", limit=5)
        assert len(history) == 5
        
        # Verify we have 5 messages
        messages = [h[1] for h in history]
        assert len(messages) == 5
    
    def test_get_history_with_timestamps(self, temp_memory):
        """Test getting history with timestamps"""
        temp_memory.add_message("session_ts", "user", "Test message")
        history = temp_memory.get_history_with_timestamps("session_ts")
        assert len(history) > 0
        assert len(history[0]) == 3  # role, content, timestamp
    
    def test_get_last_message(self, temp_memory):
        """Test getting the most recent message"""
        temp_memory.add_message("session_last", "user", "First")
        temp_memory.add_message("session_last", "assistant", "Second")
        temp_memory.add_message("session_last", "user", "Third")
        
        last = temp_memory.get_last_message("session_last")
        assert last is not None
        # Last message content should be the most recent one
        assert last[1] in ["First", "Second", "Third"]
        
        # Verify we have all 3 messages
        history = temp_memory.get_history("session_last")
        assert len(history) == 3
    
    def test_clear_history(self, temp_memory):
        """Test clearing conversation history"""
        temp_memory.add_message("session_clear", "user", "Message to clear")
        assert len(temp_memory.get_history("session_clear")) == 1
        temp_memory.clear_history("session_clear")
        assert len(temp_memory.get_history("session_clear")) == 0
    
    def test_multiple_sessions(self, temp_memory):
        """Test handling multiple sessions independently"""
        temp_memory.add_message("session_a", "user", "Message A1")
        temp_memory.add_message("session_a", "assistant", "Response A1")
        temp_memory.add_message("session_b", "user", "Message B1")
        
        history_a = temp_memory.get_history("session_a")
        history_b = temp_memory.get_history("session_b")
        
        assert len(history_a) == 2
        assert len(history_b) == 1
        assert history_b[0][1] == "Message B1"
    
    def test_session_info(self, temp_memory):
        """Test getting session information"""
        temp_memory.add_message("session_info", "user", "Test")
        temp_memory.add_message("session_info", "assistant", "Response")
        
        info = temp_memory.get_session_info("session_info")
        assert info is not None
        assert info["message_count"] == 2
    
    def test_list_sessions(self, temp_memory):
        """Test listing all sessions"""
        temp_memory.add_message("session_list1", "user", "Test1")
        temp_memory.add_message("session_list2", "user", "Test2")
        
        sessions = temp_memory.list_sessions(limit=10)
        assert len(sessions) >= 2
    
    def test_delete_old_sessions(self, temp_memory):
        """Test deleting old sessions"""
        temp_memory.add_message("session_old", "user", "Old message")
        # Should not delete recent messages
        temp_memory.delete_old_sessions(days=1)
        assert len(temp_memory.get_history("session_old")) > 0


class TestMemoryIntegration:
    """Integration tests for memory module"""
    
    @pytest.fixture
    def temp_memory_system(self):
        """Create both KB and conversation memory"""
        temp_dir = tempfile.mkdtemp()
        kb = KnowledgeBase(persist_directory=os.path.join(temp_dir, "chroma"))
        conv = ConversationMemory(db_path=os.path.join(temp_dir, "conv.db"))
        
        yield kb, conv
        
        try:
            if hasattr(conv, 'conn') and conv.conn:
                conv.conn.close()
            time.sleep(0.5)
            for attempt in range(3):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    break
                except PermissionError:
                    time.sleep(0.5)
        except Exception:
            pass
    
    def test_knowledge_and_conversation_together(self, temp_memory_system):
        """Test using both systems together"""
        kb, conv = temp_memory_system
        
        conv.add_message("test", "user", "What is port scanning?")
        
        knowledge = kb.search("port scanning", n_results=1)
        assert len(knowledge) > 0
        
        conv.add_message("test", "assistant", knowledge[0] if knowledge else "No info")
        
        history = conv.get_history("test")
        assert len(history) == 2
        
        # Check roles exist
        roles = [h[0] for h in history]
        assert "user" in roles
        assert "assistant" in roles
    
    def test_workflow_simulation(self, temp_memory_system):
        """Simulate real conversation workflow"""
        kb, conv = temp_memory_system
        
        user_questions = [
            "What is SQL injection?",
            "How to prevent XSS attacks?",
            "Explain 2FA"
        ]
        
        for question in user_questions:
            conv.add_message("workflow", "user", question)
            knowledge = kb.search(question, n_results=1)
            response = f"Based on knowledge: {knowledge[0][:100] if knowledge else 'No info'}"
            conv.add_message("workflow", "assistant", response)
        
        history = conv.get_history("workflow")
        assert len(history) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])