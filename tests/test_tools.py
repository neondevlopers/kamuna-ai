# tests/test_tools.py
"""
Unit tests for tools module (Network, Security, System, Log, File)
Run with: pytest tests/test_tools.py -v
"""

import os
import sys
import pytest
import tempfile
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.network_tools import NetworkTools
from tools.security_checks import SecurityChecker
from tools.system_info import SystemInfo
from tools.log_analyzer import LogAnalyzer
from tools.file_reader import FileReader


class TestNetworkTools:
    """Test cases for Network Tools"""
    
    def test_get_open_ports_localhost(self):
        """Test scanning localhost for open ports"""
        results = NetworkTools.get_open_ports("127.0.0.1", (80, 80))
        assert results is not None
        assert "target" in results
        assert results["target"] == "127.0.0.1"
    
    def test_scan_single_port(self):
        """Test scanning a single port"""
        result = NetworkTools.scan_single_port("127.0.0.1", 80)
        assert result is not None
        assert "port" in result
        assert result["port"] == 80
        assert "is_open" in result
    
    def test_analyze_network_security(self):
        """Test network security analysis"""
        analysis = NetworkTools.analyze_network_security()
        assert analysis is not None
        assert "open_ports" in analysis
        assert "security_concerns" in analysis
        assert "recommendations" in analysis
        assert "risk_level" in analysis
    
    def test_get_active_connections(self):
        """Test getting active network connections"""
        connections = NetworkTools.get_active_connections()
        assert connections is not None
        assert isinstance(connections, list)
    
    def test_ping_localhost(self):
        """Test pinging localhost"""
        result = NetworkTools.ping_host("127.0.0.1")
        assert result is not None
        assert "host" in result
        assert "reachable" in result
    
    def test_dns_lookup(self):
        """Test DNS lookup"""
        result = NetworkTools.dns_lookup("localhost")
        assert result is not None
        assert "hostname" in result
        assert "ip_addresses" in result
    
    def test_get_network_info(self):
        """Test getting local network information"""
        info = NetworkTools.get_network_info()
        assert info is not None
        assert "hostname" in info
        assert "local_ip" in info
    
    def test_format_scan_results(self):
        """Test formatting scan results for display"""
        scan_results = NetworkTools.get_open_ports("127.0.0.1", (80, 80))
        formatted = NetworkTools.format_scan_results(scan_results)
        assert formatted is not None
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestSecurityChecker:
    """Test cases for Security Tools"""
    
    def test_check_system_security(self):
        """Test system security check"""
        results = SecurityChecker.check_system_security()
        assert results is not None
        assert "os" in results
        assert "security_score" in results
        assert "risk_level" in results
        assert "recommendations" in results
    
    def test_check_file_permissions(self):
        """Test file permission checking"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            result = SecurityChecker.check_file_permissions(temp_path)
            assert result is not None
            assert "filepath" in result
            assert "exists" in result
            assert result["exists"] is True
        finally:
            os.unlink(temp_path)
    
    def test_check_file_permissions_not_exists(self):
        """Test checking non-existent file"""
        result = SecurityChecker.check_file_permissions("/nonexistent/file.txt")
        assert result is not None
        assert result["exists"] is False
        assert "issues" in result
    
    def test_check_password_strength_weak(self):
        """Test weak password detection"""
        result = SecurityChecker.check_password_strength("password")
        assert result is not None
        assert result["strength"] == "WEAK"
        assert len(result["issues"]) > 0
    
    def test_check_password_strength_medium(self):
        """Test medium password detection"""
        result = SecurityChecker.check_password_strength("Passw0rd")
        assert result is not None
        assert result["strength"] in ["MEDIUM", "WEAK"]
    
    def test_check_password_strength_strong(self):
        """Test strong password detection"""
        result = SecurityChecker.check_password_strength("MyStr0ng!P@ssw0rd2024")
        assert result is not None
        assert result["strength"] == "STRONG"
        assert result["score"] >= 4
    
    def test_format_security_report(self):
        """Test formatting security report"""
        results = SecurityChecker.check_system_security()
        formatted = SecurityChecker.format_security_report(results)
        assert formatted is not None
        assert isinstance(formatted, str)
        assert "Security Score" in formatted or "security" in formatted.lower()


class TestSystemInfo:
    """Test cases for System Information Tools"""
    
    def test_get_system_basics(self):
        """Test getting basic system information"""
        info = SystemInfo.get_system_basics()
        assert info is not None
        assert "os" in info
        assert "hostname" in info
        assert "timestamp" in info
    
    def test_get_cpu_info(self):
        """Test getting CPU information"""
        info = SystemInfo.get_cpu_info()
        assert info is not None
        assert "physical_cores" in info or "logical_cores" in info
        assert "total_usage" in info
    
    def test_get_memory_info(self):
        """Test getting memory information"""
        info = SystemInfo.get_memory_info()
        assert info is not None
        assert "total" in info
        assert "percentage" in info
    
    def test_get_disk_info(self):
        """Test getting disk information"""
        disks = SystemInfo.get_disk_info()
        assert disks is not None
        assert isinstance(disks, list)
    
    def test_get_network_info(self):
        """Test getting network information"""
        info = SystemInfo.get_network_info()
        assert info is not None
        assert "interfaces" in info
    
    def test_get_process_info(self):
        """Test getting process information"""
        processes = SystemInfo.get_process_info(top_n=5)
        assert processes is not None
        assert isinstance(processes, list)
        assert len(processes) <= 5
    
    def test_get_all_system_info(self):
        """Test getting complete system information"""
        info = SystemInfo.get_all_system_info()
        assert info is not None
        assert "basics" in info
        assert "cpu" in info
        assert "memory" in info
    
    def test_format_complete_report(self):
        """Test formatting complete system report"""
        info = SystemInfo.get_all_system_info()
        formatted = SystemInfo.format_complete_report(info)
        assert formatted is not None
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_bytes_to_human(self):
        """Test byte to human readable conversion"""
        # This is a private method, testing via public method that uses it
        info = SystemInfo.get_memory_info()
        assert "GB" in info.get("total", "") or "MB" in info.get("total", "")


class TestLogAnalyzer:
    """Test cases for Log Analysis Tools"""
    
    def test_load_log_from_text(self):
        """Test loading log from text"""
        log_text = """
