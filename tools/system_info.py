"""
System Information Module - Provides system diagnostics and hardware information
For educational and monitoring purposes only
"""

import os
import sys
import platform
import subprocess
import psutil
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from logger import logger


class SystemInfo:
    """
    System information gathering tools
    Provides hardware, OS, and resource usage information
    """
    
    @staticmethod
    def get_system_basics() -> Dict[str, Any]:
        """
        Get basic system information
        
        Returns:
            Dictionary with basic system info
        """
        info = {
            "timestamp": datetime.now().isoformat(),
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "hostname": platform.node(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "system_uptime": None
        }
        
        # Get uptime
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            info["system_uptime"] = f"{days}d {hours}h {minutes}m"
        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            info["system_uptime"] = "Unknown"
        
        return info
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """
        Get CPU information and usage
        
        Returns:
            Dictionary with CPU info
        """
        info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "max_frequency": None,
            "current_frequency": None,
            "usage_per_core": [],
            "total_usage": 0,
            "load_average": None
        }
        
        # CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                info["max_frequency"] = f"{freq.max:.2f} MHz" if freq.max else "Unknown"
                info["current_frequency"] = f"{freq.current:.2f} MHz" if freq.current else "Unknown"
        except Exception as e:
            logger.error(f"Error getting CPU frequency: {e}")
        
        # CPU usage per core
        try:
            info["usage_per_core"] = [f"{perc}%" for perc in psutil.cpu_percent(perc=True)]
            info["total_usage"] = f"{psutil.cpu_percent()}%"
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
        
        # Load average (Unix only)
        if hasattr(psutil, 'getloadavg'):
            try:
                load_avg = psutil.getloadavg()
                info["load_average"] = {
                    "1min": f"{load_avg[0]:.2f}",
                    "5min": f"{load_avg[1]:.2f}",
                    "15min": f"{load_avg[2]:.2f}"
                }
            except Exception:
                pass
        
        return info
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """
        Get memory (RAM) information
        
        Returns:
            Dictionary with memory info
        """
        info = {
            "total": None,
            "available": None,
            "used": None,
            "percentage": 0,
            "swap_total": None,
            "swap_used": None,
            "swap_percentage": 0
        }
        
        try:
            # Virtual memory
            mem = psutil.virtual_memory()
            info["total"] = SystemInfo._bytes_to_human(mem.total)
            info["available"] = SystemInfo._bytes_to_human(mem.available)
            info["used"] = SystemInfo._bytes_to_human(mem.used)
            info["percentage"] = mem.percent
            
            # Swap memory
            swap = psutil.swap_memory()
            info["swap_total"] = SystemInfo._bytes_to_human(swap.total)
            info["swap_used"] = SystemInfo._bytes_to_human(swap.used)
            info["swap_percentage"] = swap.percent
            
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
        
        return info
    
    @staticmethod
    def get_disk_info() -> List[Dict[str, Any]]:
        """
        Get disk partition information
        
        Returns:
            List of dictionaries with disk info
        """
        disks = []
        
        try:
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": SystemInfo._bytes_to_human(usage.total),
                        "used": SystemInfo._bytes_to_human(usage.used),
                        "free": SystemInfo._bytes_to_human(usage.free),
                        "percentage": usage.percent
                    }
                    disks.append(disk_info)
                except PermissionError:
                    # Skip partitions without permission
                    continue
                except Exception as e:
                    logger.error(f"Error getting disk usage for {partition.mountpoint}: {e}")
                    
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
        
        return disks
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """
        Get network interface information
        
        Returns:
            Dictionary with network info
        """
        info = {
            "interfaces": [],
            "connections": None,
            "bytes_sent": None,
            "bytes_recv": None
        }
        
        try:
            # Network interfaces
            net_if_addrs = psutil.net_if_addrs()
            
            for interface_name, addresses in net_if_addrs.items():
                interface_info = {"name": interface_name, "addresses": []}
                
                for addr in addresses:
                    address_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask if addr.netmask else "None",
                        "broadcast": addr.broadcast if addr.broadcast else "None"
                    }
                    interface_info["addresses"].append(address_info)
                
                info["interfaces"].append(interface_info)
            
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            info["bytes_sent"] = SystemInfo._bytes_to_human(net_io.bytes_sent)
            info["bytes_recv"] = SystemInfo._bytes_to_human(net_io.bytes_recv)
            info["packets_sent"] = net_io.packets_sent
            info["packets_recv"] = net_io.packets_recv
            info["errin"] = net_io.errin
            info["errout"] = net_io.errout
            info["dropin"] = net_io.dropin
            info["dropout"] = net_io.dropout
            
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
        
        return info
    
    @staticmethod
    def get_process_info(top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top processes by memory/CPU usage
        
        Args:
            top_n: Number of top processes to return
        
        Returns:
            List of dictionaries with process info
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "cpu_percent": proc_info['cpu_percent'] or 0,
                        "memory_percent": proc_info['memory_percent'] or 0,
                        "status": proc_info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get top N
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            processes = processes[:top_n]
            
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
        
        return processes
    
    @staticmethod
    def get_system_services() -> List[Dict[str, Any]]:
        """
        Get running system services
        
        Returns:
            List of dictionaries with service info
        """
        services = []
        
        try:
            if platform.system() == "Windows":
                # Windows services
                cmd = 'powershell "Get-Service | Where-Object {$_.Status -eq \'Running\'} | Select-Object Name, DisplayName, Status"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                lines = result.stdout.split('\n')
                for line in lines[3:]:  # Skip headers
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            services.append({
                                "name": parts[0],
                                "display_name": " ".join(parts[1:-1]) if len(parts) > 2 else parts[0],
                                "status": "Running"
                            })
            else:
                # Linux services (systemctl)
                cmd = "systemctl list-units --type=service --state=running --no-pager --no-legend"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            services.append({
                                "name": parts[0],
                                "status": "Running"
                            })
                            
        except Exception as e:
            logger.error(f"Error getting services: {e}")
        
        return services[:20]  # Limit to 20 services
    
    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """
        Get environment variables (filtered for security)
        
        Returns:
            Dictionary of filtered environment variables
        """
        # Filter sensitive variables
        sensitive_keys = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'AUTH']
        filtered_vars = {}
        
        for key, value in os.environ.items():
            # Skip sensitive variables
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                filtered_vars[key] = "*** HIDDEN ***"
            else:
                # Truncate long values
                if len(value) > 100:
                    filtered_vars[key] = value[:100] + "..."
                else:
                    filtered_vars[key] = value
        
        return filtered_vars
    
    @staticmethod
    def get_all_system_info() -> Dict[str, Any]:
        """
        Get comprehensive system information
        
        Returns:
            Dictionary with all system info
        """
        all_info = {
            "basics": SystemInfo.get_system_basics(),
            "cpu": SystemInfo.get_cpu_info(),
            "memory": SystemInfo.get_memory_info(),
            "disks": SystemInfo.get_disk_info(),
            "network": SystemInfo.get_network_info(),
            "top_processes": SystemInfo.get_process_info(10),
            "environment_vars": SystemInfo.get_environment_variables()
        }
        
        return all_info
    
    @staticmethod
    def _bytes_to_human(bytes_value: int) -> str:
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
    
    @staticmethod
    def format_basic_info(info: Dict[str, Any]) -> str:
        """
        Format basic system info for display
        
        Args:
            info: Basic system info dictionary
        
        Returns:
            Formatted string
        """
        output = f" * **System Information**\n"
        output += f"* Time: {info.get('timestamp', 'Unknown')}\n"
        output += f"* OS: {info.get('os', 'Unknown')} {info.get('os_release', '')}\n"
        output += f"* Hostname: {info.get('hostname', 'Unknown')}\n"
        output += f"* Architecture: {info.get('architecture', 'Unknown')}\n"
        output += f"* Uptime: {info.get('system_uptime', 'Unknown')}\n"
        output += f"* Python: {info.get('python_version', 'Unknown').split()[0]}\n"
        
        return output
    
    @staticmethod
    def format_cpu_info(info: Dict[str, Any]) -> str:
        """
        Format CPU info for display
        
        Args:
            info: CPU info dictionary
        
        Returns:
            Formatted string
        """
        output = f"+ **CPU Information**\n"
        output += f"+ Physical cores: {info.get('physical_cores', 'Unknown')}\n"
        output += f"+ Logical cores: {info.get('logical_cores', 'Unknown')}\n"
        output += f"+ Max frequency: {info.get('max_frequency', 'Unknown')}\n"
        output += f"+ Total usage: {info.get('total_usage', 'Unknown')}\n"
        
        usage_per_core = info.get('usage_per_core', [])
        if usage_per_core:
            output += f"+ Per-core usage: {', '.join(usage_per_core)}\n"
        
        load_avg = info.get('load_average')
        if load_avg:
            output += f"+ Load average: 1m={load_avg.get('1min', '0')} 5m={load_avg.get('5min', '0')} 15m={load_avg.get('15min', '0')}\n"
        
        return output
    
    @staticmethod
    def format_memory_info(info: Dict[str, Any]) -> str:
        """
        Format memory info for display
        
        Args:
            info: Memory info dictionary
        
        Returns:
            Formatted string
        """
        output = f"+ **Memory Information**\n"
        output += f"+ Total RAM: {info.get('total', 'Unknown')}\n"
        output += f"+ Used RAM: {info.get('used', 'Unknown')} ({info.get('percentage', 0)}%)\n"
        output += f"+ Available RAM: {info.get('available', 'Unknown')}\n"
        output += f"+ Swap total: {info.get('swap_total', 'Unknown')}\n"
        output += f"+ Swap used: {info.get('swap_used', 'Unknown')} ({info.get('swap_percentage', 0)}%)\n"
        
        return output
    
    @staticmethod
    def format_disk_info(disks: List[Dict[str, Any]]) -> str:
        """
        Format disk info for display
        
        Args:
            disks: List of disk info dictionaries
        
        Returns:
            Formatted string
        """
        if not disks:
            return "+ No disk information available.\n"
        
        output = f"+ **Disk Information**\n"
        for disk in disks:
            output += f"+ {disk.get('device', 'Unknown')} ({disk.get('mountpoint', 'Unknown')})\n"
            output += f"   Total: {disk.get('total', 'Unknown')} | Used: {disk.get('used', 'Unknown')} ({disk.get('percentage', 0)}%)\n"
            output += f"   Free: {disk.get('free', 'Unknown')} | FS: {disk.get('filesystem', 'Unknown')}\n"
        
        return output
    
    @staticmethod
    def format_complete_report(all_info: Dict[str, Any]) -> str:
        """
        Format complete system report for display
        
        Args:
            all_info: Complete system info dictionary
        
        Returns:
            Formatted string
        """
        output = "=" * 50 + "\n"
        output += "+ **COMPLETE SYSTEM REPORT**\n"
        output += "=" * 50 + "\n\n"
        
        # Basic info
        output += SystemInfo.format_basic_info(all_info.get("basics", {}))
        output += "\n"
        
        # CPU info
        output += SystemInfo.format_cpu_info(all_info.get("cpu", {}))
        output += "\n"
        
        # Memory info
        output += SystemInfo.format_memory_info(all_info.get("memory", {}))
        output += "\n"
        
        # Disk info
        output += SystemInfo.format_disk_info(all_info.get("disks", []))
        output += "\n"
        
        # Network info
        network = all_info.get("network", {})
        output += f"+ **Network Information**\n"
        output += f"+ Bytes sent: {network.get('bytes_sent', 'Unknown')}\n"
        output += f"+ Bytes received: {network.get('bytes_recv', 'Unknown')}\n"
        output += f"+ Packets sent: {network.get('packets_sent', 0)}\n"
        output += f"+ Packets received: {network.get('packets_recv', 0)}\n"
        output += "\n"
        
        # Top processes
        processes = all_info.get("top_processes", [])
        if processes:
            output += f"+ **Top {len(processes)} Processes (by CPU)**\n"
            for proc in processes:
                output += f"   • {proc.get('name', 'Unknown')} (PID: {proc.get('pid', 'N/A')}) - CPU: {proc.get('cpu_percent', 0)}% | MEM: {proc.get('memory_percent', 0):.1f}%\n"
        
        output += "\n" + "=" * 50 + "\n"
        
        return output


# Standalone functions for easy access
def quick_system_check() -> Dict[str, Any]:
    """Run a quick system check"""
    return SystemInfo.get_all_system_info()


def get_system_summary() -> str:
    """Get a formatted system summary"""
    info = SystemInfo.get_all_system_info()
    return SystemInfo.format_complete_report(info)


# Tool registry for the AI agent
SYSTEM_TOOLS = {
    "full_report": SystemInfo.get_all_system_info,
    "quick_check": quick_system_check,
    "summary": get_system_summary,
    "cpu_info": SystemInfo.get_cpu_info,
    "memory_info": SystemInfo.get_memory_info,
    "disk_info": SystemInfo.get_disk_info,
    "network_info": SystemInfo.get_network_info,
    "processes": SystemInfo.get_process_info
}