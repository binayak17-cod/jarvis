#!/usr/bin/env python3
"""
Simple, reliable version of Synbi that works with both voice and text input
"""

import pyttsx3
import speech_recognition as sr
import datetime
import time
import threading

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.8)

def speak(text):
    """Simple TTS function"""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")
        print(f"Voice: {text}")

def get_voice_input():
    """Get voice input with better error handling"""
    r = sr.Recognizer()
    
    # Configure for better performance
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    r.phrase_threshold = 0.3
    
    try:
        with sr.Microphone() as source:
            print("🎤 Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✅ Ready! Speak now...")
            
            # Listen for speech
            audio = r.listen(source, timeout=8, phrase_time_limit=8)
            
        print("🔄 Processing speech...")
        text = r.recognize_google(audio, language="en-IN")
        print(f"✅ You said: '{text}'")
        return text.lower()
        
    except sr.WaitTimeoutError:
        print("⏰ No speech detected")
        return None
    except sr.UnknownValueError:
        print("❓ Could not understand speech")
        return None
    except sr.RequestError as e:
        print(f"🌐 Speech service error: {e}")
        return None
    except Exception as e:
        print(f"❌ Voice input error: {e}")
        return None

def get_text_input():
    """Get text input from user"""
    try:
        text = input("🔤 Type your command: ").strip().lower()
        return text if text else None
    except KeyboardInterrupt:
        return "exit"
    except Exception as e:
        print(f"❌ Text input error: {e}")
        return None

def process_command(command):
    """Process user commands"""
    if not command:
        return
    
    print(f"🔄 Processing: '{command}'")
    
    # Basic commands
    if "hello" in command:
        speak("Hello! I am Synbi, your personal assistant.")
    
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {current_time}")
    
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {current_date}")
    
    elif "weather" in command:
        speak("Weather feature is available. Please specify a city name.")
    
    elif "screenshot" in command:
        speak("Taking screenshot...")
        # Add screenshot functionality here
    
    elif "exit" in command or "quit" in command:
        speak("Goodbye!")
        return "exit"
    
    elif "help" in command:
        speak("Available commands: hello, time, date, weather, screenshot, exit")
    
    else:
        speak("I didn't understand that command. Say 'help' for available commands.")

def main():
    """Main function"""
    print("🤖 Simple Synbi Assistant")
    print("=" * 30)
    speak("Simple Synbi is now active.")
    
    print("\n💡 Options:")
    print("1. Say 'voice mode' for voice commands")
    print("2. Say 'text mode' for text commands")
    print("3. Type 'exit' to quit")
    
    mode = "voice"  # Default mode
    
    while True:
        try:
            if mode == "voice":
                print(f"\n🎤 Voice mode active")
                command = get_voice_input()
                
                if command is None:
                    print("❌ Voice input failed. Switching to text mode...")
                    mode = "text"
                    continue
                    
                if "text mode" in command:
                    mode = "text"
                    speak("Switched to text mode")
                    continue
                    
            else:  # text mode
                print(f"\n🔤 Text mode active")
                command = get_text_input()
                
                if command is None:
                    continue
                    
                if "voice mode" in command:
                    mode = "voice"
                    speak("Switched to voice mode")
                    continue
            
            # Process the command
            result = process_command(command)
            if result == "exit":
                break
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            speak("Sorry, something went wrong. Please try again.")

if __name__ == "__main__":
    main()