2024-01-01 10:00:00 Failed password for user admin from 192.168.1.100
2024-01-01 10:01:00 Accepted password for user john
2024-01-01 10:02:00 ERROR: Connection refused
"""
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        assert analyzer.log_content is not None
    
    def test_analyze_security_events(self):
        """Test security event analysis"""
        log_text = """
Failed password for user admin from 192.168.1.100
Failed password for user admin from 192.168.1.100
Failed password for user admin from 192.168.1.100
Failed password for user admin from 192.168.1.100
Failed password for user admin from 192.168.1.100
Accepted password for user john
ERROR: Database connection failed
"""
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        results = analyzer.analyze_security_events()
        
        assert results is not None
        assert "summary" in results
        assert "failed_logins" in results
        assert results["summary"]["total_failed_logins"] >= 5
    
    def test_detect_suspicious_ips(self):
        """Test suspicious IP detection"""
        log_text = """
Failed password from 192.168.1.100
Failed password from 192.168.1.100
Failed password from 192.168.1.100
Failed password from 192.168.1.100
Failed password from 192.168.1.100
"""
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        analyzer.analyze_security_events()
        suspicious = analyzer.detect_suspicious_ips()
        
        assert suspicious is not None
        assert isinstance(suspicious, list)
    
    def test_detect_web_attacks(self):
        """Test web attack detection"""
        log_text = """
