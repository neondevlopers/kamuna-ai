import os
import platform
import subprocess
from typing import Dict, List
from logger import logger

class SecurityChecks:
    @staticmethod
    def check_system_security() -> Dict:
        """Perform basic system security checks"""
        results = {
            "os": platform.system(),
            "os_version": platform.version(),
            "security_issues": [],
            "recommendations": []
        }
        
        # Check for common security issues
        if platform.system() == "Windows":
            # Check Windows Defender status (simplified)
            try:
                result = subprocess.run('powershell Get-MpComputerStatus', shell=True, capture_output=True, text=True, timeout=5)
                if "True" in result.stdout:
                    results["antivirus"] = "Windows Defender is active"
                else:
                    results["security_issues"].append("Windows Defender may not be active")
                    results["recommendations"].append("Enable Windows Defender or install antivirus")
            except:
                pass
        
        # Check for suspicious processes (basic)
        suspicious_names = ["nc.exe", "ncat", "meterpreter", "nc"]
        try:
            if platform.system() == "Windows":
                result = subprocess.run('tasklist', shell=True, capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run('ps aux', shell=True, capture_output=True, text=True, timeout=5)
            
            for proc in suspicious_names:
                if proc.lower() in result.stdout.lower():
                    results["security_issues"].append(f"Suspicious process detected: {proc}")
                    results["recommendations"].append(f"Investigate process containing '{proc}'")
        except Exception as e:
            logger.error(f"Process check failed: {e}")
        
        return results
    
    @staticmethod
    def check_file_permissions(path: str) -> Dict:
        """Check file permissions for security issues"""
        results = {
            "path": path,
            "exists": os.path.exists(path),
            "permissions": {},
            "issues": []
        }
        
        if results["exists"]:
            if platform.system() != "Windows":
                import stat
                st = os.stat(path)
                results["permissions"] = {
                    "owner_read": bool(st.st_mode & stat.S_IRUSR),
                    "owner_write": bool(st.st_mode & stat.S_IWUSR),
                    "group_read": bool(st.st_mode & stat.S_IRGRP),
                    "group_write": bool(st.st_mode & stat.S_IWGRP),
                    "others_read": bool(st.st_mode & stat.S_IROTH),
                    "others_write": bool(st.st_mode & stat.S_IWOTH)
                }
                
                if results["permissions"]["others_write"]:
                    results["issues"].append("World-writable file - security risk")
                if results["permissions"]["others_read"] and "password" in path.lower():
                    results["issues"].append("Sensitive file readable by others")
        
        return results