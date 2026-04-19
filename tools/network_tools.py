"""
Network Tools Module - Provides safe network analysis functions
For educational and authorized testing purposes only
"""

import socket
import subprocess
import platform
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

from logger import logger


class NetworkTools:
    """
    Safe network analysis tools for educational purposes
    Only scans localhost and requires explicit permission for external scans
    """
    
    # Common ports and their services
    COMMON_PORTS = {
        20: "FTP (Data)",
        21: "FTP (Control)",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        8080: "HTTP-Alt",
        8443: "HTTPS-Alt",
        27017: "MongoDB"
    }
    
    # Potentially dangerous ports (require warning)
    DANGEROUS_PORTS = [21, 22, 23, 3389, 5900, 5800]
    
    @staticmethod
    def get_open_ports(target: str = "127.0.0.1", port_range: Tuple[int, int] = (1, 1024)) -> Dict[str, Any]:
        """
        Scan for open ports on a target
        
        Args:
            target: Target IP or hostname (default: localhost)
            port_range: Tuple of (start_port, end_port)
        
        Returns:
            Dictionary with scan results
        """
        results = {
            "target": target,
            "scan_time": datetime.now().isoformat(),
            "open_ports": [],
            "closed_ports": [],
            "filtered_ports": [],
            "warnings": [],
            "scan_duration": 0
        }
        
        # Security check - only allow localhost for safety
        if target not in ["127.0.0.1", "localhost", "::1"]:
            results["warnings"].append(f"? Scanning external targets ({target}) requires explicit permission. Only localhost is allowed in this demo.")
            return results
        
        start_port, end_port = port_range
        start_time = datetime.now()
        
        try:
            for port in range(start_port, end_port + 1):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                
                if result == 0:
                    service = NetworkTools.COMMON_PORTS.get(port, "Unknown")
                    port_info = {
                        "port": port,
                        "service": service,
                        "dangerous": port in NetworkTools.DANGEROUS_PORTS
                    }
                    results["open_ports"].append(port_info)
                    
                    if port in NetworkTools.DANGEROUS_PORTS:
                        results["warnings"].append(f"* Dangerous port {port} ({service}) is open!")
                else:
                    results["closed_ports"].append(port)
                
                sock.close()
                
        except socket.gaierror:
            results["warnings"].append(f"^ Could not resolve hostname: {target}")
        except Exception as e:
            results["warnings"].append(f" ^ Scan error: {str(e)}")
        
        results["scan_duration"] = (datetime.now() - start_time).total_seconds()
        
        return results
    
    @staticmethod
    def scan_single_port(target: str, port: int) -> Dict[str, Any]:
        """
        Scan a single port on a target
        
        Args:
            target: Target IP or hostname
            port: Port number to scan
        
        Returns:
            Dictionary with scan result
        """
        result = {
            "target": target,
            "port": port,
            "is_open": False,
            "service": NetworkTools.COMMON_PORTS.get(port, "Unknown"),
            "warning": None,
            "error": None
        }
        
        # Security check
        if target not in ["127.0.0.1", "localhost", "::1"]:
            result["warning"] = "External scanning requires permission"
            return result
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            connection_result = sock.connect_ex((target, port))
            
            result["is_open"] = (connection_result == 0)
            sock.close()
            
        except socket.gaierror as e:
            result["error"] = f"Could not resolve hostname: {e}"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def get_active_connections() -> List[Dict[str, Any]]:
        """
        Get active network connections (safe info only)
        Uses netstat command
        
        Returns:
            List of active connections
        """
        connections = []
        
        try:
            # Use netstat command based on OS
            if platform.system() == "Windows":
                cmd = "netstat -an"
            else:
                cmd = "netstat -an"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            for line in lines:
                # Parse netstat output
                parts = line.split()
                
                if len(parts) >= 4:
                    # Skip header lines
                    if parts[0] in ['Active', 'Proto', 'TCP', 'UDP']:
                        continue
                    
                    connection = {
                        "protocol": parts[0],
                        "local_address": parts[1],
                        "foreign_address": parts[2],
                        "state": parts[3] if len(parts) > 3 else "UNKNOWN"
                    }
                    connections.append(connection)
            
            # Limit for safety and readability
            return connections[:50]
            
        except subprocess.TimeoutExpired:
            logger.error("Netstat command timed out")
            return []
        except Exception as e:
            logger.error(f"Failed to get connections: {e}")
            return []
    
    @staticmethod
    def analyze_network_security() -> Dict[str, Any]:
        """
        Perform basic network security analysis on localhost
        
        Returns:
            Dictionary with security analysis
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "open_ports": [],
            "security_concerns": [],
            "recommendations": [],
            "risk_level": "LOW"
        }
        
        # Get open ports
        scan_result = NetworkTools.get_open_ports("127.0.0.1", (1, 1024))
        
        for port_info in scan_result.get("open_ports", []):
            port = port_info["port"]
            service = port_info["service"]
            analysis["open_ports"].append({"port": port, "service": service})
            
            # Check for security concerns
            if port == 22:
                analysis["security_concerns"].append("SSH port (22) is open - ensure strong authentication and key-based login")
                analysis["recommendations"].append("Use SSH keys instead of passwords, disable root login")
            elif port == 21:
                analysis["security_concerns"].append("FTP port (21) is open - FTP sends credentials in plaintext")
                analysis["recommendations"].append("Use SFTP or FTPS instead of plain FTP")
            elif port == 23:
                analysis["security_concerns"].append("Telnet port (23) is open - Telnet is completely insecure")
                analysis["recommendations"].append("Disable Telnet and use SSH instead")
            elif port == 3389:
                analysis["security_concerns"].append("RDP port (3389) is open - ensure Network Level Authentication is enabled")
                analysis["recommendations"].append("Use VPN for RDP access, enable NLA, limit users")
            elif port == 3306:
                analysis["security_concerns"].append("MySQL port (3306) is exposed - check access controls")
                analysis["recommendations"].append("Bind to localhost only if possible, use strong passwords")
            elif port == 5432:
                analysis["security_concerns"].append("PostgreSQL port (5432) is exposed")
                analysis["recommendations"].append("Use firewall rules to restrict access")
        
        # General recommendations
        if len(analysis["open_ports"]) > 10:
            analysis["recommendations"].append("Consider closing unnecessary ports to reduce attack surface")
            analysis["risk_level"] = "MEDIUM"
        
        if not analysis["recommendations"]:
            analysis["recommendations"].append("Network appears reasonably secure")
        
        return analysis
    
    @staticmethod
    def ping_host(host: str) -> Dict[str, Any]:
        """
        Ping a host to check if it's reachable
        
        Args:
            host: Hostname or IP address
        
        Returns:
            Dictionary with ping results
        """
        result = {
            "host": host,
            "reachable": False,
            "response_time": None,
            "error": None
        }
        
        # Security - only allow localhost
        if host not in ["127.0.0.1", "localhost", "::1", "8.8.8.8"]:
            result["error"] = "Ping only allowed for localhost or public DNS for demo"
            return result
        
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', host]
            
            response = subprocess.run(command, capture_output=True, text=True, timeout=5)
            
            if response.returncode == 0:
                result["reachable"] = True
                
                # Extract response time
                if platform.system().lower() == 'windows':
                    match = re.search(r'time[=<](\d+)ms', response.stdout)
                else:
                    match = re.search(r'time=(\d+\.?\d*) ms', response.stdout)
                
                if match:
                    result["response_time"] = float(match.group(1))
            else:
                result["error"] = "Host unreachable"
                
        except subprocess.TimeoutExpired:
            result["error"] = "Ping timeout"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def dns_lookup(hostname: str) -> Dict[str, Any]:
        """
        Perform DNS lookup for a hostname
        
        Args:
            hostname: Domain name to lookup
        
        Returns:
            Dictionary with DNS lookup results
        """
        result = {
            "hostname": hostname,
            "ip_addresses": [],
            "error": None
        }
        
        try:
            # Get IP addresses
            addrinfo = socket.getaddrinfo(hostname, None)
            ip_set = set()
            
            for addr in addrinfo:
                ip = addr[4][0]
                ip_set.add(ip)
            
            result["ip_addresses"] = list(ip_set)
            
        except socket.gaierror as e:
            result["error"] = f"Could not resolve hostname: {e}"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """
        Get basic network information about the local machine
        
        Returns:
            Dictionary with network info
        """
        info = {
            "hostname": socket.gethostname(),
            "local_ip": None,
            "public_ip": None,
            "interfaces": []
        }
        
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["local_ip"] = s.getsockname()[0]
            s.close()
        except Exception:
            info["local_ip"] = "Could not determine"
        
        # Get interface info (simplified)
        try:
            hostname = socket.gethostname()
            info["interfaces"] = socket.gethostbyname_ex(hostname)[2]
        except Exception:
            pass
        
        return info
    
    @staticmethod
    def format_scan_results(scan_results: Dict[str, Any]) -> str:
        """
        Format scan results for display
        
        Args:
            scan_results: Results from get_open_ports()
        
        Returns:
            Formatted string for display
        """
        if not scan_results:
            return "No scan results available."
        
        output = f"! **Port Scan Results for {scan_results.get('target', 'unknown')}**\n"
        output += f"% Scan completed in {scan_results.get('scan_duration', 0):.2f} seconds\n\n"
        
        # Open ports
        open_ports = scan_results.get("open_ports", [])
        if open_ports:
            output += f"+ **Open Ports ({len(open_ports)})**\n"
            for port_info in open_ports:
                danger_icon = "+ " if port_info.get("dangerous") else "🔓"
                output += f"  {danger_icon} Port {port_info['port']}: {port_info['service']}\n"
        else:
            output += "+ **No open ports found** in scanned range.\n"
        
        # Warnings
        warnings = scan_results.get("warnings", [])
        if warnings:
            output += f"\n WR **Warnings**\n"
            for warning in warnings:
                output += f"  {warning}\n"
        
        return output


# Standalone functions for easy access
def scan_ports(target: str = "127.0.0.1", ports: List[int] = None) -> Dict[str, Any]:
    """
    Quick port scan function
    
    Args:
        target: Target host
        ports: List of ports to scan (default: common ports)
    
    Returns:
        Scan results
    """
    if ports is None:
        ports = [80, 443, 22, 3306, 5432, 8080]
    
    results = {"target": target, "open_ports": [], "closed_ports": []}
    
    for port in ports:
        result = NetworkTools.scan_single_port(target, port)
        if result.get("is_open"):
            results["open_ports"].append({"port": port, "service": result.get("service")})
        else:
            results["closed_ports"].append(port)
    
    return results


# Tool registry for the AI agent
NETWORK_TOOLS = {
    "scan_ports": NetworkTools.get_open_ports,
    "quick_scan": scan_ports,
    "security_analysis": NetworkTools.analyze_network_security,
    "active_connections": NetworkTools.get_active_connections,
    "ping": NetworkTools.ping_host,
    "dns_lookup": NetworkTools.dns_lookup,
    "network_info": NetworkTools.get_network_info
}