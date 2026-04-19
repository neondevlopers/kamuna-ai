"""
Security Checker Module - Provides system security analysis and vulnerability checks
For educational and authorized testing purposes only
"""

import os
import socket
import sys
import platform
import subprocess
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from logger import logger


class SecurityChecker:
    """
    System security analysis tools for educational purposes
    Checks for common security issues and provides recommendations
    """
    
    # Common weak passwords patterns (for demonstration only)
    WEAK_PASSWORD_PATTERNS = [
        r'^password$', r'^123456$', r'^qwerty$', r'^admin$',
        r'^welcome$', r'^letmein$', r'^monkey$', r'^dragon$'
    ]
    
    # Suspicious process names
    SUSPICIOUS_PROCESSES = [
        'nc.exe', 'ncat.exe', 'netcat', 'meterpreter', 'reverse_shell',
        'keylogger', 'wireshark', 'tcpdump', 'nmap', 'hydra', 'john'
    ]
    
    # Critical system files that should have restricted permissions
    CRITICAL_FILES = [
        '/etc/passwd', '/etc/shadow', '/etc/sudoers',
        'C:\\Windows\\System32\\config\\SAM',
        'C:\\Windows\\System32\\drivers\\etc\\hosts'
    ]
    
    @staticmethod
    def check_system_security() -> Dict[str, Any]:
        """
        Perform comprehensive system security check
        
        Returns:
            Dictionary with security findings and recommendations
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "os": platform.system(),
            "os_version": platform.version(),
            "hostname": platform.node(),
            "security_issues": [],
            "warnings": [],
            "recommendations": [],
            "passing_checks": []
        }
        
        # Check OS version and updates
        results.update(SecurityChecker._check_os_updates())
        
        # Check firewall status
        results.update(SecurityChecker._check_firewall_status())
        
        # Check antivirus status (Windows only)
        if platform.system() == "Windows":
            results.update(SecurityChecker._check_antivirus_status())
        
        # Check for suspicious processes
        results.update(SecurityChecker._check_suspicious_processes())
        
        # Check running services
        results.update(SecurityChecker._check_running_services())
        
        # Check open ports (basic)
        results.update(SecurityChecker._check_open_ports_basic())
        
        # Check user accounts
        results.update(SecurityChecker._check_user_accounts())
        
        # Calculate overall security score
        results["security_score"] = SecurityChecker._calculate_security_score(results)
        results["risk_level"] = SecurityChecker._determine_risk_level(results["security_score"])
        
        return results
    
    @staticmethod
    def _check_os_updates() -> Dict[str, Any]:
        """Check if system is up to date"""
        result = {
            "os_updates_available": False,
            "os_update_warning": None,
            "recommendations": []
        }
        
        try:
            if platform.system() == "Windows":
                # Check Windows updates via PowerShell
                cmd = 'powershell "Get-WindowsUpdate | Select-Object -First 1"'
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout.strip():
                    result["os_updates_available"] = True
                    result["os_update_warning"] = "Windows updates are available"
                    result["recommendations"].append("Install pending Windows updates")
                else:
                    result["passing_checks"] = ["System is up to date"]
                    
            else:  # Linux
                # Check for package updates (simplified)
                cmd = "apt list --upgradable 2>/dev/null | grep -c upgradable"
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if process.stdout.strip() and int(process.stdout.strip()) > 0:
                    result["os_updates_available"] = True
                    result["os_update_warning"] = "System packages have updates available"
                    result["recommendations"].append("Run: sudo apt update && sudo apt upgrade")
                else:
                    result["passing_checks"] = ["System packages are up to date"]
                    
        except Exception as e:
            logger.error(f"Error checking OS updates: {e}")
            result["os_update_warning"] = "Could not check for updates"
        
        return result
    
    @staticmethod
    def _check_firewall_status() -> Dict[str, Any]:
        """Check if firewall is enabled"""
        result = {
            "firewall_enabled": False,
            "firewall_warning": None,
            "recommendations": []
        }
        
        try:
            if platform.system() == "Windows":
                cmd = 'powershell "Get-NetFirewallProfile | Select-Object -First 1"'
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                
                if "True" in process.stdout or "Enabled" in process.stdout:
                    result["firewall_enabled"] = True
                    result["passing_checks"] = ["Windows Firewall is enabled"]
                else:
                    result["firewall_warning"] = "Windows Firewall may be disabled"
                    result["recommendations"].append("Enable Windows Firewall")
                    
            else:  # Linux - check iptables/ufw
                # Check UFW status
                ufw_check = subprocess.run("ufw status", shell=True, capture_output=True, text=True, timeout=5)
                
                if "active" in ufw_check.stdout.lower():
                    result["firewall_enabled"] = True
                    result["passing_checks"] = ["UFW firewall is active"]
                else:
                    # Check iptables
                    iptables_check = subprocess.run("iptables -L -n", shell=True, capture_output=True, text=True, timeout=5)
                    
                    if "Chain INPUT" in iptables_check.stdout and "Chain FORWARD" in iptables_check.stdout:
                        result["firewall_enabled"] = True
                        result["passing_checks"] = ["iptables rules are present"]
                    else:
                        result["firewall_warning"] = "No active firewall detected"
                        result["recommendations"].append("Enable UFW: sudo ufw enable")
                        
        except Exception as e:
            logger.error(f"Error checking firewall: {e}")
            result["firewall_warning"] = "Could not check firewall status"
        
        return result
    
    @staticmethod
    def _check_antivirus_status() -> Dict[str, Any]:
        """Check if antivirus is enabled (Windows only)"""
        result = {
            "antivirus_enabled": False,
            "antivirus_warning": None,
            "recommendations": []
        }
        
        if platform.system() != "Windows":
            return result
        
        try:
            # Check Windows Defender status
            cmd = 'powershell "Get-MpComputerStatus | Select-Object -Property AntivirusEnabled, RealTimeProtectionEnabled"'
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if "True" in process.stdout:
                result["antivirus_enabled"] = True
                result["passing_checks"] = ["Windows Defender is active"]
            else:
                result["antivirus_warning"] = "Windows Defender may be disabled"
                result["recommendations"].append("Enable Windows Defender real-time protection")
                
        except Exception as e:
            logger.error(f"Error checking antivirus: {e}")
            result["antivirus_warning"] = "Could not check antivirus status"
        
        return result
    
    @staticmethod
    def _check_suspicious_processes() -> Dict[str, Any]:
        """Check for suspicious or potentially malicious processes"""
        result = {
            "suspicious_processes": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            if platform.system() == "Windows":
                cmd = "tasklist"
            else:
                cmd = "ps aux"
            
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output_lower = process.stdout.lower()
            
            for suspicious in SecurityChecker.SUSPICIOUS_PROCESSES:
                if suspicious.lower() in output_lower:
                    result["suspicious_processes"].append(suspicious)
                    result["warnings"].append(f"Suspicious process detected: {suspicious}")
                    result["recommendations"].append(f"Investigate process: {suspicious}")
                    
        except Exception as e:
            logger.error(f"Error checking processes: {e}")
        
        if not result["suspicious_processes"]:
            result["passing_checks"] = ["No suspicious processes detected"]
        
        return result
    
    @staticmethod
    def _check_running_services() -> Dict[str, Any]:
        """Check for unnecessary or risky running services"""
        result = {
            "risky_services": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Common risky services
        risky_services = ["telnet", "ftp", "rlogin", "rsh", "rexec"]
        
        try:
            if platform.system() == "Windows":
                cmd = 'powershell "Get-Service | Where-Object {$_.Status -eq \"Running\"} | Select-Object Name"'
            else:
                cmd = "systemctl list-units --type=service --state=running"
            
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output_lower = process.stdout.lower()
            
            for service in risky_services:
                if service in output_lower:
                    result["risky_services"].append(service)
                    result["warnings"].append(f"Risky service running: {service}")
                    result["recommendations"].append(f"Disable {service} if not needed")
                    
        except Exception as e:
            logger.error(f"Error checking services: {e}")
        
        if not result["risky_services"]:
            result["passing_checks"] = ["No risky services detected"]
        
        return result
    
    @staticmethod
    def _check_open_ports_basic() -> Dict[str, Any]:
        """Basic check for common open ports"""
        result = {
            "open_common_ports": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Common ports to check
        common_ports = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080]
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                result_code = sock.connect_ex(('127.0.0.1', port))
                
                if result_code == 0:
                    result["open_common_ports"].append(port)
                    
                    if port == 21:
                        result["warnings"].append("FTP (port 21) is open - credentials sent in plaintext")
                        result["recommendations"].append("Use SFTP instead of FTP")
                    elif port == 23:
                        result["warnings"].append("Telnet (port 23) is open - completely insecure")
                        result["recommendations"].append("Disable Telnet, use SSH")
                    elif port == 3389:
                        result["warnings"].append("RDP (port 3389) is open - ensure proper security")
                        result["recommendations"].append("Use VPN for RDP access")
                        
                sock.close()
            except Exception:
                pass
        
        return result
    
    @staticmethod
    def _check_user_accounts() -> Dict[str, Any]:
        """Check for security issues with user accounts"""
        result = {
            "guest_account_enabled": False,
            "admin_accounts": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            if platform.system() == "Windows":
                # Check for guest account
                guest_check = subprocess.run(
                    'powershell "Get-LocalUser -Name Guest | Select-Object -Property Enabled"',
                    shell=True, capture_output=True, text=True, timeout=5
                )
                
                if "True" in guest_check.stdout:
                    result["guest_account_enabled"] = True
                    result["warnings"].append("Guest account is enabled")
                    result["recommendations"].append("Disable guest account")
                    
                # Get admin accounts
                admin_check = subprocess.run(
                    'powershell "Get-LocalGroupMember -Group Administrators | Select-Object -Property Name"',
                    shell=True, capture_output=True, text=True, timeout=5
                )
                
                for line in admin_check.stdout.split('\n'):
                    if line.strip() and not line.startswith('Name'):
                        result["admin_accounts"].append(line.strip())
                        
            else:  # Linux
                # Check for root SSH login
                sshd_config = "/etc/ssh/sshd_config"
                if os.path.exists(sshd_config):
                    with open(sshd_config, 'r') as f:
                        content = f.read()
                        if "PermitRootLogin yes" in content and not content.startswith("#"):
                            result["warnings"].append("Root SSH login is permitted")
                            result["recommendations"].append("Disable root SSH login: PermitRootLogin no")
                            
        except Exception as e:
            logger.error(f"Error checking user accounts: {e}")
        
        return result
    
    @staticmethod
    def _calculate_security_score(results: Dict[str, Any]) -> int:
        """
        Calculate overall security score (0-100)
        
        Args:
            results: Security check results
        
        Returns:
            Security score as integer
        """
        score = 100
        deductions = 0
        
        # Deduct for security issues
        if results.get("firewall_warning"):
            deductions += 20
        if results.get("antivirus_warning"):
            deductions += 15
        if results.get("os_updates_available"):
            deductions += 15
        if results.get("guest_account_enabled"):
            deductions += 10
        if results.get("suspicious_processes"):
            deductions += 25
        if results.get("risky_services"):
            deductions += 15
        if results.get("open_common_ports"):
            deductions += len(results.get("open_common_ports", [])) * 5
        
        score = max(0, 100 - deductions)
        return score
    
    @staticmethod
    def _determine_risk_level(score: int) -> str:
        """
        Determine risk level based on security score
        
        Args:
            score: Security score (0-100)
        
        Returns:
            Risk level string
        """
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    @staticmethod
    def check_file_permissions(filepath: str) -> Dict[str, Any]:
        """
        Check file permissions for security issues
        
        Args:
            filepath: Path to file to check
        
        Returns:
            Dictionary with permission analysis
        """
        result = {
            "filepath": filepath,
            "exists": False,
            "is_critical": filepath in SecurityChecker.CRITICAL_FILES,
            "permissions": {},
            "issues": [],
            "recommendations": []
        }
        
        if not os.path.exists(filepath):
            result["issues"].append("File does not exist")
            return result
        
        result["exists"] = True
        
        if platform.system() != "Windows":
            import stat
            try:
                st = os.stat(filepath)
                result["permissions"] = {
                    "owner_read": bool(st.st_mode & stat.S_IRUSR),
                    "owner_write": bool(st.st_mode & stat.S_IWUSR),
                    "owner_exec": bool(st.st_mode & stat.S_IXUSR),
                    "group_read": bool(st.st_mode & stat.S_IRGRP),
                    "group_write": bool(st.st_mode & stat.S_IWGRP),
                    "group_exec": bool(st.st_mode & stat.S_IXGRP),
                    "others_read": bool(st.st_mode & stat.S_IROTH),
                    "others_write": bool(st.st_mode & stat.S_IWOTH),
                    "others_exec": bool(st.st_mode & stat.S_IXOTH)
                }
                
                # Check for security issues
                if result["permissions"]["others_write"]:
                    result["issues"].append("World-writable file - security risk")
                    result["recommendations"].append("Run: chmod 755 " + filepath)
                
                if result["permissions"]["others_read"]:
                    if any(keyword in filepath.lower() for keyword in ['password', 'secret', 'key', 'shadow']):
                        result["issues"].append("Sensitive file readable by others")
                        result["recommendations"].append("Run: chmod 640 " + filepath)
                
                if result["is_critical"]:
                    if result["permissions"]["others_read"] or result["permissions"]["others_write"]:
                        result["issues"].append(f"Critical system file has weak permissions")
                        result["recommendations"].append("Restrict permissions immediately")
                        
            except Exception as e:
                result["issues"].append(f"Could not read permissions: {e}")
        
        return result
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """
        Check password strength (for educational purposes only)
        
        Args:
            password: Password to check
        
        Returns:
            Dictionary with strength analysis
        """
        result = {
            "strength": "WEAK",
            "score": 0,
            "issues": [],
            "suggestions": []
        }
        
        score = 0
        
        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            result["issues"].append("Password is too short")
            result["suggestions"].append("Use at least 8 characters")
        
        # Complexity checks
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            result["issues"].append("No uppercase letters")
            result["suggestions"].append("Add uppercase letters")
        
        if re.search(r'[a-z]', password):
            score += 1
        else:
            result["issues"].append("No lowercase letters")
            result["suggestions"].append("Add lowercase letters")
        
        if re.search(r'\d', password):
            score += 1
        else:
            result["issues"].append("No numbers")
            result["suggestions"].append("Add numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            result["issues"].append("No special characters")
            result["suggestions"].append("Add special characters")
        
        # Common password check
        if password.lower() in ['password', '123456', 'qwerty', 'admin', 'welcome']:
            score = 0
            result["issues"].append("Commonly used password")
        
        # Determine strength
        if score >= 5:
            result["strength"] = "STRONG"
        elif score >= 3:
            result["strength"] = "MEDIUM"
        else:
            result["strength"] = "WEAK"
        
        result["score"] = score
        return result
    
    @staticmethod
    def format_security_report(results: Dict[str, Any]) -> str:
        """
        Format security check results for display
        
        Args:
            results: Results from check_system_security()
        
        Returns:
            Formatted string for display
        """
        output = f"+ **Security Report**\n"
        output += f"+ Generated: {results.get('timestamp', 'Unknown')}\n"
        output += f"+ System: {results.get('os', 'Unknown')} {results.get('os_version', '')}\n"
        output += f"+ Security Score: {results.get('security_score', 0)}/100\n"
        output += f"+ Risk Level: {results.get('risk_level', 'UNKNOWN')}\n\n"
        
        # Passing checks
        passing = results.get('passing_checks', [])
        if passing:
            output += f"+ **Passing Checks**\n"
            for check in passing:
                output += f"  • {check}\n"
            output += "\n"
        
        # Warnings
        warnings = results.get('warnings', [])
        if warnings:
            output += f"+ **Warnings**\n"
            for warning in warnings:
                output += f"  • {warning}\n"
            output += "\n"
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            output += f"+ **Recommendations**\n"
            for rec in recommendations:
                output += f"  • {rec}\n"
        
        return output


# Standalone functions for easy access
def quick_security_check() -> Dict[str, Any]:
    """Run a quick security check"""
    return SecurityChecker.check_system_security()


def check_file_security(filepath: str) -> Dict[str, Any]:
    """Check file security permissions"""
    return SecurityChecker.check_file_permissions(filepath)


# Tool registry for the AI agent
SECURITY_TOOLS = {
    "full_scan": SecurityChecker.check_system_security,
    "quick_scan": quick_security_check,
    "file_check": check_file_security,
    "password_check": SecurityChecker.check_password_strength
}