# cli.py
"""
KAMUNA AI - Command Line Interface
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.ollama_client import OllamaClient
from ai_core.agent import CyberAgent
from ai_core.memory import knowledge_base, conversation_memory


def print_banner():
    """Print welcome banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      ██╗  ██╗ █████╗ ███╗   ███╗██╗   ██╗███╗   ██╗ █████╗       ║
║      ██║ ██╔╝██╔══██╗████╗ ████║██║   ██║████╗  ██║██╔══██╗      ║
║      █████╔╝ ███████║██╔████╔██║██║   ██║██╔██╗ ██║███████║      ║
║      ██╔═██╗ ██╔══██║██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══██║      ║
║      ██║  ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║  ██║      ║
║      ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝      ║
║                                      Models : Kamuna CLI I       ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(" Type 'exit' or 'quit' to stop")
    print(" Type 'clear' to clear screen")
    print(" Type 'tools on/off' to enable/disable security tools")
    print(" Type 'session info' to view session info")
    print(" Type 'knowledge stats' to view knowledge base stats")
    print("-" * 70)


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_help():
    """Print help menu"""
    help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                         COMMAND HELP                          
╠══════════════════════════════════════════════════════════════════╣
║                                                                  
║   exit / quit      - Exit the application                        
║   clear            - Clear screen                                
║   help             - Show this help menu                         
║   tools on         - Enable security tools                       
║   tools off        - Disable security tools                      
║   session info     - Show current session info                   
║   session clear    - Clear conversation history                  
║   knowledge stats  - Show knowledge base statistics              
║   knowledge topics - List all topics in knowledge base          
║   model info       - Show current model information              
║                                                                  
╚══════════════════════════════════════════════════════════════════╝
    """
    print(help_text)


def main():
    """Main CLI loop"""
    # Initialize
    print(" Initializing AI Agent...")
    ollama_client = OllamaClient()
    agent = CyberAgent(ollama_client)
    
    clear_screen()
    print_banner()
    
    tools_enabled = True
    
    print("\n Kamuna is ready! Ask me anything about cybersecurity.\n")
    
    while True:
        try:
            # Get user input
            user_input = input(" You: ").strip()
            
            # Check for empty input
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n Goodbye! Stay secure!")
                break
            
            # Check for clear command
            elif user_input.lower() == 'clear':
                clear_screen()
                print_banner()
                continue
            
            # Check for help command
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            # Check for tools on/off
            elif user_input.lower() == 'tools on':
                tools_enabled = True
                agent.tools_enabled = True
                print(" Security tools: ENABLED")
                continue
            elif user_input.lower() == 'tools off':
                tools_enabled = False
                agent.tools_enabled = False
                print(" Security tools: DISABLED")
                continue
            
            # Check for session info
            elif user_input.lower() == 'session info':
                info = agent.get_session_info()
                print(f"\n Session Information")
                print(f"   Session ID: {info['session_id']}")
                print(f"   Messages: {info['message_count']}")
                print(f"   Tools Enabled: {info['tools_enabled']}")
                print(f"   Knowledge Base Size: {info['knowledge_base_size']}")
                continue
            
            # Check for session clear
            elif user_input.lower() == 'session clear':
                agent.clear_memory()
                print(" Conversation history cleared!")
                continue
            
            # Check for knowledge stats
            elif user_input.lower() == 'knowledge stats':
                stats = knowledge_base.get_stats()
                print(f"\n Knowledge Base Statistics")
                print(f"   Total Items: {stats.get('total_items', 0)}")
                print(f"   Unique Topics: {stats.get('unique_topics', 0)}")
                if stats.get('topics'):
                    print(f"   Topics: {', '.join(stats['topics'][:10])}")
                continue
            
            # Check for knowledge topics
            elif user_input.lower() == 'knowledge topics':
                topics = knowledge_base.get_all_topics()
                print(f"\n Available Topics ({len(topics)})")
                for topic in topics:
                    print(f"   • {topic}")
                continue
            
            # Check for model info
            elif user_input.lower() == 'model info':
                models = ollama_client.list_models()
                print(f"\n Current Model")
                for model in models:
                    print(f"   Name: {model.get('name', 'Unknown')}")
                print(f"   Tools Enabled: {tools_enabled}")
                continue
            
            # Process normal message
            print("\n AI: ", end="", flush=True)
            
            # Send to agent
            response = agent.process_message(user_input, use_tools=tools_enabled)
            
            # Print response
            print(response)
            print()  # Empty line for readability
            
        except KeyboardInterrupt:
            print("\n\n Goodbye! Stay secure!")
            break
        except Exception as e:
            print(f"\n Error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()