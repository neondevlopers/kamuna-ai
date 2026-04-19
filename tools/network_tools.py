import socket
import subprocess
import platform
from typing import Dict, List
from logger import logger

class NetworkTools:
    @staticmethod
    def get_open_ports() -> List[int]:
        """Get common open ports (safe analysis only)"""
        common_ports = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 8080]
        open_ports = []
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        return open_ports
    
    @staticmethod
    def get_active_connections() -> List[Dict]:
        """Get active network connections (safe info only)"""
        connections = []
        
        if platform.system() == "Windows":
            cmd = "netstat -an"
        else:
            cmd = "netstat -an"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')[4:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        connections.append({
                            "protocol": parts[0],
                            "local_address": parts[1],
                            "foreign_address": parts[2],
                            "state": parts[3] if len(parts) > 3 else "UNKNOWN"
                        })
        except Exception as e:
            logger.error(f"Failed to get connections: {e}")
        
        return connections[:20]  # Limit for safety
    
    @staticmethod
    def analyze_network_security() -> Dict:
        """Perform basic network security analysis"""
        open_ports = NetworkTools.get_open_ports()
        connections = NetworkTools.get_active_connections()
        
        security_issues = []
        if 22 in open_ports:
            security_issues.append("SSH port (22) is open - ensure strong authentication")
        if 3389 in open_ports:
            security_issues.append("RDP port (3389) is open - ensure it's properly secured")
        if 3306 in open_ports:
            security_issues.append("MySQL port (3306) is exposed - check access controls")
        
        return {
            "open_ports": open_ports,
            "active_connections_count": len(connections),
            "security_concerns": security_issues,
            "recommendations": [
                "Close unnecessary ports",
                "Use firewalls to restrict access",
                "Implement network monitoring",
                "Regular security audits"
            ] if security_issues else ["Network appears reasonably secure"]
        }