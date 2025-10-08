#!/usr/bin/env python3
"""
Process Manager for Synbi Assistant
Allows listing and killing processes through voice commands
"""

import psutil
import re
from typing import List, Dict, Optional

class ProcessManager:
    """Process management utility for Synbi assistant"""
    
    def __init__(self):
        self.process_cache = {}
        self.last_refresh = 0
        self.cache_duration = 5  # Cache for 5 seconds
        
        # Common app name mappings
        self.app_mappings = {
            'chrome': ['chrome', 'google chrome', 'chrome browser'],
            'firefox': ['firefox', 'mozilla firefox', 'firefox browser'],
            'edge': ['edge', 'microsoft edge', 'edge browser'],
            'spotify': ['spotify', 'spotify music'],
            'notepad': ['notepad', 'notepad++', 'notepad plus plus'],
            'calculator': ['calculator', 'calc', 'windows calculator'],
            'word': ['word', 'microsoft word', 'winword'],
            'excel': ['excel', 'microsoft excel'],
            'powerpoint': ['powerpoint', 'microsoft powerpoint', 'ppt'],
            'vscode': ['vscode', 'visual studio code', 'code'],
            'discord': ['discord'],
            'teams': ['teams', 'microsoft teams'],
            'zoom': ['zoom', 'zoom meetings'],
            'skype': ['skype'],
            'whatsapp': ['whatsapp', 'whatsapp desktop'],
            'telegram': ['telegram', 'telegram desktop'],
            'vlc': ['vlc', 'vlc media player'],
            'photoshop': ['photoshop', 'adobe photoshop'],
            'illustrator': ['illustrator', 'adobe illustrator'],
            'premiere': ['premiere', 'adobe premiere'],
            'obs': ['obs', 'obs studio'],
            'steam': ['steam'],
            'epic': ['epic', 'epic games launcher'],
            'origin': ['origin', 'ea app'],
            'battle': ['battle.net', 'battlenet'],
            'minecraft': ['minecraft', 'minecraft launcher'],
            'roblox': ['roblox'],
            'fortnite': ['fortnite'],
            'valorant': ['valorant'],
            'league': ['league of legends', 'lol'],
            'dota': ['dota 2'],
            'csgo': ['csgo', 'counter-strike'],
            'pubg': ['pubg', 'playerunknowns battlegrounds']
        }
    
    def normalize_app_name(self, app_name: str) -> str:
        """Normalize app name to match common process names"""
        app_name = app_name.lower().strip()
        
        # Check if the app name matches any of our mappings
        for standard_name, variations in self.app_mappings.items():
            if app_name in variations:
                return standard_name
        
        # If no mapping found, return the original name
        return app_name
    
    def get_all_processes(self, refresh_cache: bool = False) -> List[Dict]:
        """Get all running processes with their details"""
        import time
        
        current_time = time.time()
        
        # Use cache if available and not expired
        if not refresh_cache and self.process_cache and (current_time - self.last_refresh) < self.cache_duration:
            return self.process_cache.get('processes', [])
        
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
                try:
                    proc_info = proc.info
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent'],
                        'status': proc_info['status'],
                        'create_time': proc_info['create_time']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            # Update cache
            self.process_cache = {'processes': processes, 'timestamp': current_time}
            self.last_refresh = current_time
                    
        except Exception as e:
            print(f"Error getting processes: {e}")
            return []
        
        return processes
    
    def list_processes(self, limit: int = 20, sort_by: str = 'cpu') -> str:
        """List running processes in a formatted string"""
        processes = self.get_all_processes()
        
        if not processes:
            return "No processes found or access denied."
        
        # Sort processes
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x['name'].lower())
        
        # Format output
        result = f"📊 Running Processes (Top {min(limit, len(processes))} by {sort_by}):\n"
        result += "=" * 80 + "\n"
        result += f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'Memory%':<10} {'Status':<12}\n"
        result += "-" * 80 + "\n"
        
        for proc in processes[:limit]:
            name = proc['name'][:24]  # Truncate long names
            cpu = f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] is not None else "N/A"
            memory = f"{proc['memory_percent']:.1f}" if proc['memory_percent'] is not None else "N/A"
            status = proc['status'][:11]  # Truncate long status
            
            result += f"{proc['pid']:<8} {name:<25} {cpu:<8} {memory:<10} {status:<12}\n"
        
        return result
    
    def find_processes_by_name(self, name_pattern: str) -> List[Dict]:
        """Find processes matching a name pattern"""
        processes = self.get_all_processes()
        matching_processes = []
        
        # Create case-insensitive regex pattern
        pattern = re.compile(re.escape(name_pattern), re.IGNORECASE)
        
        for proc in processes:
            if pattern.search(proc['name']):
                matching_processes.append(proc)
        
        return matching_processes
    
    def kill_process_by_name(self, name_pattern: str, force: bool = False) -> Dict:
        """Kill processes matching a name pattern"""
        # Normalize the app name first
        normalized_name = self.normalize_app_name(name_pattern)
        matching_processes = self.find_processes_by_name(normalized_name)
        
        if not matching_processes:
            return {
                'success': False,
                'message': f"{name_pattern.title()} is not running",
                'killed_count': 0
            }
        
        killed_count = 0
        failed_processes = []
        
        for proc in matching_processes:
            try:
                process = psutil.Process(proc['pid'])
                
                if force:
                    process.kill()  # Force kill
                else:
                    process.terminate()  # Graceful termination
                
                killed_count += 1
                print(f"✅ Killed process: {proc['name']} (PID: {proc['pid']})")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                failed_processes.append(f"{proc['name']} (PID: {proc['pid']}): {str(e)}")
                print(f"❌ Failed to kill {proc['name']} (PID: {proc['pid']}): {e}")
        
        # Clear cache after killing processes
        self.process_cache = {}
        
        if killed_count > 0:
            # Simple, user-friendly message
            message = f"{name_pattern.title()} is closed"
            if failed_processes:
                message += f" (Some processes couldn't be closed)"
        else:
            message = f"Could not close {name_pattern.title()}"
        
        return {
            'success': killed_count > 0,
            'message': message,
            'killed_count': killed_count,
            'failed': failed_processes
        }
    
    def kill_process_by_pid(self, pid: int, force: bool = False) -> Dict:
        """Kill a process by its PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if force:
                process.kill()
            else:
                process.terminate()
                
            # Clear cache
            self.process_cache = {}
            
            return {
                'success': True,
                'message': f"{process_name} is closed",
                'killed_count': 1
            }
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'success': False,
                'message': f"Could not close process with PID {pid}",
                'killed_count': 0
            }
    
    def get_process_info(self, name_pattern: str) -> str:
        """Get detailed information about processes matching a name pattern"""
        matching_processes = self.find_processes_by_name(name_pattern)
        
        if not matching_processes:
            return f"No processes found matching '{name_pattern}'"
        
        result = f"🔍 Process Information for '{name_pattern}':\n"
        result += "=" * 60 + "\n"
        
        for proc in matching_processes:
            result += f"Name: {proc['name']}\n"
            result += f"PID: {proc['pid']}\n"
            result += f"CPU Usage: {proc['cpu_percent']:.1f}%\n"
            result += f"Memory Usage: {proc['memory_percent']:.1f}%\n"
            result += f"Status: {proc['status']}\n"
            result += "-" * 40 + "\n"
        
        return result
    
    def get_system_info(self) -> str:
        """Get system resource information"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024**3)  # Convert to GB
            memory_used = memory.used / (1024**3)
            memory_percent = memory.percent
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)
            disk_used = disk.used / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            
            result = "🖥️ System Resource Information:\n"
            result += "=" * 40 + "\n"
            result += f"CPU Usage: {cpu_percent:.1f}% ({cpu_count} cores)\n"
            result += f"Memory: {memory_used:.1f}GB / {memory_total:.1f}GB ({memory_percent:.1f}%)\n"
            result += f"Disk: {disk_used:.1f}GB / {disk_total:.1f}GB ({disk_percent:.1f}%)\n"
            
            return result
        
        except Exception as e:
            return f"Error getting system info: {e}"

# Create a global instance
process_manager = ProcessManager()

# Convenience functions for easy importing
def list_processes(limit=20, sort_by='cpu'):
    """List running processes"""
    return process_manager.list_processes(limit, sort_by)

def kill_process_by_name(name_pattern, force=False):
    """Kill processes by name pattern"""
    return process_manager.kill_process_by_name(name_pattern, force)

def kill_process_by_pid(pid, force=False):
    """Kill process by PID"""
    return process_manager.kill_process_by_pid(pid, force)

def get_process_info(name_pattern):
    """Get process information"""
    return process_manager.get_process_info(name_pattern)

def get_system_info():
    """Get system resource information"""
    return process_manager.get_system_info()

def find_processes(name_pattern):
    """Find processes by name pattern"""
    return process_manager.find_processes_by_name(name_pattern)

def normalize_app_name(app_name):
    """Normalize app name for better matching"""
    return process_manager.normalize_app_name(app_name)