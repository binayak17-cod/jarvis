#!/usr/bin/env python3
"""
Gesture Control Module for Synbi Assistant
Uses MediaPipe and OpenCV for hand gesture recognition
"""

import time
import threading
from typing import Dict, List, Callable, Optional

# Try to import optional dependencies
try:
    import cv2
    import mediapipe as mp
    import numpy as np
    GESTURE_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    GESTURE_DEPENDENCIES_AVAILABLE = False

# Try to import other modules
try:
    from spotify_control import SpotifyController
    from system_control import set_brightness, set_volume
    from camera import capture_photo, record_video
    from screenshot import take_screenshot
except ImportError as e:
    print(f"Some gesture control dependencies not available: {e}")
    # Create dummy functions to prevent errors
    def SpotifyController():
        return None
    def set_brightness(level):
        return f"Brightness set to {level}"
    def set_volume(level):
        return f"Volume set to {level}"
    def capture_photo():
        return "Photo captured"
    def record_video(duration=5):
        return f"Video recorded for {duration} seconds"
    def take_screenshot():
        return "Screenshot taken"

class GestureController:
    """Hand gesture recognition and control system"""
    
    def __init__(self):
        # Check if dependencies are available
        if not GESTURE_DEPENDENCIES_AVAILABLE:
            self.mp_hands = None
            self.mp_drawing = None
            self.hands = None
        else:
            # MediaPipe setup
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
        
        # OpenCV setup
        self.cap = None
        self.is_running = False
        self.current_mode = "disabled"
        
        # Gesture modes and their functions
        self.modes = {
            "disabled": {
                "name": "Gesture Control Disabled",
                "gestures": {},
                "description": "No gestures active"
            },
            "spotify": {
                "name": "Spotify Control",
                "gestures": {
                    "open_palm": self._spotify_play_pause,
                    "fist": self._spotify_next_track,
                    "peace_sign": self._spotify_previous_track,
                    "thumbs_up": self._spotify_volume_up,
                    "thumbs_down": self._spotify_volume_down,
                    "swipe_left": self._spotify_shuffle_on,
                    "swipe_right": self._spotify_shuffle_off
                },
                "description": "Control Spotify playback with hand gestures"
            },
            "system": {
                "name": "System Control",
                "gestures": {
                    "open_palm": self._system_brightness_up,
                    "fist": self._system_brightness_down,
                    "peace_sign": self._system_volume_up,
                    "thumbs_up": self._system_volume_up,
                    "thumbs_down": self._system_volume_down,
                    "swipe_left": self._system_screenshot,
                    "swipe_right": self._system_screenshot
                },
                "description": "Control system volume, brightness, and screenshots"
            },
            "camera": {
                "name": "Camera Control",
                "gestures": {
                    "open_palm": self._camera_take_photo,
                    "fist": self._camera_record_video,
                    "peace_sign": self._camera_take_photo,
                    "thumbs_up": self._camera_confirm,
                    "thumbs_down": self._camera_cancel,
                    "swipe_left": self._camera_switch_mode,
                    "swipe_right": self._camera_switch_mode
                },
                "description": "Control camera functions with gestures"
            },
            "navigation": {
                "name": "Navigation Control",
                "gestures": {
                    "open_palm": self._nav_home,
                    "fist": self._nav_back,
                    "peace_sign": self._nav_forward,
                    "thumbs_up": self._nav_scroll_up,
                    "thumbs_down": self._nav_scroll_down,
                    "swipe_left": self._nav_previous_tab,
                    "swipe_right": self._nav_next_tab
                },
                "description": "Navigate web pages and applications"
            }
        }
        
        # Gesture detection state
        self.gesture_history = []
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # Minimum time between gestures
        
        # Spotify controller
        self.spotify = SpotifyController()
        
        # Camera state
        self.camera_mode = "photo"  # "photo" or "video"
        
        # Feedback
        self.feedback_callback = None
        
    def set_feedback_callback(self, callback: Callable[[str], None]):
        """Set callback function for providing feedback to user"""
        self.feedback_callback = callback
    
    def _provide_feedback(self, message: str):
        """Provide feedback to user"""
        if self.feedback_callback:
            self.feedback_callback(message)
        else:
            print(f"Gesture: {message}")
    
    # Gesture detection methods
    def _detect_open_palm(self, landmarks) -> bool:
        """Detect open palm gesture"""
        # Check if all fingers are extended
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        finger_pips = [3, 6, 10, 14, 18]  # Finger PIP joints
        
        extended_fingers = 0
        for i in range(5):
            if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                extended_fingers += 1
        
        return extended_fingers >= 4
    
    def _detect_fist(self, landmarks) -> bool:
        """Detect fist gesture"""
        # Check if all fingers are closed
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        closed_fingers = 0
        for i in range(5):
            if landmarks[finger_tips[i]].y > landmarks[finger_pips[i]].y:
                closed_fingers += 1
        
        return closed_fingers >= 4
    
    def _detect_peace_sign(self, landmarks) -> bool:
        """Detect peace sign (index and middle finger extended)"""
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        # Check if index and middle fingers are extended
        index_extended = landmarks[8].y < landmarks[6].y
        middle_extended = landmarks[12].y < landmarks[10].y
        ring_closed = landmarks[16].y > landmarks[14].y
        pinky_closed = landmarks[20].y > landmarks[18].y
        
        return index_extended and middle_extended and ring_closed and pinky_closed
    
    def _detect_thumbs_up(self, landmarks) -> bool:
        """Detect thumbs up gesture"""
        # Check if thumb is extended and other fingers are closed
        thumb_extended = landmarks[4].x > landmarks[3].x  # Thumb pointing up/out
        other_fingers_closed = all(
            landmarks[8].y > landmarks[6].y,  # Index
            landmarks[12].y > landmarks[10].y,  # Middle
            landmarks[16].y > landmarks[14].y,  # Ring
            landmarks[20].y > landmarks[18].y   # Pinky
        )
        
        return thumb_extended and other_fingers_closed
    
    def _detect_thumbs_down(self, landmarks) -> bool:
        """Detect thumbs down gesture"""
        # Check if thumb is pointing down and other fingers are closed
        thumb_down = landmarks[4].y > landmarks[3].y  # Thumb pointing down
        other_fingers_closed = all(
            landmarks[8].y > landmarks[6].y,  # Index
            landmarks[12].y > landmarks[10].y,  # Middle
            landmarks[16].y > landmarks[14].y,  # Ring
            landmarks[20].y > landmarks[18].y   # Pinky
        )
        
        return thumb_down and other_fingers_closed
    
    def _detect_swipe_left(self, landmarks) -> bool:
        """Detect left swipe gesture (simplified - would need motion tracking)"""
        # This is a simplified version - in practice, you'd track hand movement over time
        # For now, we'll use a combination of open palm + left position
        if self._detect_open_palm(landmarks):
            # Check if hand is in left portion of screen
            return landmarks[9].x < 0.3  # Wrist position in left third
        return False
    
    def _detect_swipe_right(self, landmarks) -> bool:
        """Detect right swipe gesture (simplified - would need motion tracking)"""
        # This is a simplified version - in practice, you'd track hand movement over time
        # For now, we'll use a combination of open palm + right position
        if self._detect_open_palm(landmarks):
            # Check if hand is in right portion of screen
            return landmarks[9].x > 0.7  # Wrist position in right third
        return False
    
    def _recognize_gesture(self, landmarks) -> Optional[str]:
        """Recognize the current gesture from hand landmarks"""
        gestures = [
            ("open_palm", self._detect_open_palm),
            ("fist", self._detect_fist),
            ("peace_sign", self._detect_peace_sign),
            ("thumbs_up", self._detect_thumbs_up),
            ("thumbs_down", self._detect_thumbs_down),
            ("swipe_left", self._detect_swipe_left),
            ("swipe_right", self._detect_swipe_right)
        ]
        
        for gesture_name, detector in gestures:
            if detector(landmarks):
                return gesture_name
        
        return None
    
    # Mode-specific action methods
    def _spotify_play_pause(self):
        """Spotify play/pause action"""
        try:
            # Check if currently playing
            current = self.spotify.current_playing()
            if "playing" in current.lower():
                result = self.spotify.pause()
            else:
                result = self.spotify.resume()
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _spotify_next_track(self):
        """Spotify next track action"""
        try:
            result = self.spotify.next_track()
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _spotify_previous_track(self):
        """Spotify previous track action"""
        try:
            result = self.spotify.previous_track()
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _spotify_volume_up(self):
        """Spotify volume up action"""
        try:
            result = self.spotify.volume_up()
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _spotify_volume_down(self):
        """Spotify volume down action"""
        try:
            result = self.spotify.volume_down()
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _spotify_shuffle_on(self):
        """Spotify shuffle on action"""
        try:
            result = self.spotify.shuffle(True)
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _spotify_shuffle_off(self):
        """Spotify shuffle off action"""
        try:
            result = self.spotify.shuffle(False)
            self._provide_feedback(f"Spotify: {result}")
        except Exception as e:
            self._provide_feedback(f"Spotify error: {e}")
    
    def _system_brightness_up(self):
        """System brightness up action"""
        try:
            # Get current brightness and increase by 10
            result = set_brightness(75)  # Example value
            self._provide_feedback(f"Brightness increased")
        except Exception as e:
            self._provide_feedback(f"Brightness error: {e}")
    
    def _system_brightness_down(self):
        """System brightness down action"""
        try:
            # Get current brightness and decrease by 10
            result = set_brightness(25)  # Example value
            self._provide_feedback(f"Brightness decreased")
        except Exception as e:
            self._provide_feedback(f"Brightness error: {e}")
    
    def _system_volume_up(self):
        """System volume up action"""
        try:
            # Get current volume and increase by 10
            result = set_volume(75)  # Example value
            self._provide_feedback(f"Volume increased")
        except Exception as e:
            self._provide_feedback(f"Volume error: {e}")
    
    def _system_volume_down(self):
        """System volume down action"""
        try:
            # Get current volume and decrease by 10
            result = set_volume(25)  # Example value
            self._provide_feedback(f"Volume decreased")
        except Exception as e:
            self._provide_feedback(f"Volume error: {e}")
    
    def _system_screenshot(self):
        """System screenshot action"""
        try:
            result = take_screenshot()
            self._provide_feedback(f"Screenshot taken")
        except Exception as e:
            self._provide_feedback(f"Screenshot error: {e}")
    
    def _camera_take_photo(self):
        """Camera take photo action"""
        try:
            result = capture_photo()
            self._provide_feedback(f"Photo taken")
        except Exception as e:
            self._provide_feedback(f"Camera error: {e}")
    
    def _camera_record_video(self):
        """Camera record video action"""
        try:
            result = record_video(duration=5)
            self._provide_feedback(f"Video recorded")
        except Exception as e:
            self._provide_feedback(f"Camera error: {e}")
    
    def _camera_confirm(self):
        """Camera confirm action"""
        self._provide_feedback("Camera action confirmed")
    
    def _camera_cancel(self):
        """Camera cancel action"""
        self._provide_feedback("Camera action cancelled")
    
    def _camera_switch_mode(self):
        """Camera switch mode action"""
        self.camera_mode = "video" if self.camera_mode == "photo" else "photo"
        self._provide_feedback(f"Camera mode: {self.camera_mode}")
    
    def _nav_home(self):
        """Navigation home action"""
        self._provide_feedback("Navigation: Home")
    
    def _nav_back(self):
        """Navigation back action"""
        self._provide_feedback("Navigation: Back")
    
    def _nav_forward(self):
        """Navigation forward action"""
        self._provide_feedback("Navigation: Forward")
    
    def _nav_scroll_up(self):
        """Navigation scroll up action"""
        self._provide_feedback("Navigation: Scroll up")
    
    def _nav_scroll_down(self):
        """Navigation scroll down action"""
        self._provide_feedback("Navigation: Scroll down")
    
    def _nav_previous_tab(self):
        """Navigation previous tab action"""
        self._provide_feedback("Navigation: Previous tab")
    
    def _nav_next_tab(self):
        """Navigation next tab action"""
        self._provide_feedback("Navigation: Next tab")
    
    # Main control methods
    def set_mode(self, mode: str) -> bool:
        """Set the current gesture mode"""
        if mode in self.modes:
            self.current_mode = mode
            self._provide_feedback(f"Gesture mode: {self.modes[mode]['name']}")
            return True
        else:
            self._provide_feedback(f"Unknown mode: {mode}")
            return False
    
    def get_mode(self) -> str:
        """Get the current gesture mode"""
        return self.current_mode
    
    def get_available_modes(self) -> List[str]:
        """Get list of available modes"""
        return list(self.modes.keys())
    
    def get_mode_info(self, mode: str) -> Dict:
        """Get information about a specific mode"""
        return self.modes.get(mode, {})
    
    def start_gesture_control(self) -> bool:
        """Start gesture control with webcam"""
        if not GESTURE_DEPENDENCIES_AVAILABLE:
            self._provide_feedback("Gesture control dependencies not available")
            return False
            
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self._provide_feedback("Could not open webcam")
                return False
            
            self.is_running = True
            self._provide_feedback("Gesture control started")
            
            # Start gesture detection in a separate thread
            self.gesture_thread = threading.Thread(target=self._gesture_detection_loop)
            self.gesture_thread.daemon = True
            self.gesture_thread.start()
            
            return True
            
        except Exception as e:
            self._provide_feedback(f"Error starting gesture control: {e}")
            return False
    
    def stop_gesture_control(self):
        """Stop gesture control"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self._provide_feedback("Gesture control stopped")
    
    def _gesture_detection_loop(self):
        """Main gesture detection loop"""
        if not GESTURE_DEPENDENCIES_AVAILABLE:
            return
            
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                height, width, _ = frame.shape
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process the frame
                results = self.hands.process(rgb_frame)
                
                # Draw mode info on frame
                mode_text = f"Mode: {self.modes[self.current_mode]['name']}"
                cv2.putText(frame, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Draw gesture instructions
                if self.current_mode != "disabled":
                    instructions = self.modes[self.current_mode]['description']
                    cv2.putText(frame, instructions, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Process hand landmarks
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        
                        # Recognize gesture
                        current_time = time.time()
                        if current_time - self.last_gesture_time > self.gesture_cooldown:
                            gesture = self._recognize_gesture(hand_landmarks.landmark)
                            
                            if gesture and self.current_mode != "disabled":
                                # Execute gesture action
                                mode_gestures = self.modes[self.current_mode]['gestures']
                                if gesture in mode_gestures:
                                    mode_gestures[gesture]()
                                    self.last_gesture_time = current_time
                                    
                                    # Draw gesture name on frame
                                    cv2.putText(frame, f"Gesture: {gesture}", (10, 60), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # Display the frame
                cv2.imshow('Synbi Gesture Control', frame)
                
                # Check for exit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                print(f"Gesture detection error: {e}")
                continue
        
        # Cleanup
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

# Create a global instance
gesture_controller = GestureController()

# Convenience functions for easy importing
def start_gesture_control():
    """Start gesture control"""
    return gesture_controller.start_gesture_control()

def stop_gesture_control():
    """Stop gesture control"""
    gesture_controller.stop_gesture_control()

def set_gesture_mode(mode: str):
    """Set gesture control mode"""
    return gesture_controller.set_mode(mode)

def get_gesture_mode():
    """Get current gesture mode"""
    return gesture_controller.get_mode()

def get_available_gesture_modes():
    """Get available gesture modes"""
    return gesture_controller.get_available_modes()

def set_gesture_feedback_callback(callback):
    """Set feedback callback for gesture actions"""
    gesture_controller.set_feedback_callback(callback)
