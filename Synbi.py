import pyttsx3
import speech_recognition as sr
import random
import re
import webbrowser
import datetime
import time
from plyer import notification
import pyautogui
import wikipedia
import pywhatkit as pwk
import user
from spotify_control import SpotifyController
from camera import capture_photo, record_video
from weather import get_weather
from system_control import set_brightness, set_volume
from internet_speed import get_speed
from sys_utils import battery_status, system_info
from screenshot import take_screenshot
from file_manager import move_item, copy_item, delete_item
# import email_config  # Removed - no email commands
from task_manager import add_task, delete_task, complete_task, get_tasks_summary, get_tasks_text, clear_completed_tasks, search_tasks, get_pending_tasks
import subprocess
import os

# Import new features
try:
    from whatsapp_handler import whatsapp_handler, enhanced_send_whatsapp_message, get_whatsapp_status, enhanced_open_whatsapp
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False

try:
    from process_manager import process_manager, list_processes, kill_process_by_name, get_process_info, get_system_info, find_processes
    PROCESS_MANAGER_AVAILABLE = True
except ImportError:
    PROCESS_MANAGER_AVAILABLE = False

try:
    from simple_gesture_control import start_simple_gesture_control, stop_simple_gesture_control
    GESTURE_CONTROL_AVAILABLE = True
except ImportError:
    GESTURE_CONTROL_AVAILABLE = False

