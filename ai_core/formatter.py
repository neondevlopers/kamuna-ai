import re
import json

class ResponseFormatter:
    """Clean Message"""
    
    @staticmethod
    def format_code_blocks(text):
        """Find code blocks"""
        pattern = r'```(\w*)\n(.*?)```'
        
        def replace_code(match):
            lang = match.group(1) or 'python'
            code = match.group(2)
            return f'\n- **Code ({lang}):**\n```\n{code}\n```\n'
        
        return re.sub(pattern, replace_code, text, flags=re.DOTALL)
    
    @staticmethod
    def format_lists(text):
        """Edit Clean List"""
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            #  (1., 2., etc.)
            if re.match(r'^\d+\.', line.strip()):
                line = f'   • {line.strip()}'
            # -
            elif line.strip().startswith('-'):
                line = f'   • {line.strip()[1:].strip()}'
            
            formatted.append(line)
        
        return '\n'.join(formatted)
    
    @staticmethod
    def extract_security_warnings(text):
        """Install And allert Secu"""
        warning_keywords = ['warning', 'caution', '=', 'permission', 'authorized', 'legal']
        
        lines = text.split('\n')
        warnings = []
        other_lines = []
        
        for line in lines:
            if any(kw in line.lower() for kw in warning_keywords):
                warnings.append(f'= {line.strip()}')
            else:
                other_lines.append(line)
        
        if warnings:
            warning_section = '\n'.join(warnings)
            return warning_section + '\n\n' + '\n'.join(other_lines)
        
        return '\n'.join(other_lines)
    
    @staticmethod
    def add_separators(text):
        """Add Line """
        sections = []
        current_section = []
        
        for line in text.split('\n'):
            if line.strip() and len(line.strip()) > 0:
                # ALL CAPS
                if ':' in line or line.isupper():
                    if current_section:
                        sections.append('\n'.join(current_section))
                        current_section = []
                    sections.append(f'\n📌 **{line.strip()}**\n')
                else:
                    current_section.append(line)
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return '\n'.join(sections)
    
    @staticmethod
    def truncate_long_response(text, max_length=2000):
        """Cut Message"""
        if len(text) <= max_length:
            return text
        
        # កាត់ត្រឹម max_length ហើយបន្ថែម ...
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + '\n\n... (Response truncated, continue asking for more details)'
    
    @staticmethod
    def format_response(raw_response, add_warnings=True):
        """Fuction Answer"""
        
        # 1. Message Short
        formatted = ResponseFormatter.truncate_long_response(raw_response)
        
        # 2. code blocks
        formatted = ResponseFormatter.format_code_blocks(formatted)
        
        # 3. Build List
        formatted = ResponseFormatter.format_lists(formatted)
        
        # 4. Add Security
        if add_warnings:
            formatted = ResponseFormatter.extract_security_warnings(formatted)
        
        # 5. Add Line
        formatted = ResponseFormatter.add_separators(formatted)
        
        return formatted.strip()
    
    @staticmethod
    def format_tool_result(tool_name, result_data):
        """ធ្វើទ្រង់ទ្រាយលទ្ធផលពី tools"""
        
        if isinstance(result_data, dict):
            formatted = f"\n+ **{tool_name} Results:**\n"
            for key, value in result_data.items():
                if isinstance(value, list):
                    formatted += f"   • {key}: {', '.join(str(v) for v in value)}\n"
                else:
                    formatted += f"   • {key}: {value}\n"
            return formatted
        
        elif isinstance(result_data, list):
            formatted = f"\n+ **{tool_name} Results:**\n"
            for item in result_data:
                formatted += f"   • {item}\n"
            return formatted
        
        else:
            return f"\n🔧 **{tool_name}:** {result_data}\n"
    
    @staticmethod
    def format_knowledge_results(results):
        """Build knowledge base"""
        
        if not results:
            return "No relevant information found."
        
        formatted = "+ **Knowledge Base Results:**\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result}\n\n"
        
        return formatted
    
    @staticmethod
    def create_error_message(error_type, details=None):
        """Build Simple Messages"""
        
        errors = {
            "api_error": " # **API Error:** Cannot connect to AI service. Please check if Colab is running.",
            "timeout": "+ **Timeout:** The request took too long. Please try again.",
            "no_response": "+ **No Response:** The AI did not generate a response. Please rephrase your question.",
            "tool_error": "+ **Tool Error:** Failed to execute security tool.",
            "knowledge_error": "+ **Knowledge Error:** Cannot access knowledge base."
        }
        
        message = errors.get(error_type, f"❌ **Error:** {error_type}")
        
        if details:
            message += f"\nDetails: {details}"
        
        return message

# បង្កើត instance សម្រាប់ប្រើងាយៗ
formatter = ResponseFormatter()