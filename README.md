# Kamuna AI 

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![Ollama](https://img.shields.io/badge/Ollama-0.1.0-orange.svg)](https://ollama.ai)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.22-purple.svg)](https://chromadb.com)
[![Tests](https://img.shields.io/badge/tests-32%20passing-brightgreen.svg)](https://pytest.org)

> **An intelligent AI-powered Cyber Security Assistant with local LLM, knowledge base, and security tools.**

---

## **Project Overview & Capabilities**

## Core Technical Architecture

![App Screenshot](Kamuna/Kamuna1.png)


The system is built on a robust, modular stack that combines modern AI techniques with traditional security tools and web frameworks.

AI Core: Powered by DeepSeek Coder integrated with Ollama for efficient local execution.

Knowledge Base: Utilizes ChromaDB for vector storage and semantic search capabilities.

Memory Management: Employs SQLite to maintain persistent conversation history and session data.

Security Infrastructure: Integrates multiple layers, including Network analysis, System process monitoring, and Log analysis.

Web Interface: A lightweight frontend built with Flask (Python), utilizing standard web technologies (HTML/CSS/JS).

Quality Assurance: The project maintains high code reliability with a 100% test coverage suite utilizing Pytest (32 test cases).

## Functional Capabilities

![App Screenshot](Kamuna/Kamuna2.png)

The system is designed to handle complex security and analytical workflows through six distinct categories:

Network: Conducts automated network reconnaissance, including port scanning, identifying open ports, and providing security analysis.

Security: Performs active host protection through firewall status checks, antivirus verification, and real-time process monitoring.

Logs: Provides forensic analysis, including detecting failed login attempts, brute force attack identification, and pattern recognition for malicious activity.

Files: Implements safe file handling, sensitive data detection, and comprehensive metadata extraction.

AI: Features an advanced reasoning engine that supports local LLM inference, Retrieval-Augmented Generation (RAG), conversation memory, and automated tool calling.

Knowledge: Enables rapid information retrieval via vector search and semantic understanding, supporting over 15 distinct subject domains.

## AI Model Portfolio & Resource Allocation

![App Screenshot](Kamuna/Kamuna3.png)

The system offers flexibility in choosing an AI model, allowing users to balance performance with hardware constraints (RAM and storage):

Model,Size,RAM Required,Performance,Quality
TinyLlama 1.1B,1.1B,2GB,Very Fast,⭐⭐
DeepSeek Coder 1.3B,1.3B,2-3GB,Fast,⭐⭐⭐
DeepSeek Coder 6.7B,6.7B,6-8GB,Medium,⭐⭐⭐⭐
CodeLlama 7B,7B,8GB,Medium,⭐⭐⭐⭐
Qwen2.5-Coder 7B,7B,8GB,Medium,⭐⭐⭐⭐⭐

## Operational Metrics & Benchmarks

![App Screenshot](Kamuna/Kamuna4.png)

The system is optimized for low-latency operations and scalable deployment:

Response Latency:

Local Execution: Optimized at 1–5 seconds.

Colab Environment: 5–15 seconds, depending on cloud overhead.

Knowledge Search: Sub-100ms response time.

Footprint:

Memory Usage: Operates efficiently within 2–8 GB of RAM.

Storage: Base storage requirement is ~500 MB, with additional space allocated for models (3–20 GB).

Extensibility: The system is highly extensible, currently supporting 15+ dedicated tools and 15+ base knowledge items.

## License

MIT License - Free for educational and commercial use.

## Acknowledgments

[Ollama](https://ollama.com/) - Local LLM runtime

[Deepseek](https://www.deepseek.com/) - Code-specialized models

[ChromaDB](https://docs.trychroma.com/) - Vector database

## Contact
 
[GitHub](neondevlopers/kamuna-ai) 

[Issues](https://github.com/neondevlopers/kamuna-ai/issues) 

[Gmail](menmengleapx1@gmail.com)

LangChain - LLM framework

