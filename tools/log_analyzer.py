"""
Log Analyzer Module - Provides log file analysis and security event detection
For educational and authorized security monitoring purposes only
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict

from logger import logger


class LogAnalyzer:
    """
    Log file analysis tools for security monitoring
    Detects suspicious patterns, brute force attempts, and security events
    """
    
    # Common log file paths
    COMMON_LOG_PATHS = {
        "linux": [
            "/var/log/syslog",
            "/var/log/auth.log",
            "/var/log/secure",
            "/var/log/apache2/access.log",
            "/var/log/apache2/error.log",
            "/var/log/nginx/access.log",
            "/var/log/nginx/error.log",
            "/var/log/fail2ban.log",
            "/var/log/ufw.log"
        ],
        "windows": [
            "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx",
            "C:\\Windows\\System32\\winevt\\Logs\\System.evtx",
            "C:\\Windows\\System32\\winevt\\Logs\\Application.evtx"
        ]
    }
    
    # Patterns for detecting suspicious activities
    PATTERNS = {
        "failed_login": [
            r"Failed password",
            r"authentication failure",
            r"login failed",
            r"Invalid password",
            r"Access denied"
        ],
        "successful_login": [
            r"Accepted password",
            r"session opened",
            r"login successful",
            r"authentication success"
        ],
        "brute_force": [
            r"Failed password for .* from ([\d\.]+)",
            r"authentication failure.*rhost=([\d\.]+)"
        ],
        "sql_injection": [
            r"SELECT.*' OR '1'='1",
            r"UNION.*SELECT",
            r"DROP TABLE",
            r"INSERT INTO.*VALUES"
        ],
        "xss_attempt": [
            r"<script.*>",
            r"javascript:",
            r"onerror=",
            r"onload="
        ],
        "path_traversal": [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"C:\\Windows"
        ],
        "command_injection": [
            r"; ls",
            r"\| cat",
            r"`whoami`",
            r"\$\(id\)"
        ],
        "suspicious_ips": [
            r"1\.1\.1\.1",
            r"2\.2\.2\.2"
        ],
        "error_patterns": [
            r"ERROR",
            r"FATAL",
            r"CRITICAL",
            r"Segmentation fault",
            r"Out of memory"
        ]
    }
    
    def __init__(self, log_file_path: Optional[str] = None):
        """
        Initialize LogAnalyzer
        
        Args:
            log_file_path: Path to log file (optional)
        """
        self.log_file_path = log_file_path
        self.log_content = None
        self.analysis_results = {}
        
    def load_log_file(self, file_path: str, max_lines: int = 10000) -> bool:
        """
        Load log file content
        
        Args:
            file_path: Path to log file
            max_lines: Maximum lines to read
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Log file not found: {file_path}")
                return False
            
            self.log_file_path = file_path
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Limit lines for performance
            if len(lines) > max_lines:
                lines = lines[-max_lines:]
                logger.info(f"Limited to last {max_lines} lines")
            
            self.log_content = ''.join(lines)
            logger.info(f"Loaded {len(lines)} lines from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading log file: {e}")
            return False
    
    def load_from_text(self, text: str) -> None:
        """
        Load log content from text string
        
        Args:
            text: Log content as string
        """
        self.log_content = text
        self.log_file_path = None
        logger.info("Loaded log content from text")
    
    def analyze_security_events(self) -> Dict[str, Any]:
        """
        Analyze log for security events
        
        Returns:
            Dictionary with security analysis results
        """
        if not self.log_content:
            return {"error": "No log content loaded"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "log_file": self.log_file_path,
            "total_lines": len(self.log_content.split('\n')),
            "failed_logins": [],
            "successful_logins": [],
            "suspicious_ips": [],
            "brute_force_attempts": [],
            "attack_patterns": defaultdict(int),
            "errors": [],
            "summary": {}
        }
        
        lines = self.log_content.split('\n')
        
        # Track IP addresses for brute force detection
        ip_failures = defaultdict(int)
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            
            # Check for failed logins
            for pattern in self.PATTERNS["failed_login"]:
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract IP if present
                    ip_match = re.search(r'(\d{1,3}\.){3}\d{1,3}', line)
                    if ip_match:
                        ip = ip_match.group(0)
                        ip_failures[ip] += 1
                        results["failed_logins"].append({
                            "line": line_num,
                            "ip": ip,
                            "content": line[:200]
                        })
                    else:
                        results["failed_logins"].append({
                            "line": line_num,
                            "content": line[:200]
                        })
                    break
            
            # Check for successful logins
            for pattern in self.PATTERNS["successful_login"]:
                if re.search(pattern, line, re.IGNORECASE):
                    results["successful_logins"].append({
                        "line": line_num,
                        "content": line[:200]
                    })
                    break
            
            # Check for attack patterns
            for attack_type, patterns in self.PATTERNS.items():
                if attack_type in ["failed_login", "successful_login", "error_patterns"]:
                    continue
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        results["attack_patterns"][attack_type] += 1
                        break
            
            # Check for errors
            for pattern in self.PATTERNS["error_patterns"]:
                if re.search(pattern, line, re.IGNORECASE):
                    results["errors"].append({
                        "line": line_num,
                        "content": line[:200]
                    })
                    break
        
        # Detect brute force attempts
        for ip, count in ip_failures.items():
            if count >= 5:  # Threshold for brute force
                results["brute_force_attempts"].append({
                    "ip": ip,
                    "failed_count": count,
                    "severity": "HIGH" if count >= 20 else "MEDIUM" if count >= 10 else "LOW"
                })
        
        # Add summary statistics
        results["summary"] = {
            "total_failed_logins": len(results["failed_logins"]),
            "total_successful_logins": len(results["successful_logins"]),
            "total_errors": len(results["errors"]),
            "unique_attack_patterns": len(results["attack_patterns"]),
            "potential_brute_force": len(results["brute_force_attempts"]),
            "severity_score": self._calculate_severity_score(results)
        }
        
        self.analysis_results = results
        return results
    
    def _calculate_severity_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall security severity score
        
        Args:
            results: Analysis results
        
        Returns:
            Severity score (0-100, higher = more severe)
        """
        score = 0
        
        # Failed logins
        failed_count = results["summary"]["total_failed_logins"]
        if failed_count > 100:
            score += 30
        elif failed_count > 50:
            score += 20
        elif failed_count > 10:
            score += 10
        
        # Brute force attempts
        brute_count = len(results["brute_force_attempts"])
        if brute_count > 5:
            score += 30
        elif brute_count > 2:
            score += 20
        elif brute_count > 0:
            score += 10
        
        # Attack patterns
        pattern_count = results["summary"]["unique_attack_patterns"]
        if pattern_count > 10:
            score += 25
        elif pattern_count > 5:
            score += 15
        elif pattern_count > 0:
            score += 5
        
        # Errors
        error_count = results["summary"]["total_errors"]
        if error_count > 50:
            score += 15
        elif error_count > 20:
            score += 10
        elif error_count > 0:
            score += 5
        
        return min(score, 100)
    
    def detect_suspicious_ips(self) -> List[Dict[str, Any]]:
        """
        Detect suspicious IP addresses from log
        
        Returns:
            List of suspicious IPs with details
        """
        if not self.log_content:
            return []
        
        suspicious_ips = []
        ip_activity = defaultdict(lambda: {"failed": 0, "success": 0, "attacks": []})
        
        lines = self.log_content.split('\n')
        
        for line in lines:
            # Extract IP
            ip_match = re.search(r'(\d{1,3}\.){3}\d{1,3}', line)
            if not ip_match:
                continue
            
            ip = ip_match.group(0)
            
            # Skip private IPs (optional)
            if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('127.'):
                continue
            
            # Check activity type
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.PATTERNS["failed_login"]):
                ip_activity[ip]["failed"] += 1
            elif any(re.search(pattern, line, re.IGNORECASE) for pattern in self.PATTERNS["successful_login"]):
                ip_activity[ip]["success"] += 1
            
            # Check for attack patterns
            for attack_type, patterns in self.PATTERNS.items():
                if attack_type in ["failed_login", "successful_login", "error_patterns"]:
                    continue
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if attack_type not in ip_activity[ip]["attacks"]:
                            ip_activity[ip]["attacks"].append(attack_type)
                        break
        
        # Filter suspicious IPs
        for ip, activity in ip_activity.items():
            if activity["failed"] >= 5 or len(activity["attacks"]) > 0:
                suspicious_ips.append({
                    "ip": ip,
                    "failed_attempts": activity["failed"],
                    "successful_attempts": activity["success"],
                    "attack_types": activity["attacks"],
                    "risk_score": min(100, (activity["failed"] * 2) + (len(activity["attacks"]) * 10))
                })
        
        # Sort by risk score
        suspicious_ips.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return suspicious_ips
    
    def get_time_based_analysis(self) -> Dict[str, Any]:
        """
        Analyze log events by time
        
        Returns:
            Dictionary with time-based analysis
        """
        if not self.log_content:
            return {"error": "No log content loaded"}
        
        time_analysis = {
            "hourly_distribution": defaultdict(int),
            "daily_distribution": defaultdict(int),
            "peak_activity_hours": [],
            "suspicious_time_patterns": []
        }
        
        lines = self.log_content.split('\n')
        
        # Common time patterns in logs
        time_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\w{3}/\d{4})',   # DD/Mon/YYYY
            r'(\d{2}:\d{2}:\d{2})'    # HH:MM:SS
        ]
        
        for line in lines:
            # Extract hour if present
            hour_match = re.search(r'(\d{2}):\d{2}:\d{2}', line)
            if hour_match:
                hour = int(hour_match.group(1))
                time_analysis["hourly_distribution"][hour] += 1
            
            # Extract date if present
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match:
                date = date_match.group(1)
                time_analysis["daily_distribution"][date] += 1
        
        # Find peak activity hours
        if time_analysis["hourly_distribution"]:
            sorted_hours = sorted(time_analysis["hourly_distribution"].items(), key=lambda x: x[1], reverse=True)
            time_analysis["peak_activity_hours"] = [
                {"hour": hour, "count": count} 
                for hour, count in sorted_hours[:5]
            ]
        
        return time_analysis
    
    def generate_report(self, format_type: str = "text") -> str:
        """
        Generate a formatted security report
        
        Args:
            format_type: "text" or "json"
        
        Returns:
            Formatted report string
        """
        if not self.analysis_results:
            self.analyze_security_events()
        
        if format_type == "json":
            return json.dumps(self.analysis_results, indent=2, default=str)
        
        # Text format
        results = self.analysis_results
        summary = results.get("summary", {})
        
        report = "=" * 60 + "\n"
        report += "+ **LOG ANALYSIS SECURITY REPORT**\n"
        report += "=" * 60 + "\n"
        report += f"+ Generated: {results.get('timestamp', 'Unknown')}\n"
        report += f"+ Log file: {results.get('log_file', 'Text input')}\n"
        report += f"+ Lines analyzed: {results.get('total_lines', 0)}\n\n"
        
        # Severity
        severity = summary.get("severity_score", 0)
        severity_level = "* CRITICAL" if severity >= 70 else "🟠 HIGH" if severity >= 40 else "🟡 MEDIUM" if severity >= 20 else "🟢 LOW"
        report += f"* Severity Score: {severity}/100 - {severity_level}\n\n"
        
        # Login attempts
        report += "# **Login Activity**\n"
        report += f"   • Failed logins: {summary.get('total_failed_logins', 0)}\n"
        report += f"   • Successful logins: {summary.get('total_successful_logins', 0)}\n\n"
        
        # Brute force attempts
        brute_force = results.get("brute_force_attempts", [])
        if brute_force:
            report += "+ **Potential Brute Force Attacks**\n"
            for attempt in brute_force:
                report += f"   • IP: {attempt['ip']} - {attempt['failed_count']} failures ({attempt['severity']})\n"
            report += "\n"
        
        # Attack patterns
        attack_patterns = results.get("attack_patterns", {})
        if attack_patterns:
            report += "+ **Detected Attack Patterns**\n"
            for pattern, count in attack_patterns.items():
                if count > 0:
                    report += f"   • {pattern}: {count}\n"
            report += "\n"
        
        # Errors
        errors = results.get("errors", [])
        if errors:
            report += "+ **Critical Errors** (first 5)\n"
            for error in errors[:5]:
                report += f"   • Line {error['line']}: {error['content'][:80]}...\n"
            report += "\n"
        
        # Suspicious IPs
        suspicious_ips = self.detect_suspicious_ips()
        if suspicious_ips:
            report += "# **Suspicious IP Addresses**\n"
            for ip_info in suspicious_ips[:5]:
                report += f"   • {ip_info['ip']} - Risk: {ip_info['risk_score']}%\n"
            report += "\n"
        
        report += "=" * 60 + "\n"
        report += "+ **Recommendations**\n"
        
        if severity >= 70:
            report += "   •  Immediate action required - investigate all suspicious activities\n"
            report += "   • Block malicious IP addresses\n"
            report += "   • Review security policies\n"
        elif severity >= 40:
            report += "   •  Increase monitoring on detected attack patterns\n"
            report += "   • Review failed login attempts\n"
        elif severity >= 20:
            report += "   •  Review logs regularly for anomalies\n"
            report += "   • Consider implementing additional security measures\n"
        else:
            report += "   •  Continue regular monitoring\n"
            report += "   • Maintain current security posture\n"
        
        report += "=" * 60 + "\n"
        
        return report
    
    def detect_web_attacks(self) -> Dict[str, Any]:
        """
        Detect web application attacks from logs
        
        Returns:
            Dictionary with web attack analysis
        """
        if not self.log_content:
            return {"error": "No log content loaded"}
        
        web_attacks = {
            "sql_injection": [],
            "xss_attempts": [],
            "path_traversal": [],
            "command_injection": [],
            "total_count": 0
        }
        
        lines = self.log_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # SQL Injection
            for pattern in self.PATTERNS["sql_injection"]:
                if re.search(pattern, line, re.IGNORECASE):
                    web_attacks["sql_injection"].append({
                        "line": line_num,
                        "content": line[:200]
                    })
                    web_attacks["total_count"] += 1
                    break
            
            # XSS attempts
            for pattern in self.PATTERNS["xss_attempt"]:
                if re.search(pattern, line, re.IGNORECASE):
                    web_attacks["xss_attempts"].append({
                        "line": line_num,
                        "content": line[:200]
                    })
                    web_attacks["total_count"] += 1
                    break
            
            # Path traversal
            for pattern in self.PATTERNS["path_traversal"]:
                if re.search(pattern, line, re.IGNORECASE):
                    web_attacks["path_traversal"].append({
                        "line": line_num,
                        "content": line[:200]
                    })
                    web_attacks["total_count"] += 1
                    break
            
            # Command injection
            for pattern in self.PATTERNS["command_injection"]:
                if re.search(pattern, line, re.IGNORECASE):
                    web_attacks["command_injection"].append({
                        "line": line_num,
                        "content": line[:200]
                    })
                    web_attacks["total_count"] += 1
                    break
        
        return web_attacks
    
    def find_common_log_sources(self) -> List[str]:
        """
        Find common log files on the system
        
        Returns:
            List of existing log file paths
        """
        existing_logs = []
        
        # Determine OS
        import platform
        os_type = platform.system().lower()
        
        if os_type == "windows":
            log_paths = self.COMMON_LOG_PATHS["windows"]
        else:
            log_paths = self.COMMON_LOG_PATHS["linux"]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                existing_logs.append(log_path)
        
        return existing_logs
    
    def analyze_system_logs(self) -> Dict[str, Any]:
        """
        Analyze common system logs automatically
        
        Returns:
            Combined analysis from found log files
        """
        log_files = self.find_common_log_sources()
        
        if not log_files:
            return {"error": "No common log files found"}
        
        combined_results = {
            "analyzed_files": log_files,
            "timestamp": datetime.now().isoformat(),
            "file_results": {}
        }
        
        for log_file in log_files:
            if self.load_log_file(log_file):
                results = self.analyze_security_events()
                combined_results["file_results"][log_file] = {
                    "severity": results.get("summary", {}).get("severity_score", 0),
                    "failed_logins": results.get("summary", {}).get("total_failed_logins", 0),
                    "brute_force": len(results.get("brute_force_attempts", []))
                }
        
        return combined_results


# Standalone functions for easy access
def analyze_log_file(file_path: str) -> Dict[str, Any]:
    """
    Quick log file analysis
    
    Args:
        file_path: Path to log file
    
    Returns:
        Analysis results
    """
    analyzer = LogAnalyzer()
    if analyzer.load_log_file(file_path):
        return analyzer.analyze_security_events()
    return {"error": f"Could not load {file_path}"}


def analyze_log_text(log_text: str) -> Dict[str, Any]:
    """
    Quick analysis of log text
    
    Args:
        log_text: Log content as string
    
    Returns:
        Analysis results
    """
    analyzer = LogAnalyzer()
    analyzer.load_from_text(log_text)
    return analyzer.analyze_security_events()


def get_log_report(file_path: str) -> str:
    """
    Generate a formatted report from log file
    
    Args:
        file_path: Path to log file
    
    Returns:
        Formatted report string
    """
    analyzer = LogAnalyzer()
    if analyzer.load_log_file(file_path):
        analyzer.analyze_security_events()
        return analyzer.generate_report()
    return f"❌ Error: Could not load {file_path}"


# Tool registry for the AI agent
LOG_TOOLS = {
    "analyze_file": analyze_log_file,
    "analyze_text": analyze_log_text,
    "generate_report": get_log_report,
    "find_logs": LogAnalyzer().find_common_log_sources
}