"""
Unit tests for memory module (ChromaDB + SQLite)
Run with: pytest tests/test_memory.py -v
"""

import os
import sys
import pytest
import tempfile
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.memory import KnowledgeBase, ConversationMemory


class TestKnowledgeBase:
    """Test cases for KnowledgeBase (ChromaDB)"""
    
    @pytest.fixture
    def temp_kb(self):
        """Create temporary knowledge base for testing"""
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        kb = KnowledgeBase(persist_directory=temp_dir)
        yield kb
        # Cleanup
        shutil.rmtree(temp_dir)
    
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
        assert any("SQL" in r or "injection" in r for r in results)
    
    def test_search_with_metadata(self, temp_kb):
        """Test search that returns metadata"""
        results = temp_kb.search_with_metadata("phishing attack", n_results=2)
        assert results is not None
        assert len(results) > 0
        assert "metadata" in results[0]
        assert "text" in results[0]
    
    def test_add_knowledge(self, temp_kb):
        """Test adding new knowledge to database"""
        initial_count = temp_kb.collection.count()
        
        doc_id = temp_kb.add_knowledge(
            text="Test knowledge: This is a test entry for unit testing.",
            topic="testing",
            metadata={"source": "unit_test", "priority": "high"}
        )
        
        assert doc_id is not None
        assert len(doc_id) > 0
        assert temp_kb.collection.count() == initial_count + 1
        
        # Verify by searching
        results = temp_kb.search("test knowledge", n_results=1)
        assert len(results) > 0
    
    def test_delete_knowledge(self, temp_kb):
        """Test deleting knowledge from database"""
        # Add a test entry
        doc_id = temp_kb.add_knowledge(
            text="Test knowledge to delete",
            topic="testing"
        )
        
        initial_count = temp_kb.collection.count()
        
        # Delete it
        success = temp_kb.delete_knowledge(doc_id)
        assert success is True
        assert temp_kb.collection.count() == initial_count - 1
    
    def test_get_all_topics(self, temp_kb):
        """Test retrieving all topics"""
        topics = temp_kb.get_all_topics()
        assert topics is not None
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert "phishing" in topics or "sql_injection" in topics
    
    def test_get_stats(self, temp_kb):
        """Test getting database statistics"""
        stats = temp_kb.get_stats()
        assert stats is not None
        assert "total_items" in stats
        assert "unique_topics" in stats
        assert stats["total_items"] > 0
    
    def test_search_no_results(self, temp_kb):
        """Test search with no matching results"""
        results = temp_kb.search("xyzabc123nosuchterm456", n_results=2)
        # Should return empty list or very few results
        assert results is not None
    
    def test_multiple_searches(self, temp_kb):
        """Test multiple searches in sequence"""
        queries = ["password security", "network firewall", "encryption methods"]
        
        for query in queries:
            results = temp_kb.search(query, n_results=1)
            # Should not crash
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
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        shutil.rmtree(temp_dir)
    
    def test_add_message(self, temp_memory):
        """Test adding messages to conversation"""
        temp_memory.add_message("test_session", "user", "Hello, this is a test message")
        
        history = temp_memory.get_history("test_session")
        assert len(history) > 0
        assert history[0][0] == "user"
        assert "test message" in history[0][1]
    
    def test_get_history(self, temp_memory):
        """Test retrieving conversation history"""
        # Add multiple messages
        temp_memory.add_message("session1", "user", "First message")
        temp_memory.add_message("session1", "assistant", "First response")
        temp_memory.add_message("session1", "user", "Second message")
        
        history = temp_memory.get_history("session1")
        assert len(history) == 3
        assert history[0][0] == "user"
        assert history[0][1] == "First message"
        assert history[1][1] == "First response"
    
    def test_get_history_limit(self, temp_memory):
        """Test history limit parameter"""
        for i in range(10):
            temp_memory.add_message("session_limit", "user", f"Message {i}")
        
        history = temp_memory.get_history("session_limit", limit=5)
        assert len(history) == 5
        assert history[-1][1] == "Message 4"  # Last 5 messages
    
    def test_get_history_with_timestamps(self, temp_memory):
        """Test getting history with timestamps"""
        temp_memory.add_message("session_ts", "user", "Test message")
        
        history = temp_memory.get_history_with_timestamps("session_ts")
        assert len(history) > 0
        assert len(history[0]) == 3  # role, content, timestamp
        assert history[0][2] is not None
    
    def test_get_last_message(self, temp_memory):
        """Test getting the last message"""
        temp_memory.add_message("session_last", "user", "First")
        temp_memory.add_message("session_last", "assistant", "Second")
        temp_memory.add_message("session_last", "user", "Third")
        
        last = temp_memory.get_last_message("session_last")
        assert last is not None
        assert last[0] == "user"
        assert last[1] == "Third"
    
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
        assert info["session_id"] == "session_info"
        assert info["message_count"] == 2
        assert "created_at" in info
        assert "last_active" in info
    
    def test_list_sessions(self, temp_memory):
        """Test listing all sessions"""
        temp_memory.add_message("session_list1", "user", "Test1")
        temp_memory.add_message("session_list2", "user", "Test2")
        temp_memory.add_message("session_list1", "assistant", "Response")
        
        sessions = temp_memory.list_sessions(limit=10)
        assert len(sessions) >= 2
        
        session_ids = [s["session_id"] for s in sessions]
        assert "session_list1" in session_ids
        assert "session_list2" in session_ids
    
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
        shutil.rmtree(temp_dir)
    
    def test_knowledge_and_conversation_together(self, temp_memory_system):
        """Test using both systems together"""
        kb, conv = temp_memory_system
        
        # Add conversation
        conv.add_message("test", "user", "What is port scanning?")
        
        # Search knowledge
        knowledge = kb.search("port scanning", n_results=1)
        assert len(knowledge) > 0
        
        # Add assistant response
        conv.add_message("test", "assistant", knowledge[0] if knowledge else "No info")
        
        # Verify conversation saved
        history = conv.get_history("test")
        assert len(history) == 2
        assert "user" in history[0][0]
    
    def test_workflow_simulation(self, temp_memory_system):
        """Simulate real conversation workflow"""
        kb, conv = temp_memory_system
        
        # Simulate conversation
        user_questions = [
            "What is SQL injection?",
            "How to prevent XSS attacks?",
            "Explain 2FA"
        ]
        
        for question in user_questions:
            # Save user message
            conv.add_message("workflow", "user", question)
            
            # Search knowledge
            knowledge = kb.search(question, n_results=1)
            
            # Generate response (simulated)
            response = f"Based on knowledge: {knowledge[0][:100] if knowledge else 'No info'}"
            
            # Save assistant response
            conv.add_message("workflow", "assistant", response)
        
        # Verify all messages saved
        history = conv.get_history("workflow")
        assert len(history) == 6  # 3 questions + 3 responses


# Run tests directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])