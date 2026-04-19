# tools/knowledge_tools.py
from ai_core.memory import knowledge_base

def search_knowledge(query):
    """ knowledge base"""
    documents, metadatas, distances = knowledge_base.search(query, n_results=3)
    
    if not documents:
        return "No relevant information found in knowledge base."
    
    output = "+ **Relevant Information Found:**\n\n"
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        output += f"{i}. {doc}\n"
        output += f"   Topic: {meta.get('topic', 'unknown')}\n"
        output += f"   Relevance: {round(1 - dist, 2)}\n\n"
    
    return output

def get_all_topics():
    """ topics """
    topics = knowledge_base.get_all_topics()
    return f"Available topics: {', '.join(topics)}"

def add_new_knowledge(text, topic):
    """Add New"""
    doc_id = knowledge_base.add_knowledge(text, topic)
    return f"Added new knowledge with ID: {doc_id}"

def get_stats():
    """Got"""
    count = knowledge_base.collection.count()
    topics = knowledge_base.get_all_topics()
    return f"Total: {count} items | Topics: {len(topics)}"