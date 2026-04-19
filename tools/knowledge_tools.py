"""
Knowledge Tools Module - Provides functions for searching and managing
the knowledge base from within the AI agent and API endpoints
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from ai_core.memory import knowledge_base
from logger import logger


def search_knowledge(query: str, n_results: int = 3) -> str:
    """
    Search the knowledge base for relevant information
    
    Args:
        query: Search query string
        n_results: Number of results to return
    
    Returns:
        Formatted string with search results
    """
    try:
        # Search with metadata
        results = knowledge_base.search_with_metadata(query, n_results)
        
        if not results:
            return "+ No relevant information found in the knowledge base.\n\n * Tip: You can add new knowledge using the `/add_knowledge` command."
        
        # Format results
        output = f"+ **Knowledge Base Search Results** (Top {len(results)})\n\n"
        
        for i, result in enumerate(results, 1):
            # Calculate relevance score (distance to relevance)
            relevance = 1 - result.get('distance', 0)
            relevance_percent = int(relevance * 100)
            
            # Relevance indicator
            if relevance_percent > 80:
                relevance_icon = "#"
            elif relevance_percent > 60:
                relevance_icon = "#"
            else:
                relevance_icon = "#"
            
            output += f"{i}. {relevance_icon} **Relevance: {relevance_percent}%**\n"
            output += f"   + {result['text'][:300]}"
            if len(result['text']) > 300:
                output += "..."
            output += f"\n"
            
            # Add metadata if available
            if result.get('metadata'):
                meta = result['metadata']
                if 'topic' in meta:
                    output += f"   + Topic: {meta['topic']}\n"
                if 'type' in meta:
                    output += f"   + Type: {meta['type']}\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return f"+ Error searching knowledge base: {str(e)}"


def search_knowledge_json(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search knowledge base and return JSON results (for API use)
    
    Args:
        query: Search query string
        n_results: Number of results to return
    
    Returns:
        List of dictionaries with search results
    """
    try:
        return knowledge_base.search_with_metadata(query, n_results)
    except Exception as e:
        logger.error(f"Error searching knowledge JSON: {e}")
        return []


def add_knowledge(text: str, topic: str = "general", metadata: Optional[Dict] = None) -> str:
    """
    Add new knowledge to the knowledge base
    
    Args:
        text: Knowledge text to add
        topic: Topic category (e.g., "phishing", "sql_injection", "network")
        metadata: Additional metadata as dictionary
    
    Returns:
        Success message with document ID
    """
    try:
        # Validate input
        if not text or len(text.strip()) < 10:
            return "+ Error: Knowledge text must be at least 10 characters long."
        
        if not topic:
            topic = "general"
        
        # Add to knowledge base
        doc_id = knowledge_base.add_knowledge(text, topic, metadata)
        
        if doc_id:
            return f"+ **Knowledge added successfully!**\n\n📄 ID: `{doc_id}`\n🏷️ Topic: `{topic}`\n📝 Content: {text[:100]}...\n\n💡 The AI will now use this information when answering relevant questions."
        else:
            return "+ Error: Failed to add knowledge. Please try again."
            
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        return f"+ Error adding knowledge: {str(e)}"


def delete_knowledge(doc_id: str) -> str:
    """
    Delete knowledge from the knowledge base
    
    Args:
        doc_id: Document ID to delete
    
    Returns:
        Success or error message
    """
    try:
        success = knowledge_base.delete_knowledge(doc_id)
        
        if success:
            return f"+ Knowledge with ID `{doc_id}` has been deleted successfully."
        else:
            return f"+ Error: Could not find knowledge with ID `{doc_id}`."
            
    except Exception as e:
        logger.error(f"Error deleting knowledge: {e}")
        return f"+ Error deleting knowledge: {str(e)}"


