# screenshot.py

import os
import pyautogui
import datetime

def take_screenshot():
    # Create the folder if it doesn't exist
    folder = "Screenshots"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(folder, f"screenshot_{timestamp}.png")

    # Take screenshot
    pyautogui.screenshot(file_path)

    return f"Screenshot saved to {file_path}"