# --- voice engine setup ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 200)
spotify = SpotifyController()
now = datetime.datetime.now()
send_time = now + datetime.timedelta(minutes=2)
hour = send_time.hour
minute = send_time.minute

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def is_whatsapp_running():
    """Check if WhatsApp is already running with improved detection"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                # Check for various WhatsApp process names
                if any(name in proc_name for name in ['whatsapp', 'whatsapp.exe', 'whatsappdesktop']):
                    print(f"Found WhatsApp process: {proc_name}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        print("WhatsApp process not found")
        return False
    except Exception as e:
        print(f"Error checking WhatsApp process: {e}")
        return False

def focus_whatsapp_window():
    """Focus on WhatsApp window with improved reliability"""
    try:
        import psutil
        import win32gui
        import win32con
        
        # First check if WhatsApp is actually running
        whatsapp_running = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(name in proc_name for name in ['whatsapp', 'whatsapp.exe', 'whatsappdesktop']):
                    whatsapp_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not whatsapp_running:
            print("WhatsApp is not running, cannot focus window")
            return False
        
        # Try to focus the window using multiple methods
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd).lower()
                if any(name in window_text for name in ['whatsapp', 'whatsapp desktop']):
                    print(f"Found WhatsApp window: {window_text}")
                    # Bring window to front and restore if minimized
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                    return False
            return True
        
        win32gui.EnumWindows(enum_windows_callback, [])
        time.sleep(2)  # Wait longer for window to focus
        return True
        
    except Exception as e:
        print(f"Error focusing WhatsApp window: {e}")
        # Fallback: try Alt+Tab to find WhatsApp
        try:
            pyautogui.hotkey('alt', 'tab')
            time.sleep(2)
            return True
        except:
            return False

def find_whatsapp_path():
    """Find WhatsApp installation path with improved search"""
    common_paths = [
        os.path.expanduser("~/AppData/Local/WhatsApp/WhatsApp.exe"),
        "C:/Users/Public/Desktop/WhatsApp.lnk",
        os.path.expanduser("~/Desktop/WhatsApp.lnk"),
        "C:/Program Files/WindowsApps/WhatsAppDesktop_*/WhatsApp.exe",
        "C:/Program Files/WhatsApp/WhatsApp.exe",
        "C:/Program Files (x86)/WhatsApp/WhatsApp.exe",
        os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/WhatsApp.lnk")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"Found WhatsApp at: {path}")
            return path
    
    print("WhatsApp not found in common locations")
    return None

def open_whatsapp_app():
    """Helper function to open WhatsApp Windows app with improved reliability"""
    try:
        # Check if WhatsApp is already running with better detection
        if is_whatsapp_running():
            print("WhatsApp is already running, focusing on existing window...")
            # Focus on existing window
            if focus_whatsapp_window():
                return True
            else:
                print("Could not focus on existing WhatsApp window, will try to open new instance")
        
        # Method 1: Try direct executable paths
        print("Trying to open WhatsApp from common installation paths...")
        whatsapp_path = find_whatsapp_path()
        if whatsapp_path:
            try:
                print(f"Opening WhatsApp from: {whatsapp_path}")
                # Try different ways to open the executable
                try:
                    # Method 1a: Direct subprocess
                    subprocess.Popen([whatsapp_path])
                    print("Opened using direct subprocess")
                except:
                    try:
                        # Method 1b: Using shell=True
                        subprocess.run([whatsapp_path], shell=True)
                        print("Opened using shell=True")
                    except:
                        # Method 1c: Using os.startfile
                        os.startfile(whatsapp_path)
                        print("Opened using os.startfile")
                
                time.sleep(15)  # Wait longer for app to start and load
                
                # Check if WhatsApp is now running
                if is_whatsapp_running():
                    print("WhatsApp process detected after opening")
                    # Focus on the window after opening
                    if focus_whatsapp_window():
                        print("WhatsApp opened and focused successfully")
                        return True
                    else:
                        print("WhatsApp opened but could not focus window")
                        return False
                else:
                    print("WhatsApp process not detected after opening attempt")
                    return False
                    
            except Exception as e:
                print(f"Failed to open from {whatsapp_path}: {e}")
        
        # Method 2: Try Windows search with better timing
        print("Trying Windows search method...")
        try:
            pyautogui.press('super')  # Open Windows search
            time.sleep(3)  # Wait longer for search to open
            pyautogui.typewrite('whatsapp')
            time.sleep(3)  # Wait for search results
            pyautogui.press('enter')
            time.sleep(15)  # Wait longer for app to start
            
            # Check if WhatsApp is now running
            if is_whatsapp_running():
                print("WhatsApp process detected after search method")
                # Focus on the window after opening
                if focus_whatsapp_window():
                    print("WhatsApp opened via search and focused successfully")
                    return True
                else:
                    print("WhatsApp opened via search but could not focus window")
                    return False
            else:
                print("WhatsApp process not detected after search method")
                return False
                
        except Exception as e:
            print(f"Windows search method failed: {e}")
        
        # Method 3: Try using 'start' command
        print("Trying 'start' command method...")
        try:
            subprocess.run(['start', 'whatsapp'], shell=True)
            time.sleep(15)
            
            # Check if WhatsApp is now running
            if is_whatsapp_running():
                print("WhatsApp process detected after start command")
                # Focus on the window after opening
                if focus_whatsapp_window():
                    print("WhatsApp opened via start command and focused successfully")
                    return True
                else:
                    print("WhatsApp opened via start command but could not focus window")
                    return False
            else:
                print("WhatsApp process not detected after start command")
                return False
                
        except Exception as e:
            print(f"'start' command failed: {e}")
        
        # Method 4: Try opening from Microsoft Store
        print("Trying Microsoft Store method...")
        try:
            subprocess.run(['start', 'ms-windows-store://pdp/?ProductId=9NKSQGP7F2NH'], shell=True)
            time.sleep(5)
            print("Opened Microsoft Store for WhatsApp")
            return False  # This opens store, not the app directly
        except Exception as e:
            print(f"Microsoft Store method failed: {e}")
        
        print("All methods failed to open WhatsApp")
        return False
            
    except Exception as e:
        print(f"Error opening WhatsApp: {e}")
        return False

def send_whatsapp_message(contact_name, message):
    """Optimized WhatsApp message sending function with better focus handling"""
    try:
        # Focus on WhatsApp window first and ensure it's active
        print("Focusing on WhatsApp window...")
        focus_whatsapp_window()
        
        # Wait for WhatsApp to fully load and be responsive
        time.sleep(5)
        
        # Method: Use Ctrl+F search (most reliable)
        try:
            print("Searching for contact...")
            # Press Ctrl+F to open search
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(2)  # Wait longer for search to open
            
            # Clear any existing text and type contact name
            pyautogui.hotkey('ctrl', 'a')  # Select all
            time.sleep(1)
            pyautogui.typewrite(contact_name)
            time.sleep(2)  # Wait for search results to load
            
            # Wait a bit more for search results to fully populate
            time.sleep(1)
            
            # Select the first contact (it should be highlighted by default)
            pyautogui.press('enter')
            time.sleep(1.5)  # Wait for contact selection and chat to load
            
            # Now type the message directly in the chat input
            
            # Type the message and send immediately
            print(f"Typing message: {message}")
            pyautogui.typewrite(message)
            pyautogui.press('enter')
            print("Message sent with Enter key")
            return True
            
        except Exception as e:
            print(f"Search method failed: {e}")
            return False
    
    except Exception as e:
        print(f"Message sending failed: {e}")
        return False

def command():
    r = sr.Recognizer()
    retries = 3
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                print("Listening... Please speak.")
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            content = r.recognize_google(audio, language="en-IN")
            print("You Said: " + content)
            return content.lower()
        except sr.WaitTimeoutError:
            print("Listening timed out, please try again.")
        except sr.UnknownValueError:
            print("Sorry, I did not catch that.")
            speak("Sorry, I didn't catch that. Please say again.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            speak("Sorry, I am unable to connect to the speech service.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            speak("Sorry, something went wrong. Please try again.")
    return ""

def main_process():
    speak("Synbi is now active.")
    while True:
        try:
            request = command()
            if not request:
                continue

            if "wait" in request:
                speak("Okay, going to sleep. Say 'Hey Synbi' to wake me up.")
                break

            if "hello" in request:
                speak("Hello, I am Synbi, your personal assistant.")

            # Spotify controls
            elif "play spotify" in request:
                song = request.replace("play spotify", "").strip()
                if song:
                    response = spotify.play_song(song)
                    speak(response)
                else:
                    speak("Please tell me which song to play on Spotify.")
            elif "pause spotify" in request or "stop spotify" in request:
                speak(spotify.pause())
            elif "resume spotify" in request:
                speak(spotify.resume())
            elif "next song" in request:
                speak(spotify.next_track())
            elif "previous song" in request:
                speak(spotify.previous_track())
            elif "shuffle on" in request:
                speak(spotify.shuffle(True))
            elif "shuffle off" in request:
                speak(spotify.shuffle(False))
            elif "repeat song" in request:
                speak(spotify.repeat("track"))
            elif "repeat playlist" in request:
                speak(spotify.repeat("context"))
            elif "repeat off" in request:
                speak(spotify.repeat("off"))
            elif "spotify status" in request:
                speak(spotify.current_playing())

            # Play YouTube video by query
            elif "play" in request and any(word in request for word in ["youtube", "video", "song", "music"]):
                query = request.replace("play", "").replace("youtube", "").replace("video", "").replace("song", "").replace("music", "").strip()
                if query:
                    speak(f"Playing {query} on YouTube")
                    pwk.playonyt(query)
                else:
                    speak("What would you like me to play on YouTube?")
            
            # YouTube playback controls
            elif "pause youtube" in request or "pause video" in request:
                try:
                    pyautogui.press('space')
                    speak("Video paused")
                except:
                    speak("Please pause the video manually")
            
            elif "resume youtube" in request or "resume video" in request:
                try:
                    pyautogui.press('space')
                    speak("Video resumed")
                except:
                    speak("Please resume the video manually")
            
            elif "next youtube" in request or "next video" in request:
                try:
                    # Try multiple methods for next video
                    pyautogui.press('right')  # Skip 10 seconds
                    time.sleep(0.5)
                    pyautogui.press('n')  # Next video shortcut
                    speak("Skipped to next video")
                except:
                    speak("Please skip to next video manually")
            
            elif "previous youtube" in request or "previous video" in request:
                try:
                    # Try multiple methods for previous video
                    pyautogui.press('left')  # Rewind 10 seconds
                    time.sleep(0.5)
                    pyautogui.press('p')  # Previous video shortcut
                    speak("Went to previous video")
                except:
                    speak("Please go to previous video manually")
            
            elif "mute youtube" in request or "mute video" in request:
                try:
                    pyautogui.press('m')
                    speak("Video muted/unmuted")
                except:
                    speak("Please mute/unmute the video manually")
            
            elif "fullscreen youtube" in request or "fullscreen video" in request:
                try:
                    # Try multiple methods for fullscreen
                    pyautogui.press('f')  # YouTube's fullscreen shortcut
                    time.sleep(0.5)
                    # Alternative: try escape key to exit fullscreen if already in fullscreen
                    pyautogui.press('escape')
                    time.sleep(0.5)
                    pyautogui.press('f')  # Try fullscreen again
                    speak("Video fullscreen toggled")
                except:
                    speak("Please toggle fullscreen manually by pressing F key")

            # Camera functions
            elif "take picture" in request or "take a photo" in request:
                response = capture_photo()
                speak(response)

            elif "record video" in request:
                speak("Recording video for 5 seconds")
                response = record_video(duration=5)
                speak(response)

            elif "take screenshot" in request or "screenshot" in request:
                response = take_screenshot()
                speak(response)
            
            #internet and system utilities
            # Internet Speed & System Utilities
            elif "internet speed" in request or "network speed" in request or "check internet" in request:
                speak("Checking internet speed, please wait...")
                speed = get_speed()
                print(speed)
                speak(speed)

            elif "battery status" in request or "battery level" in request or "check battery" in request:
                status = battery_status()
                print(status)
                speak(status)

            elif "system info" in request or "system status" in request or "check system" in request:
                info = system_info()
                print(info)
                speak(info)

            # Weather
            elif any(phrase in request for phrase in ["weather", "temperature", "forecast"]):
                city = None
            # Try to extract city from the sentence
                match = re.search(r"weather in ([a-zA-Z\s]+)", request)
                if not match:
                    match = re.search(r"temperature in ([a-zA-Z\s]+)", request)
                if not match:
                    match = re.search(r"forecast in ([a-zA-Z\s]+)", request)

                if match:
                    city = match.group(1).strip()
                else:
                    speak("Which city's weather would you like to know?")
                    city = command()
                if city:
                    weather_info = get_weather(city)
                    print(weather_info)
                    speak(weather_info)
                else:
                    speak("I didn't get the city name.")

            # Brightness control
            elif "set brightness" in request:
                speak("What level do you want the brightness set to? Please give a number from 0 to 100.")
                try:
                    level = int(command())
                    result = set_brightness(level)
                    speak(result)
                except Exception:
                    speak("Please provide a valid number for brightness.")

            # Volume control
            elif "set volume" in request:
                speak("What level do you want the volume set to? Please give a number from 0 to 100.")
                try:
                    level = int(command())
                    result = set_volume(level)
                    speak(result)
                except Exception:
                    speak("Please provide a valid number for volume.")

            # Time and date
            elif "say time" in request:
                now_time = datetime.datetime.now().strftime("%H:%M")
                speak("The time is " + now_time)
            elif "say date" in request:
                now_date = datetime.datetime.now().strftime("%Y-%m-%d")
                speak("Date is " + now_date)

            # ----------------------------
            # TASK MANAGEMENT: Optimized
            # ----------------------------
            elif "new task" in request or "add task" in request:
                task_text = request.replace("new task", "").replace("add task", "").strip()
                if task_text:
                    # Ask for priority if not specified
                    priority = "medium"
                    if any(word in request for word in ["high priority", "urgent", "important"]):
                        priority = "high"
                    elif any(word in request for word in ["low priority", "not urgent"]):
                        priority = "low"
                    
                    result = add_task(task_text, priority)
                    speak(result)
                else:
                    speak("What task would you like to add?")
                    task_text = command()
                    if task_text:
                        result = add_task(task_text)
                        speak(result)
                    else:
                        speak("No task specified.")

            elif "delete task" in request or "remove task" in request:
                task_identifier = request.replace("delete task", "").replace("remove task", "").strip()
                if task_identifier:
                    result = delete_task(task_identifier)
                    speak(result)
                else:
                    # List tasks and ask which to delete
                    tasks = get_pending_tasks()
                    if tasks:
                        speak("Which task would you like to delete? Say the number or task name.")
                        speak(get_tasks_text())
                        task_identifier = command()
                        if task_identifier:
                            result = delete_task(task_identifier)
                            speak(result)
                    else:
                        speak("You have no tasks to delete.")

            elif "complete task" in request or "mark task complete" in request or "finish task" in request:
                task_identifier = request.replace("complete task", "").replace("mark task complete", "").replace("finish task", "").strip()
                if task_identifier:
                    result = complete_task(task_identifier)
                    speak(result)
                else:
                    # List tasks and ask which to complete
                    tasks = get_pending_tasks()
                    if tasks:
                        speak("Which task would you like to complete? Say the number or task name.")
                        speak(get_tasks_text())
                        task_identifier = command()
                        if task_identifier:
                            result = complete_task(task_identifier)
                            speak(result)
                    else:
                        speak("You have no tasks to complete.")

            elif "speak task" in request or "read tasks" in request or "list tasks" in request:
                result = get_tasks_text()
                speak(result)

            elif "task summary" in request or "task status" in request:
                result = get_tasks_summary()
                speak(result)

            elif "show work" in request or "show tasks" in request:
                tasks = get_pending_tasks()
                if tasks:
                    task_text = "\n".join([f"{i}. {task['text']}" for i, task in enumerate(tasks, 1)])
                    notification.notify(
                        title="Your Tasks",
                        message=task_text,
                        timeout=10
                    )
                    speak("Tasks displayed in notification.")
                else:
                    speak("You have no pending tasks.")

            elif "clear completed" in request or "clear finished tasks" in request:
                result = clear_completed_tasks()
                speak(result)

            elif "search task" in request or "find task" in request:
                search_term = request.replace("search task", "").replace("find task", "").strip()
                if search_term:
                    found_tasks = search_tasks(search_term)
                    if found_tasks:
                        task_list = [f"{i}. {task['text']}" for i, task in enumerate(found_tasks, 1)]
                        result = f"Found {len(found_tasks)} task(s): " + ". ".join(task_list)
                        speak(result)
                    else:
                        speak(f"No tasks found containing '{search_term}'.")
                else:
                    speak("What would you like to search for?")
                    search_term = command()
                    if search_term:
                        found_tasks = search_tasks(search_term)
                        if found_tasks:
                            task_list = [f"{i}. {task['text']}" for i, task in enumerate(found_tasks, 1)]
                            result = f"Found {len(found_tasks)} task(s): " + ". ".join(task_list)
                            speak(result)
                        else:
                            speak(f"No tasks found containing '{search_term}'.")
            # ----------------------------
            # FILE SYSTEM: Move File/Folder
            # ----------------------------
            elif "move" in request and "from" in request and "to" in request:
                try:
                    pattern = r"move (.+?) from (.+?) to (.+)"
                    match = re.search(pattern, request)
                    if match:
                        item_name = match.group(1).strip()
                        from_folder = match.group(2).strip()
                        to_folder = match.group(3).strip()
                        
                        speak(f"Moving {item_name} from {from_folder} to {to_folder}")
                        result = move_item(item_name, from_folder, to_folder)
                        speak(result)
                    else:
                        speak("I didn't understand your move request. Please say 'move [filename] from [folder] to [folder]'")
                except Exception as e:
                    speak("Something went wrong while moving the file.")
                    print(e)

            # ----------------------------
            # FILE SYSTEM: Copy File/Folder
            # ----------------------------
            elif "copy" in request and "from" in request and "to" in request:
                try:
                    pattern = r"copy (.+?) from (.+?) to (.+)"
                    match = re.search(pattern, request)
                    if match:
                        item_name = match.group(1).strip()
                        from_folder = match.group(2).strip()
                        to_folder = match.group(3).strip()
                        
                        speak(f"Copying {item_name} from {from_folder} to {to_folder}")
                        result = copy_item(item_name, from_folder, to_folder)
                        speak(result)
                    else:
                        speak("I couldn't understand your copy request. Please say 'copy [filename] from [folder] to [folder]'")
                except Exception as e:
                    speak("Something went wrong while copying.")
                    print(e)

            # ----------------------------
            # FILE SYSTEM: Delete File/Folder
            # ----------------------------
            elif "delete" in request and "from" in request:
                try:
                    pattern = r"delete (.+?) from (.+)"
                    match = re.search(pattern, request)
                    if match:
                        item_name = match.group(1).strip()
                        from_folder = match.group(2).strip()
                        
                        speak(f"Preparing to delete {item_name} from {from_folder}")
                        result = delete_item(item_name, from_folder)
                        speak(result)
                    else:
                        speak("Could not understand which item to delete. Please say 'delete [filename] from [folder]'")
                except Exception as e:
                    speak("Something went wrong while deleting.")
                    print(e)

            
            # Open apps or files using keyboard shortcuts
            elif "open" in request:
                query = request.replace("open", "").strip()
                if query:
                    pyautogui.press("super")
                    pyautogui.typewrite(query)
                    pyautogui.press("enter")

            # Wikipedia search
            elif "wikipedia" in request:
                query = request.replace("synbi", "").replace("search wikipedia", "").strip()
                if query:
                    try:
                        result = wikipedia.summary(query, sentences=3)
                        speak(result)
                    except Exception:
                        speak("Sorry, I couldn't find any results on Wikipedia.")

            # Google search
            elif "search google" in request:
                query = request.replace("synbi", "").replace("search google", "").strip()
                if query:
                    webbrowser.open("https://www.google.com/search?q=" + query)

            # YouTube search
            elif "search youtube" in request:
                query = request.replace("synbi", "").replace("search youtube", "").strip()
                if query:
                    webbrowser.open("https://www.youtube.com/results?search_query=" + query)

            # ----------------------------
            # NEW FEATURES: WhatsApp Integration
            # ----------------------------
            elif "open whatsapp" in request or "launch whatsapp" in request or "start whatsapp" in request:
                if not WHATSAPP_AVAILABLE:
                    speak("WhatsApp integration is not available. Please install required dependencies.")
                    continue
                    
                try:
                    if enhanced_open_whatsapp():
                        speak("WhatsApp desktop app is now ready")
                    else:
                        speak("Could not open WhatsApp desktop app")
                except Exception as e:
                    print(f"WhatsApp desktop error: {e}")
                    speak("Sorry, I encountered an error opening WhatsApp")

            elif "send whatsapp" in request or "whatsapp message" in request or "send message" in request:
                if not WHATSAPP_AVAILABLE:
                    speak("WhatsApp integration is not available. Please install required dependencies.")
                    continue
                    
                try:
                    # Ask for contact name
                    speak("Who would you like to send a WhatsApp message to?")
                    contact_name = command()
                    if not contact_name:
                        speak("I didn't catch the contact name. Please try again.")
                        continue
                    
                    speak(f"What message would you like to send to {contact_name}?")
                    message = command()
                    if not message:
                        speak("I didn't catch the message. Please try again.")
                        continue
                    
                    # Send message using enhanced desktop function
                    if enhanced_send_whatsapp_message(contact_name, message):
                        speak(f"Message successfully sent to {contact_name}")
                    else:
                        speak("I couldn't send the message. Please ensure WhatsApp is installed and try again.")
                    
                except Exception as e:
                    print(f"WhatsApp message error: {e}")
                    speak("Sorry, I couldn't send the WhatsApp message. Please try again.")

            # ----------------------------
            # NEW FEATURES: Process Manager
            # ----------------------------
            elif "list processes" in request or "show processes" in request or "running processes" in request:
                if not PROCESS_MANAGER_AVAILABLE:
                    speak("Process manager is not available. Please install required dependencies.")
                    continue
                    
                try:
                    speak("Getting list of running processes...")
                    processes = list_processes(limit=15, sort_by='cpu')
                    print(processes)
                    speak("Here are the top running processes by CPU usage")
                except Exception as e:
                    print(f"Process listing error: {e}")
                    speak("Sorry, I couldn't get the process list.")

            elif "close" in request or "kill" in request:
                if not PROCESS_MANAGER_AVAILABLE:
                    speak("Process manager is not available. Please install required dependencies.")
                    continue
                    
                try:
                    # Extract app name from request
                    app_name = request.replace("close", "").replace("kill", "").strip()
                    if app_name:
                        result = kill_process_by_name(app_name)
                        print(result['message'])
                        speak(result['message'])
                    else:
                        speak("Please specify which application to close.")
                except Exception as e:
                    print(f"Process closing error: {e}")
                    speak("Sorry, I couldn't close the application.")

            # ----------------------------
            # NEW FEATURES: Gesture Control
            # ----------------------------
            elif "start gesture control" in request or "enable gesture control" in request or "begin gesture control" in request:
                if not GESTURE_CONTROL_AVAILABLE:
                    speak("Gesture control is not available. Please install required dependencies.")
                    continue
                    
                try:
                    speak("Starting mouse gesture control...")
                    
                    if start_simple_gesture_control():
                        speak("Mouse control is now active. Show your hand to the camera to control the mouse.")
                    else:
                        speak("Could not start mouse control. Your camera might be in use by another application or not available.")
                except Exception as e:
                    print(f"Gesture control error: {e}")
                    speak("Sorry, I couldn't start mouse control. Please check your camera permissions and make sure no other application is using it.")

            elif "stop gesture control" in request or "disable gesture control" in request or "end gesture control" in request:
                if not GESTURE_CONTROL_AVAILABLE:
                    speak("Gesture control is not available.")
                    continue
                    
                try:
                    speak("Stopping mouse control...")
                    stop_simple_gesture_control()
                    speak("Mouse control has been stopped.")
                except Exception as e:
                    print(f"Gesture control error: {e}")
                    speak("Sorry, I couldn't stop mouse control.")

            

            # Exit the assistant
            elif "exit" in request or "quit" in request:
                speak("Goodbye! See you later.")
                break

            else:
                speak("I didn't understand that. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            speak("Sorry, something went wrong. Please try again.")


if __name__ == "__main__":
    main_process()