def get_knowledge_stats() -> str:
    """
    Get statistics about the knowledge base
    
    Returns:
        Formatted string with statistics
    """
    try:
        stats = knowledge_base.get_stats()
        
        if 'error' in stats:
            return f"+ Error getting stats: {stats['error']}"
        
        output = f"+ **Knowledge Base Statistics**\n\n"
        output += f"+ Total items: **{stats.get('total_items', 0)}**\n"
        output += f"+ Unique topics: **{stats.get('unique_topics', 0)}**\n"
        
        # Topic list
        topics = stats.get('topics', [])
        if topics:
            output += f"\n+ **Topics:**\n"
            for topic in topics[:10]:
                output += f"   • {topic}\n"
            if len(topics) > 10:
                output += f"   ... and {len(topics) - 10} more\n"
        
        # Type distribution
        type_dist = stats.get('type_distribution', {})
        if type_dist:
            output += f"\n+ **Content Types:**\n"
            for doc_type, count in type_dist.items():
                output += f"   • {doc_type}: {count}\n"
        
        output += f"\n+ Storage location: `{stats.get('persist_directory', 'unknown')}`"
        
        return output
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return f"+ Error getting knowledge stats: {str(e)}"


def get_all_topics() -> str:
    """
    Get all available topics in the knowledge base
    
    Returns:
        Formatted string with topics list
    """
    try:
        topics = knowledge_base.get_all_topics()
        
        if not topics:
            return "+ No topics found in knowledge base."
        
        output = f"+ **Available Topics** ({len(topics)})\n\n"
        for topic in topics:
            output += f"   • {topic}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Error getting topics: {e}")
        return f"+ Error getting topics: {str(e)}"


def clear_all_knowledge() -> str:
    """
    Clear all knowledge from the database (use with caution!)
    
    Returns:
        Warning and confirmation message
    """
    try:
        # Get count before clearing
        stats = knowledge_base.get_stats()
        count = stats.get('total_items', 0)
        
        if count == 0:
            return "+ Knowledge base is already empty."
        
        # Clear the database
        success = knowledge_base.clear_all()
        
        if success:
            return f"+ **Knowledge base cleared!**\n\nRemoved {count} items. The base knowledge has been reinitialized."
        else:
            return "+ Error clearing knowledge base."
            
    except Exception as e:
        logger.error(f"Error clearing knowledge: {e}")
        return f" + Error clearing knowledge base: {str(e)}"


def export_knowledge_to_json(filepath: str = "knowledge_export.json") -> str:
    """
    Export all knowledge to a JSON file
    
    Args:
        filepath: Path to save the JSON file
    
    Returns:
        Success message with file location
    """
    try:
        # Get all data from collection
        all_data = knowledge_base.collection.get()
        
        # Prepare export data
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_items": len(all_data['ids']),
            "items": []
        }
        
        for i in range(len(all_data['ids'])):
            export_data["items"].append({
                "id": all_data['ids'][i],
                "text": all_data['documents'][i],
                "metadata": all_data['metadatas'][i]
            })
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return f"+ Knowledge exported to `{filepath}`\n\n📊 Total items: {len(all_data['ids'])}"
        
    except Exception as e:
        logger.error(f"Error exporting knowledge: {e}")
        return f"+ Error exporting knowledge: {str(e)}"


def import_knowledge_from_json(filepath: str) -> str:
    """
    Import knowledge from a JSON file
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Success message with import count
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        for item in data.get('items', []):
            doc_id = knowledge_base.add_knowledge(
                text=item['text'],
                topic=item['metadata'].get('topic', 'imported'),
                metadata=item['metadata']
            )
            if doc_id:
                imported_count += 1
        
        return f"+ Imported {imported_count} items from `{filepath}`"
        
    except Exception as e:
        logger.error(f"Error importing knowledge: {e}")
        return f"+ Error importing knowledge: {str(e)}"


# Tool function mapping for easy access
KNOWLEDGE_TOOLS = {
    "search": search_knowledge,
    "add": add_knowledge,
    "delete": delete_knowledge,
    "stats": get_knowledge_stats,
    "topics": get_all_topics,
    "clear": clear_all_knowledge,
    "export": export_knowledge_to_json,
    "import": import_knowledge_from_json
}


def execute_knowledge_tool(tool_name: str, **kwargs) -> str:
    """
    Execute a knowledge tool by name
    
    Args:
        tool_name: Name of the tool to execute
        **kwargs: Arguments to pass to the tool
    
    Returns:
        Tool execution result
    """
    if tool_name not in KNOWLEDGE_TOOLS:
        return f"+ Unknown knowledge tool: {tool_name}\n\nAvailable tools: {', '.join(KNOWLEDGE_TOOLS.keys())}"
    
    try:
        tool_func = KNOWLEDGE_TOOLS[tool_name]
        return tool_func(**kwargs)
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return f"+ Error executing {tool_name}: {str(e)}"