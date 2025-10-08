import os
import time
import subprocess
import psutil
import pyautogui
import glob
import win32gui
import win32con
from pathlib import Path

class WhatsAppHandler:
    """Consolidated WhatsApp Desktop handler with enhanced reliability"""
    
    def __init__(self):
        self.whatsapp_path = None
        self.window_handle = None
        self.process_names = [
            'whatsapp.exe',
            'whatsappdesktop.exe', 
            'whatsapp',
            'WhatsApp.exe',
            'WhatsAppDesktop.exe'
        ]
        
    def find_whatsapp_installation(self):
        """Enhanced WhatsApp installation detection with multiple methods"""
        print("🔍 Searching for WhatsApp installation...")
        
        # Check if already found and cached
        if self.whatsapp_path and os.path.exists(self.whatsapp_path):
            print(f"✅ Using cached WhatsApp path: {self.whatsapp_path}")
            return self.whatsapp_path
        
        # Method 1: Get path from running process (most reliable)
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                    if 'whatsapp.exe' in proc_name:
                        exe_path = proc.info.get('exe')
                        if exe_path and os.path.exists(exe_path):
                            print(f"✅ Found WhatsApp (Running process): {exe_path}")
                            self.whatsapp_path = exe_path
                            return exe_path
                except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
                    continue
        except Exception as e:
            print(f"Error checking running processes: {e}")
        
        # Method 2: Windows Store version paths (most common)
        store_patterns = [
            "C:/Program Files/WindowsApps/5319275A.WhatsAppDesktop_*/WhatsApp.exe",
            "C:/Program Files/WindowsApps/*WhatsApp*/WhatsApp.exe",
            "C:/Program Files/WindowsApps/*/WhatsApp.exe"
        ]
        
        for pattern in store_patterns:
            try:
                matches = glob.glob(pattern)
                if matches:
                    path = matches[0]
                    print(f"✅ Found WhatsApp (Store version): {path}")
                    self.whatsapp_path = path
                    return path
            except Exception as e:
                print(f"Error checking pattern {pattern}: {e}")
        
        # Method 3: Traditional installation paths
        traditional_paths = [
            os.path.expanduser("~/AppData/Local/WhatsApp/WhatsApp.exe"),
            os.path.expanduser("~/AppData/Roaming/WhatsApp/WhatsApp.exe"),
            "C:/Program Files/WhatsApp/WhatsApp.exe",
            "C:/Program Files (x86)/WhatsApp/WhatsApp.exe",
            os.path.expanduser("~/AppData/Local/Programs/WhatsApp/WhatsApp.exe")
        ]
        
        for path in traditional_paths:
            try:
                if os.path.exists(path):
                    print(f"✅ Found WhatsApp (Traditional): {path}")
                    self.whatsapp_path = path
                    return path
            except Exception as e:
                print(f"Error checking path {path}: {e}")
        
        # Method 4: Registry search (Windows Store apps)
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages")
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    if "whatsapp" in subkey_name.lower():
                        # Try to find the actual executable
                        app_path = f"C:/Program Files/WindowsApps/{subkey_name}"
                        for exe_name in ["WhatsApp.exe", "whatsapp.exe"]:
                            full_path = os.path.join(app_path, exe_name)
                            if os.path.exists(full_path):
                                print(f"✅ Found WhatsApp (Registry): {full_path}")
                                self.whatsapp_path = full_path
                                winreg.CloseKey(key)
                                return full_path
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Registry search failed: {e}")
        
        print("❌ WhatsApp installation not found")
        return None
    
    def is_whatsapp_running(self):
        """Check if WhatsApp desktop app is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ""
                    
                    # Check process name and executable path
                    for name in self.process_names:
                        if (name.lower() in proc_name or 
                            (proc_exe and name.lower() in os.path.basename(proc_exe))):
                            print(f"✅ WhatsApp process found: {proc.info['name']} (PID: {proc.info['pid']})")
                            return proc.info['pid']
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
                    continue
            
            print("❌ WhatsApp process not found")
            return None
            
        except Exception as e:
            print(f"Error checking WhatsApp process: {e}")
            return None
    
    def get_whatsapp_window(self):
        """Find and return WhatsApp window handle"""
        try:
            def enum_windows_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd).lower()
                        class_name = win32gui.GetClassName(hwnd).lower()
                        
                        # Check for WhatsApp window patterns
                        whatsapp_indicators = [
                            'whatsapp',
                            'whatsapp desktop',
                            'whatsapp - chrome',  # For web version in Chrome
                        ]
                        
                        for indicator in whatsapp_indicators:
                            if indicator in window_text:
                                print(f"✅ Found WhatsApp window: '{window_text}' (Class: {class_name})")
                                windows.append(hwnd)
                                return False  # Stop enumeration
                                
                except Exception as e:
                    pass
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                self.window_handle = windows[0]
                return windows[0]
            
            print("❌ WhatsApp window not found")
            return None
            
        except Exception as e:
            print(f"Error enumerating windows: {e}")
            return None
    
    def focus_whatsapp_window(self):
        """Focus on WhatsApp window with enhanced reliability and multiple fallbacks"""
        try:
            print("🎯 Focusing WhatsApp window...")
            
            # Method 1: Try to find and focus existing window
            if not self.window_handle:
                self.window_handle = self.get_whatsapp_window()
            
            if self.window_handle:
                print("📍 Using window handle method...")
                # Multiple methods to ensure window focus
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                time.sleep(0.5)
                win32gui.SetForegroundWindow(self.window_handle)
                time.sleep(0.5)
                win32gui.BringWindowToTop(self.window_handle)
                time.sleep(1)
                
                # Verify window is focused
                focused_window = win32gui.GetForegroundWindow()
                if focused_window == self.window_handle:
                    print("✅ WhatsApp window focused successfully (Method 1)")
                    return True
                else:
                    print("⚠️ Window handle method uncertain, trying alternatives...")
            
            # Method 2: Try Alt+Tab to cycle through windows
            print("🔄 Trying Alt+Tab method...")
            try:
                for _ in range(5):  # Try up to 5 times
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(1)
                    
                    # Check if WhatsApp is now focused
                    current_window = win32gui.GetForegroundWindow()
                    window_title = win32gui.GetWindowText(current_window).lower()
                    if 'whatsapp' in window_title:
                        print("✅ WhatsApp window focused successfully (Method 2)")
                        self.window_handle = current_window
                        return True
            except Exception as e:
                print(f"Alt+Tab method failed: {e}")
            
            # Method 3: Try clicking on taskbar WhatsApp icon
            print("📱 Trying taskbar click method...")
            try:
                # This is a simplified approach - in practice, you'd need to find the taskbar icon
                # For now, we'll use a combination of methods
                pyautogui.hotkey('win', 'tab')  # Open task view
                time.sleep(1)
                pyautogui.press('escape')  # Close task view
                time.sleep(0.5)
                
                # Try to find WhatsApp in the taskbar by pressing Win key and typing
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.typewrite('whatsapp')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)
                
                print("✅ WhatsApp launched/focused via Start menu (Method 3)")
                return True
            except Exception as e:
                print(f"Taskbar method failed: {e}")
            
            # Method 4: Try to launch WhatsApp if not running
            print("🚀 Trying to launch WhatsApp...")
            if not self.is_whatsapp_running():
                if self.launch_whatsapp():
                    print("✅ WhatsApp launched and should be focused")
                    return True
                else:
                    print("❌ Could not launch WhatsApp")
                    return False
            
            # Method 5: Last resort - try to find any WhatsApp window
            print("🔍 Last resort: searching for any WhatsApp window...")
            try:
                def find_whatsapp_callback(hwnd, windows):
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd).lower()
                            if 'whatsapp' in window_text:
                                windows.append(hwnd)
                    except:
                        pass
                    return True
                
                windows = []
                win32gui.EnumWindows(find_whatsapp_callback, windows)
                
                if windows:
                    hwnd = windows[0]
                    win32gui.SetForegroundWindow(hwnd)
                    self.window_handle = hwnd
                    print("✅ WhatsApp window found and focused (Method 5)")
                    return True
            except Exception as e:
                print(f"Last resort method failed: {e}")
            
            print("❌ All focus methods failed")
            return False
                
        except Exception as e:
            print(f"Error in focus_whatsapp_window: {e}")
            return False
    
    def launch_whatsapp(self):
        """Enhanced WhatsApp launching with multiple methods"""
        print("🚀 Launching WhatsApp...")
        
        # Check if already running
        if self.is_whatsapp_running():
            print("✅ WhatsApp is already running")
            if self.focus_whatsapp_window():
                return True
        
        # Find WhatsApp if not already found
        if not self.whatsapp_path:
            self.find_whatsapp_installation()
        
        # Method 1: Direct executable launch
        if self.whatsapp_path and os.path.exists(self.whatsapp_path):
            try:
                print(f"🚀 Launching from: {self.whatsapp_path}")
                subprocess.Popen([self.whatsapp_path])
                print("⏳ Waiting for WhatsApp to start...")
                
                # Wait for WhatsApp to start
                max_wait = 30
                wait_time = 0
                while wait_time < max_wait:
                    if self.is_whatsapp_running():
                        print("✅ WhatsApp launched successfully")
                        time.sleep(3)  # Give it time to fully load
                        return self.focus_whatsapp_window()
                    time.sleep(1)
                    wait_time += 1
                
                print("❌ WhatsApp took too long to start")
                return False
                
            except Exception as e:
                print(f"Failed to launch WhatsApp directly: {e}")
        
        # Method 2: Try Windows Store app protocol
        try:
            print("🚀 Trying Windows Store app launch...")
            os.startfile("ms-windows-store://pdp/?ProductId=9NKSQGP7F2NH")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Store launch failed: {e}")
        
        # Method 3: Try start command
        try:
            print("🚀 Trying start command...")
            subprocess.run(['start', 'whatsapp://'], shell=True, check=True)
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Start command failed: {e}")
        
        print("❌ All launch methods failed")
        return False
    
    def search_contact(self, contact_name, timeout=10):
        """Search for a contact in WhatsApp with enhanced reliability"""
        print(f"🔍 Searching for contact: {contact_name}")
        
        try:
            # Ensure we're in the main WhatsApp window
            if not self.focus_whatsapp_window():
                print("❌ Cannot focus WhatsApp window for contact search")
                return False
            
            # Clear any existing search and start fresh
            print("🧹 Clearing any existing search...")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            
            # Clear search box completely
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.5)
            
            # Alternative: Press Escape to ensure we're not in search mode
            pyautogui.press('escape')
            time.sleep(0.5)
            
            # Start new search
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            
            # Type contact name with better error handling
            print(f"⌨️ Typing contact name: {contact_name}")
            for i, char in enumerate(contact_name):
                try:
                    pyautogui.typewrite(char)
                    time.sleep(0.08)  # Slightly faster but still reliable
                except Exception as e:
                    print(f"Error typing character '{char}' at position {i}: {e}")
                    continue
            
            # Wait for search results to appear
            print("⏳ Waiting for search results...")
            time.sleep(3)
            
            # Try to select the first result
            print("🎯 Selecting first search result...")
            
            # Method 1: Press Down arrow to highlight first result, then Enter
            pyautogui.press('down')  # Highlight first result
            time.sleep(0.8)
            pyautogui.press('enter')  # Select first result
            time.sleep(3)  # Wait longer for contact to be selected
            
            # Method 2: If Enter doesn't work, try clicking on first result
            # This is a fallback for cases where Enter doesn't select the contact
            try:
                # Click in the area where search results typically appear
                screen_width, screen_height = pyautogui.size()
                result_x = screen_width // 2
                result_y = screen_height // 2 - 100  # Above center
                pyautogui.click(result_x, result_y)
                time.sleep(1)
            except Exception as e:
                print(f"Click fallback failed: {e}")
            
            # Don't exit search box - just ensure contact is selected
            print("✅ Contact selected, ready for message typing")
            return True
            
        except Exception as e:
            print(f"❌ Contact search failed: {e}")
            return False
    
    def send_message(self, message):
        """Send a message in the currently active chat"""
        print(f"💬 Sending message: {message[:50]}...")
        
        try:
            # Get screen dimensions for dynamic positioning
            screen_width, screen_height = pyautogui.size()
            
            # Calculate message input area based on screen size
            # WhatsApp message input is typically at the bottom of the window
            message_x = screen_width // 2  # Center horizontally
            message_y = screen_height - 100  # Near bottom of screen
            
            # Try multiple positions for message input
            message_positions = [
                (message_x, message_y),
                (message_x, message_y - 50),
                (message_x, message_y - 100),
                (screen_width // 2, screen_height - 150),
                (400, screen_height - 100)  # Fallback to original position
            ]
            
            # Start typing directly after contact selection
            print("💬 Starting to type message directly...")
            
            # First, press Enter to confirm we're in the chat (in case we're still in search)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Type message directly
            for char in message:
                try:
                    if char == '\n':
                        pyautogui.hotkey('shift', 'enter')
                    else:
                        pyautogui.typewrite(char)
                    time.sleep(0.03)  # Slightly faster typing
                except Exception as e:
                    print(f"Error typing character '{char}': {e}")
                    continue
            
            time.sleep(1)
            
            # Send message
            print("📤 Sending message...")
            pyautogui.press('enter')
            time.sleep(2)
            
            print("✅ Message sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Message sending failed: {e}")
            return False
    
    def _exit_search_mode(self):
        """Exit search mode to ensure we can type in message area"""
        try:
            print("🔍 Exiting search mode...")
            
            # Method 1: Press Escape multiple times to close search
            for _ in range(5):  # More attempts
                pyautogui.press('escape')
                time.sleep(0.3)
            
            # Method 2: Clear any text in search box and close it
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            pyautogui.press('escape')
            time.sleep(0.3)
            
            # Method 3: Click in chat area to exit search
            screen_width, screen_height = pyautogui.size()
            chat_x = screen_width // 2
            chat_y = screen_height // 2
            pyautogui.click(chat_x, chat_y)
            time.sleep(0.5)
            
            # Method 4: Use Ctrl+F to toggle search off completely
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.3)
            pyautogui.press('escape')
            time.sleep(0.3)
            
            # Method 5: Click in message area to ensure focus
            message_x = screen_width // 2
            message_y = screen_height - 100
            pyautogui.click(message_x, message_y)
            time.sleep(0.5)
            
            print("✅ Search mode exited")
            
        except Exception as e:
            print(f"⚠️ Could not exit search mode: {e}")
    
    def get_whatsapp_status(self):
        """Get comprehensive WhatsApp status"""
        status = {
            'installed': False,
            'running': False,
            'window_found': False,
            'installation_path': None,
            'process_id': None
        }
        
        # Check installation
        path = self.find_whatsapp_installation()
        if path:
            status['installed'] = True
            status['installation_path'] = path
        
        # Check if running
        pid = self.is_whatsapp_running()
        if pid:
            status['running'] = True
            status['process_id'] = pid
        
        # Check window
        window = self.get_whatsapp_window()
        if window:
            status['window_found'] = True
        
        return status

# Create a global instance for easy importing
whatsapp_handler = WhatsAppHandler()

# Enhanced functions for backward compatibility
def enhanced_open_whatsapp():
    """Enhanced function to open WhatsApp Windows desktop app"""
    return whatsapp_handler.launch_whatsapp()

def enhanced_send_whatsapp_message(contact_name, message):
    """Enhanced WhatsApp message sending function for desktop app"""
    try:
        # Ensure WhatsApp is running
        if not whatsapp_handler.is_whatsapp_running():
            if not whatsapp_handler.launch_whatsapp():
                return False
        
        # Focus WhatsApp window
        if not whatsapp_handler.focus_whatsapp_window():
            return False
        
        # Search for contact
        if not whatsapp_handler.search_contact(contact_name):
            return False
        
        # Send message
        return whatsapp_handler.send_message(message)
        
    except Exception as e:
        print(f"Enhanced message sending failed: {e}")
        return False

def get_whatsapp_status():
    """Get WhatsApp status"""
    return whatsapp_handler.get_whatsapp_status()

def find_whatsapp():
    """Find WhatsApp installation"""
    return whatsapp_handler.find_whatsapp_installation()

def focus_whatsapp_window():
    """Focus WhatsApp window"""
    return whatsapp_handler.focus_whatsapp_window()

# Alias for backward compatibility
whatsapp_simple = whatsapp_handler