GET /login?username=admin' OR '1'='1
GET /search?q=<script>alert('XSS')</script>
GET /download?file=../../../etc/passwd
POST /exec?cmd=; ls -la
"""
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        attacks = analyzer.detect_web_attacks()
        
        assert attacks is not None
        assert "sql_injection" in attacks
        assert "xss_attempts" in attacks
        assert "path_traversal" in attacks
        assert "command_injection" in attacks
    
    def test_generate_report(self):
        """Test report generation"""
        log_text = "Failed password from 192.168.1.1"
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        analyzer.analyze_security_events()
        
        report = analyzer.generate_report(format_type="text")
        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_generate_json_report(self):
        """Test JSON report generation"""
        log_text = "Test log entry"
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        analyzer.analyze_security_events()
        
        report = analyzer.generate_report(format_type="json")
        assert report is not None
        # Should be valid JSON
        import json
        data = json.loads(report)
        assert "timestamp" in data


class TestFileReader:
    """Test cases for File Reader Tools"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def text_file(self, temp_dir):
        """Create a temporary text file"""
        file_path = os.path.join(temp_dir, "test.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Line 1: Hello World\n")
            f.write("Line 2: This is a test file\n")
            f.write("Line 3: Password = secret123\n")
            f.write("Line 4: API_KEY = abc123xyz\n")
        return file_path
    
    def test_read_text_file(self, temp_dir, text_file):
        """Test reading a text file"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.read_file(text_file)
        
        assert result["success"] is True
        assert "file_info" in result
        assert result["file_info"]["name"] == "test.txt"
        assert result["content"] is not None
    
    def test_read_file_outside_root(self, temp_dir):
        """Test reading file outside root directory (should be denied)"""
        reader = FileReader(root_directory=temp_dir)
        
        # Try to read a file outside root
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            outside_path = f.name
        
        try:
            result = reader.read_file(outside_path)
            assert result["success"] is False
            assert "Access denied" in result["error"] or "not allowed" in result["error"]
        finally:
            os.unlink(outside_path)
    
    def test_list_directory(self, temp_dir, text_file):
        """Test listing directory contents"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.list_directory(temp_dir)
        
        assert result["success"] is True
        assert "files" in result
        assert len(result["files"]) >= 1
        assert result["files"][0]["name"] == "test.txt"
    
    def test_get_file_metadata(self, temp_dir, text_file):
        """Test getting file metadata"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.get_file_metadata(text_file)
        
        assert result["success"] is True
        assert "metadata" in result
        assert result["metadata"]["name"] == "test.txt"
        assert "size_bytes" in result["metadata"]
    
    def test_search_in_file(self, temp_dir, text_file):
        """Test searching for pattern in file"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.search_in_file(text_file, "password", case_sensitive=False)
        
        assert result["success"] is True
        assert result["match_count"] >= 1
        assert "secret123" in str(result["matches"])
    
    def test_detect_sensitive_data(self, temp_dir, text_file):
        """Test sensitive data detection"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.read_file(text_file)
        
        assert result["success"] is True
        assert "sensitive_findings" in result
        # Should detect password pattern
        assert len(result["sensitive_findings"]) >= 1
    
    def test_format_file_result(self, temp_dir, text_file):
        """Test formatting file read result"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.read_file(text_file)
        formatted = reader.format_file_result(result)
        
        assert formatted is not None
        assert isinstance(formatted, str)
        assert "test.txt" in formatted
    
    def test_format_directory_result(self, temp_dir, text_file):
        """Test formatting directory listing result"""
        reader = FileReader(root_directory=temp_dir)
        result = reader.list_directory(temp_dir)
        formatted = reader.format_directory_result(result)
        
        assert formatted is not None
        assert isinstance(formatted, str)
        assert "test.txt" in formatted


class TestToolsIntegration:
    """Integration tests for multiple tools"""
    
    def test_network_and_security_integration(self):
        """Test using network and security tools together"""
        # Get network info
        network_info = NetworkTools.get_network_info()
        assert network_info is not None
        
        # Check system security
        security_results = SecurityChecker.check_system_security()
        assert security_results is not None
        
        # Both should work independently
        assert isinstance(network_info, dict)
        assert isinstance(security_results, dict)
    
    def test_system_and_log_integration(self):
        """Test using system info and log analysis together"""
        # Get system info
        sys_info = SystemInfo.get_system_basics()
        
        # Create a simple log
        log_text = f"System check at {sys_info.get('timestamp', 'unknown')}"
        analyzer = LogAnalyzer()
        analyzer.load_from_text(log_text)
        results = analyzer.analyze_security_events()
        
        assert results is not None
        assert "summary" in results


# Run tests directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])