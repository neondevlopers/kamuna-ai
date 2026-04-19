# ai_core/memory.py
import chromadb
from chromadb.utils import embedding_functions
import sqlite3
import os
import uuid

class KnowledgeBase:
    """Control ChromaDB"""
    
    def __init__(self):
        # folder
        os.makedirs("memory_db/chroma_db", exist_ok=True)
        
        #  ChromaDB
        self.client = chromadb.PersistentClient(path="memory_db/chroma_db")
        
        # collection
        self.collection = self.client.get_or_create_collection(
            name="cyber_knowledge",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )
        
        if self.collection.count() == 0:
            self._init_base_knowledge()
    
    def _init_base_knowledge(self):
        """Add Data"""
        base_knowledge = [
            {
                "id": "kb_001",
                "text": "Phishing is a cyber attack where attackers send fake emails pretending to be from legitimate companies to steal sensitive information like passwords and credit card details.",
                "metadata": {"topic": "phishing", "type": "attack"}
            },
            {
                "id": "kb_002", 
                "text": "SQL injection is a code injection technique that attackers use to insert malicious SQL statements into input fields to manipulate databases.",
                "metadata": {"topic": "sql_injection", "type": "vulnerability"}
            },
            {
                "id": "kb_003",
                "text": "Two-Factor Authentication (2FA) adds an extra layer of security by requiring not just a password but also a second factor like a code from your phone.",
                "metadata": {"topic": "2fa", "type": "defense"}
            },
            {
                "id": "kb_004",
                "text": "Port scanning is a technique used to identify open ports on a network. Common tools include Nmap. Example: 'nmap -p 1-1000 target.com'",
                "metadata": {"topic": "port_scanning", "type": "technique"}
            },
            {
                "id": "kb_005",
                "text": "Ethical hacking (white hat) is authorized testing of systems to find vulnerabilities before malicious hackers can exploit them. Always get written permission before testing.",
                "metadata": {"topic": "ethical_hacking", "type": "practice"}
            },
            {
                "id": "kb_006",
                "text": "Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users. Prevention includes input validation and output encoding.",
                "metadata": {"topic": "xss", "type": "vulnerability"}
            },
            {
                "id": "kb_007",
                "text": "A firewall monitors and filters network traffic based on security rules. Use 'sudo ufw enable' on Ubuntu to enable firewall.",
                "metadata": {"topic": "firewall", "type": "defense"}
            },
            {
                "id": "kb_008",
                "text": "Password best practices: Use at least 12 characters, include uppercase, lowercase, numbers, and symbols. Never reuse passwords across sites. Use a password manager.",
                "metadata": {"topic": "password", "type": "best_practice"}
            },
            {
                "id": "kb_009",
                "text": "DDoS (Distributed Denial of Service) attack floods a server with traffic to make it unavailable. Protection includes rate limiting and using CDN services.",
                "metadata": {"topic": "ddos", "type": "attack"}
            },
            {
                "id": "kb_010",
                "text": "Man-in-the-Middle (MITM) attack occurs when an attacker intercepts communication between two parties. Use HTTPS and VPN to prevent MITM attacks.",
                "metadata": {"topic": "mitm", "type": "attack"}
            }
        ]
        
        for item in base_knowledge:
            self.collection.add(
                documents=[item["text"]],
                metadatas=[item["metadata"]],
                ids=[item["id"]]
            )
        print(f"+ Added {len(base_knowledge)} base knowledge items")
    
    def search(self, query, n_results=3):
        """Find Info"""
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        return documents, metadatas, distances
    
    def add_knowledge(self, text, topic, metadata=None):
        """Add"""
        doc_id = f"kb_{uuid.uuid4().hex[:8]}"
        
        meta = {"topic": topic, "type": "user_added"}
        if metadata:
            meta.update(metadata)
        
        self.collection.add(
            documents=[text],
            metadatas=[meta],
            ids=[doc_id]
        )
        return doc_id
    
    def get_all_topics(self):
        """ទទួលបាន topics ទាំងអស់"""
        all_data = self.collection.get()
        topics = set()
        for meta in all_data['metadatas']:
            if meta and 'topic' in meta:
                topics.add(meta['topic'])
        return list(topics)
    
    def delete_knowledge(self, doc_id):
        """Delete"""
        self.collection.delete(ids=[doc_id])
        return True

class ConversationMemory:
    """Save Message"""
    
    def __init__(self):
        os.makedirs("memory_db", exist_ok=True)
        self.conn = sqlite3.connect("memory_db/sqlite.db", check_same_thread=False)
        self._init_table()
    
    def _init_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def add_message(self, session_id, role, content):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        self.conn.commit()
    
    def get_history(self, session_id, limit=5):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        return list(reversed(rows))
    
    def clear_history(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        self.conn.commit()

# instance
knowledge_base = KnowledgeBase()
conversation_memory = ConversationMemory()