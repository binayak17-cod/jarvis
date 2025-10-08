import os
import shutil
import speech_recognition as sr

def validate_path(path):
    """Validate if path exists and is accessible"""
    try:
        return os.path.exists(path) and os.access(path, os.R_OK)
    except:
        return False

def get_full_path(folder_path):
    """Get full absolute path from user input"""
    # Handle common folder names
    folder_mapping = {
        "desktop": "~/Desktop",
        "documents": "~/Documents", 
        "downloads": "~/Downloads",
        "pictures": "~/Pictures",
        "music": "~/Music",
        "videos": "~/Videos"
    }
    
    folder_lower = folder_path.lower()
    if folder_lower in folder_mapping:
        return os.path.expanduser(folder_mapping[folder_lower])
    else:
        return os.path.expanduser(folder_path)

# Move item from one folder to another
def move_item(item_name, from_folder, to_folder):
    try:
        # Get full paths
        from_path = os.path.join(get_full_path(from_folder), item_name)
        to_path = get_full_path(to_folder)
        to_item_path = os.path.join(to_path, item_name)

        # Validate source path
        if not validate_path(from_path):
            return f"Error: '{item_name}' not found in '{from_folder}' or path is not accessible."

        # Create destination folder if it doesn't exist
        if not os.path.exists(to_path):
            try:
                os.makedirs(to_path)
            except Exception as e:
                return f"Error: Could not create destination folder '{to_folder}': {str(e)}"

        # Check if destination already exists
        if os.path.exists(to_item_path):
            return f"Error: '{item_name}' already exists in '{to_folder}'. Cannot move."

        # Perform the move
        shutil.move(from_path, to_item_path)
        return f"Successfully moved '{item_name}' from '{from_folder}' to '{to_folder}'."
        
    except PermissionError:
        return f"Error: Permission denied. Cannot move '{item_name}'."
    except Exception as e:
        return f"Error moving '{item_name}': {str(e)}"

# Copy item from one folder to another
def copy_item(item_name, from_folder, to_folder):
    try:
        # Get full paths
        from_path = os.path.join(get_full_path(from_folder), item_name)
        to_path = get_full_path(to_folder)
        to_item_path = os.path.join(to_path, item_name)

        # Validate source path
        if not validate_path(from_path):
            return f"Error: '{item_name}' not found in '{from_folder}' or path is not accessible."

        # Create destination folder if it doesn't exist
        if not os.path.exists(to_path):
            try:
                os.makedirs(to_path)
            except Exception as e:
                return f"Error: Could not create destination folder '{to_folder}': {str(e)}"

        # Check if destination already exists
        if os.path.exists(to_item_path):
            return f"Error: '{item_name}' already exists in '{to_folder}'. Cannot copy."

        # Perform the copy
        if os.path.isdir(from_path):
            shutil.copytree(from_path, to_item_path)
        else:
            shutil.copy2(from_path, to_item_path)
            
        return f"Successfully copied '{item_name}' from '{from_folder}' to '{to_folder}'."
        
    except PermissionError:
        return f"Error: Permission denied. Cannot copy '{item_name}'."
    except Exception as e:
        return f"Error copying '{item_name}': {str(e)}"

# Delete item with voice confirmation
def delete_item(item_name, from_folder):
    try:
        # Get full path
        from_path = os.path.join(get_full_path(from_folder), item_name)

        # Validate source path
        if not validate_path(from_path):
            return f"Error: '{item_name}' not found in '{from_folder}' or path is not accessible."

        # Get file/folder info for confirmation
        item_type = "folder" if os.path.isdir(from_path) else "file"
        item_size = ""
        
        if os.path.isfile(from_path):
            size = os.path.getsize(from_path)
            if size > 1024*1024:  # MB
                item_size = f" ({size//(1024*1024)} MB)"
            elif size > 1024:  # KB
                item_size = f" ({size//1024} KB)"
            else:
                item_size = f" ({size} bytes)"

        # Ask for confirmation
        confirmation_message = f"Are you sure you want to delete the {item_type} '{item_name}'{item_size} from '{from_folder}'? Say 'yes' to confirm or 'no' to cancel."
        print(confirmation_message)
        
        confirmation = listen_for_confirmation()
        
        if confirmation != "yes":
            return "Delete operation cancelled."

        # Perform the delete
        if os.path.isdir(from_path):
            shutil.rmtree(from_path)
        else:
            os.remove(from_path)
            
        return f"Successfully deleted '{item_name}' from '{from_folder}'."
        
    except PermissionError:
        return f"Error: Permission denied. Cannot delete '{item_name}'."
    except Exception as e:
        return f"Error deleting '{item_name}': {str(e)}"

# Listen for yes/no confirmation
def listen_for_confirmation():
    r = sr.Recognizer()
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            with sr.Microphone() as source:
                print("Listening for confirmation...")
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
                response = r.recognize_google(audio, language="en-IN").lower()
                print(f"You said: {response}")
                
                # Accept various forms of yes/no
                if response in ["yes", "yeah", "yep", "sure", "okay", "ok", "confirm"]:
                    return "yes"
                elif response in ["no", "nope", "nah", "cancel", "stop"]:
                    return "no"
                else:
                    print("Please say 'yes' or 'no'.")
                    
        except sr.WaitTimeoutError:
            print("No response detected. Please try again.")
        except sr.UnknownValueError:
            print("Could not understand. Please say 'yes' or 'no'.")
        except Exception as e:
            print(f"Error: {e}")
            
    print("No valid confirmation received. Cancelling operation.")
    return "no"
