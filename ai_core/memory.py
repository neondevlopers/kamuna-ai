# ai_core/memory.py
"""
Memory Module - Manages knowledge base and conversation history
Uses ChromaDB for vector search and SQLite for conversation memory
"""

import os
import sys
import sqlite3
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions

# Fix import for Colab and local environments
try:
    from backend.logger import logger
except ImportError:
    try:
        from logger import logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.warning("Using fallback logging configuration")


class KnowledgeBase:
    """
    Vector database for storing and retrieving cybersecurity knowledge
    Uses ChromaDB with semantic search capabilities
    """
    
    def __init__(self, persist_directory: str = "memory_db/chroma_db"):
        """
        Initialize the knowledge base
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name="cyber_knowledge",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )
        
        # Initialize with base knowledge if empty
        if self.collection.count() == 0:
            self._init_base_knowledge()
            logger.info(f"Initialized knowledge base with {self.collection.count()} items")
        else:
            logger.info(f"Loaded knowledge base with {self.collection.count()} items")
    
    def _init_base_knowledge(self):
        """Initialize knowledge base with core cybersecurity information"""
        
        base_knowledge = [
            {
                "id": "kb_001",
                "text": "Phishing is a cyber attack where attackers send fake emails pretending to be from legitimate companies to steal sensitive information like passwords and credit card details. Prevention: Check sender email, don't click suspicious links, use email filters.",
                "metadata": {"topic": "phishing", "type": "attack", "difficulty": "beginner"}
            },
            {
                "id": "kb_002", 
                "text": "SQL injection is a code injection technique that attackers use to insert malicious SQL statements into input fields to manipulate databases. Prevention: Use parameterized queries, input validation, and prepared statements.",
                "metadata": {"topic": "sql_injection", "type": "vulnerability", "difficulty": "intermediate"}
            },
            {
                "id": "kb_003",
                "text": "Two-Factor Authentication (2FA) adds an extra layer of security by requiring not just a password but also a second factor like a code from your phone. Types: SMS codes, authenticator apps, biometrics, hardware tokens.",
                "metadata": {"topic": "2fa", "type": "defense", "difficulty": "beginner"}
            },
            {
                "id": "kb_004",
                "text": "Port scanning is a technique used to identify open ports on a network. Common tools include Nmap. Example: 'nmap -p 1-1000 target.com' for TCP scan, 'nmap -sU target.com' for UDP scan. Only scan systems you own or have permission to test.",
                "metadata": {"topic": "port_scanning", "type": "technique", "difficulty": "beginner"}
            },
            {
                "id": "kb_005",
                "text": "Ethical hacking (white hat) is authorized testing of systems to find vulnerabilities before malicious hackers can exploit them. Steps: 1) Get written permission, 2) Define scope, 3) Report findings, 4) Never disclose vulnerabilities publicly without consent.",
                "metadata": {"topic": "ethical_hacking", "type": "practice", "difficulty": "intermediate"}
            },
            {
                "id": "kb_006",
                "text": "Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users. Types: Reflected XSS, Stored XSS, DOM-based XSS. Prevention: Input validation, output encoding, Content Security Policy (CSP).",
                "metadata": {"topic": "xss", "type": "vulnerability", "difficulty": "intermediate"}
            },
            {
                "id": "kb_007",
                "text": "A firewall monitors and filters network traffic based on security rules. Commands: 'sudo ufw enable' on Ubuntu, 'firewall-cmd --list-all' on CentOS, 'netsh advfirewall' on Windows. Types: Network firewalls, host-based firewalls, next-generation firewalls.",
                "metadata": {"topic": "firewall", "type": "defense", "difficulty": "beginner"}
            },
            {
                "id": "kb_008",
                "text": "Password best practices: Use at least 12 characters, include uppercase, lowercase, numbers, and symbols. Never reuse passwords across sites. Use a password manager like Bitwarden or KeePass. Enable 2FA whenever possible.",
                "metadata": {"topic": "password", "type": "best_practice", "difficulty": "beginner"}
            },
            {
                "id": "kb_009",
                "text": "DDoS (Distributed Denial of Service) attack floods a server with traffic to make it unavailable. Types: Volume-based, protocol attacks, application layer. Protection: Rate limiting, CDN services, cloud DDoS protection like Cloudflare.",
                "metadata": {"topic": "ddos", "type": "attack", "difficulty": "intermediate"}
            },
            {
                "id": "kb_010",
                "text": "Man-in-the-Middle (MITM) attack occurs when an attacker intercepts communication between two parties. Prevention: Use HTTPS, VPN, avoid public Wi-Fi for sensitive transactions, verify SSL certificates, use WPA3 for Wi-Fi.",
                "metadata": {"topic": "mitm", "type": "attack", "difficulty": "intermediate"}
            },
            {
                "id": "kb_011",
                "text": "Python socket programming for port scanning: import socket; sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(1); result = sock.connect_ex(('target', port)); return result == 0",
                "metadata": {"topic": "python", "type": "code", "difficulty": "beginner"}
            },
            {
                "id": "kb_012",
                "text": "Nmap is a network scanning tool. Common commands: 'nmap -sV target' (version detection), 'nmap -sS target' (stealth SYN scan), 'nmap -A target' (OS detection), 'nmap -p- target' (all ports). Always get permission before scanning.",
                "metadata": {"topic": "nmap", "type": "tool", "difficulty": "beginner"}
            },
            {
                "id": "kb_013",
                "text": "Metasploit Framework is a penetration testing tool. Basic usage: 'msfconsole' to start, 'search vulnerability' to find exploits, 'use exploit/path' to select, 'set RHOSTS target', 'run' to execute. Only use on authorized systems.",
                "metadata": {"topic": "metasploit", "type": "tool", "difficulty": "advanced"}
            },
            {
                "id": "kb_014",
                "text": "Wireshark is a network protocol analyzer. Use for: capturing packets, filtering traffic with display filters like 'http' or 'tcp.port==80', analyzing network issues, detecting suspicious traffic patterns.",
                "metadata": {"topic": "wireshark", "type": "tool", "difficulty": "intermediate"}
            },
            {
                "id": "kb_015",
                "text": "Incident response steps: 1) Preparation - have a plan, 2) Identification - detect the breach, 3) Containment - stop the attack, 4) Eradication - remove the threat, 5) Recovery - restore systems, 6) Lessons learned - improve security.",
                "metadata": {"topic": "incident_response", "type": "process", "difficulty": "advanced"}
            }
        ]
        
        try:
            for item in base_knowledge:
                self.collection.add(
                    documents=[item["text"]],
                    metadatas=[item["metadata"]],
                    ids=[item["id"]]
                )
            logger.info(f"Added {len(base_knowledge)} base knowledge items")
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
    
    def search(self, query: str, n_results: int = 3) -> List[str]:
        """
        Search for relevant information in the knowledge base
        
        Args:
            query: Search query string
            n_results: Number of results to return
        
        Returns:
            List of relevant document texts
        """
        try:
            if self.collection.count() == 0:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = results['documents'][0] if results['documents'] else []
            return documents
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def search_with_metadata(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for information and return with metadata
        
        Args:
            query: Search query string
            n_results: Number of results to return
        
        Returns:
            List of dictionaries with text, metadata, and distance
        """
        try:
            if self.collection.count() == 0:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            items = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    items.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 1.0
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Error searching with metadata: {e}")
            return []
    
    def add_knowledge(self, text: str, topic: str, metadata: Optional[Dict] = None) -> str:
        """
        Add new knowledge to the knowledge base
        
        Args:
            text: Knowledge text to add
            topic: Topic category
            metadata: Additional metadata
        
        Returns:
            ID of the added document
        """
        try:
            doc_id = f"kb_{uuid.uuid4().hex[:12]}"
            
            meta = {
                "topic": topic,
                "type": "user_added",
                "timestamp": datetime.now().isoformat(),
                "source": "user"
            }
            if metadata:
                meta.update(metadata)
            
            self.collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.info(f"Added knowledge: {doc_id} - {topic}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            return ""
    
    def delete_knowledge(self, doc_id: str) -> bool:
        """
        Delete knowledge from the knowledge base
        
        Args:
            doc_id: ID of document to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted knowledge: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting knowledge: {e}")
            return False
    
    def get_all_topics(self) -> List[str]:
        """
        Get all unique topics in the knowledge base
        
        Returns:
            List of topic strings
        """
        try:
            all_data = self.collection.get()
            topics = set()
            
            for meta in all_data['metadatas']:
                if meta and 'topic' in meta:
                    topics.add(meta['topic'])
            
            return sorted(list(topics))
            
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base
        
        Returns:
            Dictionary with statistics
        """
        try:
            topics = self.get_all_topics()
            all_data = self.collection.get()
            
            # Count items by type
            type_counts = {}
            for meta in all_data['metadatas']:
                if meta and 'type' in meta:
                    doc_type = meta['type']
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            return {
                'total_items': self.collection.count(),
                'unique_topics': len(topics),
                'topics': topics[:10],
                'type_distribution': type_counts,
                'persist_directory': self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}
    
    def clear_all(self) -> bool:
        """
        Clear all knowledge from the database (use with caution!)
        
        Returns:
            True if successful
        """
        try:
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
            
            self._init_base_knowledge()
            
            logger.warning("Knowledge base cleared and reinitialized")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {e}")
            return False


class ConversationMemory:
    """
    SQLite-based storage for conversation history
    Persists chat messages per session
    """
    
    def __init__(self, db_path: str = "memory_db/sqlite.db"):
        """
        Initialize conversation memory
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database connection
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
        
        logger.info(f"Conversation memory initialized at {db_path}")
    
    def _init_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_timestamp 
            ON conversations(session_id, timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO conversations (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                (session_id, role, content, str(metadata) if metadata else None)
            )
            
            cursor.execute('''
                INSERT INTO sessions (session_id, message_count, last_active)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    message_count = message_count + 1,
                    last_active = CURRENT_TIMESTAMP
            ''', (session_id,))
            
            self.conn.commit()
            logger.debug(f"Added {role} message to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            self.conn.rollback()
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Tuple[str, str]]:
        """Get conversation history for a session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT role, content 
                FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            return rows
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def get_history_with_timestamps(self, session_id: str, limit: int = 10) -> List[Tuple[str, str, str]]:
        """Get conversation history with timestamps"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT role, content, timestamp 
                FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (session_id, limit))
            
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting history with timestamps: {e}")
            return []
    
    def get_last_message(self, session_id: str) -> Optional[Tuple[str, str]]:
        """Get the most recent message in a session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT role, content 
                FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (session_id,))
            
            row = cursor.fetchone()
            return row if row else None
            
        except Exception as e:
            logger.error(f"Error getting last message: {e}")
            return None
    
    def clear_history(self, session_id: str):
        """Clear all conversation history for a session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self.conn.commit()
            
            logger.info(f"Cleared history for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            self.conn.rollback()
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT session_id, created_at, last_active, message_count 
                FROM sessions 
                WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row[0],
                    'created_at': row[1],
                    'last_active': row[2],
                    'message_count': row[3]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List all sessions with their information"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT session_id, created_at, last_active, message_count 
                FROM sessions 
                ORDER BY last_active DESC 
                LIMIT ?
            ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'created_at': row[1],
                    'last_active': row[2],
                    'message_count': row[3]
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []
    
    def delete_old_sessions(self, days: int = 30):
        """Delete sessions older than specified days"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            cursor.execute('''
                DELETE FROM sessions 
                WHERE last_active < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            self.conn.commit()
            logger.info(f"Deleted sessions older than {days} days")
            
        except Exception as e:
            logger.error(f"Error deleting old sessions: {e}")
            self.conn.rollback()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Create global instances for easy import
knowledge_base = KnowledgeBase()
conversation_memory = ConversationMemory()

logger.info("Memory module initialized successfully")