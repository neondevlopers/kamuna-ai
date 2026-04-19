# tools/file_reader.py
"""
File Reader Module - Provides safe file reading and analysis capabilities
For educational and authorized security testing purposes only
"""

import os
import re
import hashlib
import magic
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

from logger import logger


class FileReader:
    """
    Safe file reading and analysis tools
    Includes security checks to prevent unauthorized access
    """
    
    # Allowed file extensions for reading
    ALLOWED_EXTENSIONS = {
        'txt', 'log', 'py', 'js', 'html', 'css', 'json', 'xml', 'yaml', 'yml',
        'md', 'rst', 'ini', 'cfg', 'conf', 'csv', 'sql', 'sh', 'bat', 'ps1',
        'java', 'c', 'cpp', 'h', 'go', 'rs', 'php', 'rb', 'pl'
    }
    
    # Binary file extensions (will show preview only)
    BINARY_EXTENSIONS = {
        'exe', 'dll', 'so', 'dylib', 'bin', 'dat', 'db', 'sqlite',
        'jpg', 'png', 'gif', 'bmp', 'ico', 'pdf', 'doc', 'docx', 'xls', 'xlsx',
        'zip', 'tar', 'gz', 'bz2', '7z', 'rar'
    }
    
    # Sensitive patterns to highlight
    SENSITIVE_PATTERNS = {
        'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*\S+',
        'api_key': r'(?i)(api[_-]?key|apikey|token)\s*[:=]\s*\S+',
        'secret': r'(?i)(secret|private_key)\s*[:=]\s*\S+',
        'aws_key': r'AKIA[0-9A-Z]{16}',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'url': r'https?://[^\s]+',
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    }
    
    def __init__(self, root_directory: str = None):
        """
        Initialize FileReader
        
        Args:
            root_directory: Restrict file access to this directory (security)
        """
        self.root_directory = root_directory or os.getcwd()
        self.current_file = None
        self.file_content = None
        self.file_info = {}
        
        # Ensure root directory exists
        if not os.path.exists(self.root_directory):
            os.makedirs(self.root_directory, exist_ok=True)
        
        logger.info(f"FileReader initialized with root: {self.root_directory}")
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        Check if file path is safe to access
        
        Args:
            file_path: Path to check
        
        Returns:
            True if safe, False otherwise
        """
        try:
            # Resolve to absolute path
            abs_path = os.path.abspath(file_path)
            abs_root = os.path.abspath(self.root_directory)
            
            # Check if path is within root directory
            if not abs_path.startswith(abs_root):
                logger.warning(f"Access denied: {abs_path} is outside root {abs_root}")
                return False
            
            # Check for path traversal attempts
            if '..' in file_path or file_path.startswith('/etc') or file_path.startswith('C:\\Windows'):
                logger.warning(f"Potential path traversal detected: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking path safety: {e}")
            return False
    
    def _get_file_type(self, file_path: str) -> str:
        """
        Detect file type using python-magic
        
        Args:
            file_path: Path to file
        
        Returns:
            File type description
        """
        try:
            mime = magic.from_file(file_path, mime=True)
            return mime
        except Exception:
            # Fallback to extension-based detection
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            if ext in self.ALLOWED_EXTENSIONS:
                return f"text/{ext}"
            elif ext in self.BINARY_EXTENSIONS:
                return f"application/{ext}"
            else:
                return "unknown"
    
    def _calculate_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """
        Calculate file hash
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256)
        
        Returns:
            Hash string
        """
        try:
            hash_func = getattr(hashlib, algorithm)()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return ""
    
    def _detect_sensitive_data(self, content: str) -> Dict[str, List[str]]:
        """
        Detect sensitive data patterns in file content
        
        Args:
            content: File content
        
        Returns:
            Dictionary of found patterns
        """
        findings = {}
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                # Redact sensitive values for display
                if pattern_name in ['password', 'api_key', 'secret']:
                    matches = [m[:20] + '...' if len(m) > 20 else m for m in matches[:3]]
                findings[pattern_name] = matches[:5]  # Limit to 5 matches
        
        return findings
    
    def read_file(self, file_path: str, max_size_mb: int = 10) -> Dict[str, Any]:
        """
        Read and analyze a file safely
        
        Args:
            file_path: Path to file (relative to root or absolute)
            max_size_mb: Maximum file size to read in MB
        
        Returns:
            Dictionary with file information and content
        """
        result = {
            "success": False,
            "error": None,
            "file_info": {},
            "content": None,
            "preview": None,
            "sensitive_findings": {},
            "statistics": {}
        }
        
        # Resolve path
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.root_directory, file_path)
        
        # Security check
        if not self._is_safe_path(file_path):
            result["error"] = "Access denied: File path is not allowed"
            return result
        
        # Check if file exists
        if not os.path.exists(file_path):
            result["error"] = f"File not found: {file_path}"
            return result
        
        # Check file size
        file_size = os.path.getsize(file_path)
        max_size = max_size_mb * 1024 * 1024
        
        if file_size > max_size:
            result["error"] = f"File too large: {file_size / 1024 / 1024:.2f} MB (max {max_size_mb} MB)"
            return result
        
        try:
            # Get file info
            stat = os.stat(file_path)
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            result["file_info"] = {
                "path": file_path,
                "name": os.path.basename(file_path),
                "extension": ext,
                "size_bytes": file_size,
                "size_human": self._bytes_to_human(file_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "file_type": self._get_file_type(file_path),
                "hash_md5": self._calculate_hash(file_path, 'md5'),
                "hash_sha256": self._calculate_hash(file_path, 'sha256')
            }
            
            # Read file based on type
            is_binary = ext in self.BINARY_EXTENSIONS
            
            if is_binary:
                # Binary file - preview only
                result["preview"] = f"🔧 Binary file: {ext.upper()} format. Content cannot be displayed."
                result["statistics"] = {
                    "is_binary": True,
                    "file_type": ext.upper()
                }
            else:
                # Text file - read content
                encoding = self._detect_encoding(file_path)
                
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                
                result["content"] = content
                result["preview"] = self._get_preview(content)
                result["sensitive_findings"] = self._detect_sensitive_data(content)
                result["statistics"] = self._get_text_statistics(content)
                result["statistics"]["encoding"] = encoding
            
            self.current_file = file_path
            self.file_content = result["content"]
            self.file_info = result["file_info"]
            result["success"] = True
            
            logger.info(f"Successfully read file: {file_path}")
            
        except UnicodeDecodeError:
            result["error"] = "File encoding not supported. Try binary mode."
        except Exception as e:
            result["error"] = f"Error reading file: {str(e)}"
            logger.error(f"Error reading file {file_path}: {e}")
        
        return result
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding
        
        Args:
            file_path: Path to file
        
        Returns:
            Detected encoding
        """
        import chardet
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8') or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def _get_preview(self, content: str, max_chars: int = 1000) -> str:
        """
        Get preview of file content
        
        Args:
            content: Full file content
            max_chars: Maximum characters for preview
        
        Returns:
            Preview string
        """
        if len(content) <= max_chars:
            return content
        
        preview = content[:max_chars]
        
        # Try to cut at line boundary
        last_newline = preview.rfind('\n')
        if last_newline > max_chars - 200:
            preview = preview[:last_newline]
        
        return preview + f"\n\n... (truncated, {len(content) - max_chars} more characters)"
    
    def _get_text_statistics(self, content: str) -> Dict[str, Any]:
        """
        Get statistics about text content
        
        Args:
            content: File content
        
        Returns:
            Dictionary with statistics
        """
        lines = content.split('\n')
        words = content.split()
        
        # Count characters
        char_count = len(content)
        
        # Count non-empty lines
        non_empty_lines = sum(1 for line in lines if line.strip())
        
        # Estimate line distribution
        line_lengths = [len(line) for line in lines if line.strip()]
        
        stats = {
            "line_count": len(lines),
            "non_empty_lines": non_empty_lines,
            "word_count": len(words),
            "character_count": char_count,
            "avg_line_length": sum(line_lengths) / len(line_lengths) if line_lengths else 0,
            "max_line_length": max(line_lengths) if line_lengths else 0
        }
        
        # Detect language (simple)
        if re.search(r'[\u1000-\u109F]', content):
            stats["detected_language"] = "Khmer"
        elif re.search(r'[\u4e00-\u9fff]', content):
            stats["detected_language"] = "Chinese/Japanese/Korean"
        else:
            stats["detected_language"] = "Latin (English likely)"
        
        return stats
    
    def _bytes_to_human(self, bytes_value: int) -> str:
        """
        Convert bytes to human readable format
        
        Args:
            bytes_value: Size in bytes
        
        Returns:
            Human readable string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def search_in_file(self, file_path: str, pattern: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for pattern in file
        
        Args:
            file_path: Path to file
            pattern: Regex pattern to search
            case_sensitive: Whether search is case sensitive
        
        Returns:
            Dictionary with search results
        """
        result = {
            "success": False,
            "matches": [],
            "match_count": 0,
            "error": None
        }
        
        file_result = self.read_file(file_path)
        
        if not file_result["success"]:
            result["error"] = file_result["error"]
            return result
        
        content = file_result["content"]
        if not content:
            result["error"] = "File is binary or empty"
            return result
        
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                matches = regex.finditer(line)
                for match in matches:
                    result["matches"].append({
                        "line": line_num,
                        "content": line.strip()[:200],
                        "match": match.group(0)[:100]
                    })
            
            result["match_count"] = len(result["matches"])
            result["success"] = True
            
        except re.error as e:
            result["error"] = f"Invalid regex pattern: {e}"
        except Exception as e:
            result["error"] = f"Search error: {e}"
        
        return result
    
    def list_directory(self, directory_path: str = None, extensions: List[str] = None) -> Dict[str, Any]:
        """
        List files in a directory
        
        Args:
            directory_path: Path to directory (relative to root)
            extensions: Filter by file extensions
        
        Returns:
            Dictionary with directory listing
        """
        if directory_path is None:
            directory_path = self.root_directory
        elif not os.path.isabs(directory_path):
            directory_path = os.path.join(self.root_directory, directory_path)
        
        result = {
            "success": False,
            "path": directory_path,
            "files": [],
            "directories": [],
            "total_size": 0,
            "error": None
        }
        
        # Security check
        if not self._is_safe_path(directory_path):
            result["error"] = "Access denied: Directory path is not allowed"
            return result
        
        if not os.path.exists(directory_path):
            result["error"] = f"Directory not found: {directory_path}"
            return result
        
        if not os.path.isdir(directory_path):
            result["error"] = f"Not a directory: {directory_path}"
            return result
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if os.path.isdir(item_path):
                    result["directories"].append({
                        "name": item,
                        "path": item_path,
                        "type": "directory"
                    })
                else:
                    ext = os.path.splitext(item)[1].lower().lstrip('.')
                    
                    # Filter by extension if specified
                    if extensions and ext not in extensions:
                        continue
                    
                    size = os.path.getsize(item_path)
                    result["total_size"] += size
                    
                    result["files"].append({
                        "name": item,
                        "path": item_path,
                        "extension": ext,
                        "size_bytes": size,
                        "size_human": self._bytes_to_human(size),
                        "modified": datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat(),
                        "is_text": ext in self.ALLOWED_EXTENSIONS
                    })
            
            # Sort files by name
            result["files"].sort(key=lambda x: x["name"])
            result["directories"].sort(key=lambda x: x["name"])
            result["total_size_human"] = self._bytes_to_human(result["total_size"])
            result["success"] = True
            
        except Exception as e:
            result["error"] = f"Error listing directory: {e}"
            logger.error(f"Error listing directory {directory_path}: {e}")
        
        return result
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without reading content
        
        Args:
            file_path: Path to file
        
        Returns:
            Dictionary with file metadata
        """
        result = {
            "success": False,
            "metadata": {},
            "error": None
        }
        
        # Security check
        if not self._is_safe_path(file_path):
            result["error"] = "Access denied: File path is not allowed"
            return result
        
        if not os.path.exists(file_path):
            result["error"] = f"File not found: {file_path}"
            return result
        
        try:
            stat = os.stat(file_path)
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            result["metadata"] = {
                "path": file_path,
                "name": os.path.basename(file_path),
                "extension": ext,
                "size_bytes": stat.st_size,
                "size_human": self._bytes_to_human(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK),
                "is_executable": os.access(file_path, os.X_OK),
                "file_type": self._get_file_type(file_path)
            }
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = f"Error getting metadata: {e}"
        
        return result
    
    def format_file_result(self, result: Dict[str, Any]) -> str:
        """
        Format file read result for display
        
        Args:
            result: Result from read_file()
        
        Returns:
            Formatted string
        """
        if not result["success"]:
            return f"# **Error:** {result['error']}"
        
        info = result["file_info"]
        
        output = f"+ **File Analysis: {info['name']}**\n\n"
        output += f"+ Size: {info['size_human']}\n"
        output += f"+ Type: {info['file_type']}\n"
        output += f"+ SHA256: {info['hash_sha256'][:16]}...\n"
        output += f"+ Modified: {info['modified'][:19]}\n\n"
        
        # Statistics
        stats = result.get("statistics", {})
        if stats and not stats.get("is_binary", False):
            output += f"+ **Statistics**\n"
            output += f"   • Lines: {stats.get('line_count', 0)}\n"
            output += f"   • Words: {stats.get('word_count', 0)}\n"
            output += f"   • Characters: {stats.get('character_count', 0)}\n"
            output += f"   • Language: {stats.get('detected_language', 'Unknown')}\n\n"
        
        # Sensitive findings
        findings = result.get("sensitive_findings", {})
        if findings:
            output += f"+ **Sensitive Data Detected**\n"
            for pattern, matches in findings.items():
                output += f"   • {pattern}: {', '.join(matches[:3])}\n"
            output += "\n"
        
        # Preview
        preview = result.get("preview")
        if preview:
            output += f"+ **Preview**\n"
            output += f"```\n{preview}\n```\n"
        
        return output
    
    def format_directory_result(self, result: Dict[str, Any]) -> str:
        """
        Format directory listing result for display
        
        Args:
            result: Result from list_directory()
        
        Returns:
            Formatted string
        """
        if not result["success"]:
            return f"+ **Error:** {result['error']}"
        
        output = f"+ **Directory: {os.path.basename(result['path'])}**\n\n"
        
        # Directories
        if result["directories"]:
            output += f"+ **Subdirectories ({len(result['directories'])})**\n"
            for d in result["directories"][:20]:
                output += f"   • {d['name']}/\n"
            if len(result["directories"]) > 20:
                output += f"   ... and {len(result['directories']) - 20} more\n"
            output += "\n"
        
        # Files
        if result["files"]:
            output += f"+ **Files ({len(result['files'])})**\n"
            for f in result["files"][:30]:
                output += f"   • {f['name']} - {f['size_human']}\n"
            if len(result["files"]) > 30:
                output += f"   ... and {len(result['files']) - 30} more\n"
            output += "\n"
        
        output += f"+ Total size: {result['total_size_human']}\n"
        
        return output


# Standalone functions for easy access
def read_file_safe(file_path: str, root_dir: str = None) -> Dict[str, Any]:
    """
    Quick safe file read
    
    Args:
        file_path: Path to file
        root_dir: Root directory restriction
    
    Returns:
        File analysis result
    """
    reader = FileReader(root_dir)
    return reader.read_file(file_path)


def list_files(directory: str = ".", extensions: List[str] = None) -> Dict[str, Any]:
    """
    Quick directory listing
    
    Args:
        directory: Directory path
        extensions: Filter by extensions
    
    Returns:
        Directory listing result
    """
    reader = FileReader()
    return reader.list_directory(directory, extensions)


# Tool registry for the AI agent
FILE_TOOLS = {
    "read": read_file_safe,
    "list": list_files,
    "metadata": FileReader().get_file_metadata,
    "search": FileReader().search_in_file
}