#!/usr/bin/env python3
"""
Simple Gesture Control Module for Synbi Assistant
Uses OpenCV for basic gesture recognition (without MediaPipe dependency)
"""

import time
import threading
from typing import Dict, List, Callable, Optional

# Try to import OpenCV
try:
    import cv2
    import numpy as np
    # Limit OpenCV threading to reduce CPU spikes
    try:
        cv2.setNumThreads(1)
    except Exception:
        pass
    OPENCV_AVAILABLE = True
except ImportError as e:
    OPENCV_AVAILABLE = False

# Import mouse control
import pyautogui

class SimpleGestureController:
    """Simple gesture recognition using OpenCV (without MediaPipe)"""
    
    def __init__(self):
        # Check if OpenCV is available
        if not OPENCV_AVAILABLE:
            self.cap = None
            print("Simple gesture control initialized without OpenCV dependencies")
            print("Install OpenCV to enable functionality: pip install opencv-python numpy")
        else:
            self.cap = None
        
        self.is_running = False
        self.current_mode = "disabled"
        
        # Mouse control gestures
        self.mouse_gestures = {
            "hand_detected": self._mouse_click,
            "two_fingers": self._mouse_left_click,
            "three_fingers": self._mouse_right_click,
            "movement_left": self._mouse_move_left,
            "movement_right": self._mouse_move_right,
            "movement_up": self._mouse_move_up,
            "movement_down": self._mouse_move_down
        }
        
        # Movement tracking
        self.last_hand_position = None
        self.smoothed_hand_position = None
        self.position_smoothing_alpha = 0.35  # EMA factor for cursor smoothing
        self.movement_threshold = 28  # Slightly reduced for better sensitivity
        self.gesture_cooldown = 0.35  # Cooldown to avoid double triggers
        self.last_gesture_time = 0
        self.last_click_type = None  # 'left' | 'right'
        self.click_reset_required = False  # Require finger release before next click
        
        # Mouse control settings
        self.mouse_sensitivity = 5  # Base pixel step for moveRel
        self.mouse_speed = 0.03  # Faster, but still smooth
        
        # Feedback
        self.feedback_callback = None
    
    def set_feedback_callback(self, callback: Callable[[str], None]):
        """Set callback function for providing feedback to user"""
        self.feedback_callback = callback
    
    def _provide_feedback(self, message: str):
        """Provide feedback to user with throttling"""
        try:
            # Throttle feedback to prevent excessive TTS calls
            current_time = time.time()
            if hasattr(self, '_last_feedback_time') and current_time - self._last_feedback_time < 2.0:
                return  # Skip feedback if called too frequently

            self._last_feedback_time = current_time

            if self.feedback_callback:
                self.feedback_callback(message)
            else:
                print(f"Gesture: {message}")
        except Exception as e:
            print(f"Feedback error: {e}")
            print(f"Gesture: {message}")

    def _smooth_position(self, current_pos):
        """Exponential moving average smoothing for hand position."""
        if current_pos is None:
            return None
        if self.smoothed_hand_position is None:
            self.smoothed_hand_position = current_pos
            return current_pos
        ax = self.position_smoothing_alpha
        sx = int(ax * current_pos[0] + (1 - ax) * self.smoothed_hand_position[0])
        sy = int(ax * current_pos[1] + (1 - ax) * self.smoothed_hand_position[1])
        self.smoothed_hand_position = (sx, sy)
        return self.smoothed_hand_position
    
    # Simple gesture detection methods
    def _detect_hand_movement(self, current_pos, last_pos):
        """Detect hand movement direction"""
        if last_pos is None:
            return None
        
        dx = current_pos[0] - last_pos[0]
        dy = current_pos[1] - last_pos[1]
        
        if abs(dx) < self.movement_threshold and abs(dy) < self.movement_threshold:
            return "hand_detected"
        
        if abs(dx) > abs(dy):
            if dx > self.movement_threshold:
                return "movement_right"
            elif dx < -self.movement_threshold:
                return "movement_left"
        else:
            if dy > self.movement_threshold:
                return "movement_down"
            elif dy < -self.movement_threshold:
                return "movement_up"
        
        return None
    
    def _simple_hand_detection(self, frame):
        """Simple hand detection using color-based segmentation with finger counting"""
        if not OPENCV_AVAILABLE:
            return None, None, 0
        
        try:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (320, 240))
            
            # Convert to HSV for better skin color detection
            hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
            
            # Define skin color range (adjust these values as needed)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create mask for skin color
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Apply morphological operations to clean up the mask (reduced iterations)
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour (likely the hand)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Get the center of the contour
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Scale coordinates back to original frame size
                    scale_x = frame.shape[1] / small_frame.shape[1]
                    scale_y = frame.shape[0] / small_frame.shape[0]
                    cx_scaled = int(cx * scale_x)
                    cy_scaled = int(cy * scale_y)
                    
                    # Count fingers using convex hull defects
                    finger_count = self._count_fingers(largest_contour, small_frame)
                    
                    # Draw circle and crosshair on the hand (on original frame)
                    cv2.circle(frame, (cx_scaled, cy_scaled), 15, (0, 255, 0), 2)
                    cv2.circle(frame, (cx_scaled, cy_scaled), 5, (0, 255, 0), -1)
                    # Draw crosshair
                    cv2.line(frame, (cx_scaled-20, cy_scaled), (cx_scaled+20, cy_scaled), (0, 255, 0), 2)
                    cv2.line(frame, (cx_scaled, cy_scaled-20), (cx_scaled, cy_scaled+20), (0, 255, 0), 2)
                    
                    # Draw finger count and gesture info
                    if finger_count == 2:
                        cv2.putText(frame, "TWO FINGERS - LEFT CLICK", (cx_scaled+25, cy_scaled), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    elif finger_count == 3:
                        cv2.putText(frame, "THREE FINGERS - RIGHT CLICK", (cx_scaled+25, cy_scaled), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, f"FINGERS: {finger_count}", (cx_scaled+25, cy_scaled), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    return (cx_scaled, cy_scaled), largest_contour, finger_count
            
            return None, None, 0
            
        except Exception as e:
            print(f"Hand detection error: {e}")
            return None, None, 0
    
    def _count_fingers(self, contour, frame):
        """Count fingers using convex hull defects"""
        try:
            # Check if contour has enough points
            if len(contour) < 5:
                return 0
                
            # Calculate convex hull
            hull = cv2.convexHull(contour, returnPoints=False)
            defects = cv2.convexityDefects(contour, hull)
            
            if defects is None or len(defects) == 0:
                return 0
            
            finger_count = 0
            for i in range(defects.shape[0]):
                try:
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])
                    
                    # Calculate the angle between the lines
                    a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                    b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                    c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                    
                    # Avoid division by zero
                    if b == 0 or c == 0:
                        continue
                    
                    # Calculate angle using cosine rule
                    cos_angle = (b**2 + c**2 - a**2) / (2*b*c)
                    # Clamp cos_angle to valid range [-1, 1]
                    cos_angle = max(-1, min(1, cos_angle))
                    angle = np.arccos(cos_angle)
                    
                    # If angle is less than 90 degrees, it's a finger
                    if angle <= np.pi/2:
                        finger_count += 1
                except Exception as e:
                    continue
            
            # Add 1 because we count the spaces between fingers, not the fingers themselves
            return min(finger_count + 1, 5)  # Cap at 5 fingers
            
        except Exception as e:
            print(f"Finger counting error: {e}")
            return 0
    
    # Mouse control methods
    def _mouse_click(self):
        """Mouse click action (default left click)"""
        try:
            pyautogui.click()
            self._provide_feedback("Mouse clicked")
        except Exception as e:
            self._provide_feedback(f"Mouse click error: {e}")
    
    def _mouse_left_click(self):
        """Mouse left click action"""
        try:
            pyautogui.click(button='left')
            self._provide_feedback("Left click")
        except Exception as e:
            self._provide_feedback(f"Left click error: {e}")
    
    def _mouse_right_click(self):
        """Mouse right click action"""
        try:
            pyautogui.click(button='right')
            self._provide_feedback("Right click")
        except Exception as e:
            self._provide_feedback(f"Right click error: {e}")
    
    def _mouse_move_left(self):
        """Mouse move left action"""
        try:
            pyautogui.moveRel(-self.mouse_sensitivity, 0, duration=self.mouse_speed)
            self._provide_feedback("Mouse moved left")
        except Exception as e:
            self._provide_feedback(f"Mouse move error: {e}")
    
    def _mouse_move_right(self):
        """Mouse move right action"""
        try:
            pyautogui.moveRel(self.mouse_sensitivity, 0, duration=self.mouse_speed)
            self._provide_feedback("Mouse moved right")
        except Exception as e:
            self._provide_feedback(f"Mouse move error: {e}")
    
    def _mouse_move_up(self):
        """Mouse move up action"""
        try:
            pyautogui.moveRel(0, -self.mouse_sensitivity, duration=self.mouse_speed)
            self._provide_feedback("Mouse moved up")
        except Exception as e:
            self._provide_feedback(f"Mouse move error: {e}")
    
    def _mouse_move_down(self):
        """Mouse move down action"""
        try:
            pyautogui.moveRel(0, self.mouse_sensitivity, duration=self.mouse_speed)
            self._provide_feedback("Mouse moved down")
        except Exception as e:
            self._provide_feedback(f"Mouse move error: {e}")
    
    # Main control methods
    def get_mode(self) -> str:
        """Get the current gesture mode"""
        return "mouse"  # Always mouse mode
    
    def get_available_modes(self) -> List[str]:
        """Get list of available modes"""
        return ["mouse"]  # Only mouse mode
    
    def get_mode_info(self, mode: str) -> Dict:
        """Get information about a specific mode"""
        if mode == "mouse":
            return {
                "name": "Mouse Control",
                "description": "Control mouse pointer with hand movements"
            }
        return {}
    
    def start_gesture_control(self) -> bool:
        """Start mouse gesture control with webcam"""
        if not OPENCV_AVAILABLE:
            self._provide_feedback("OpenCV not available")
            return False
            
        try:
            # Try different camera backends and indices
            camera_found = False
            for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
                for index in [0, 1, 2]:
                    try:
                        print(f"🔍 Trying camera {index} with backend {backend}")
                        self.cap = cv2.VideoCapture(index, backend)
                        
                        if self.cap.isOpened():
                            # Test if camera is working by trying to read a frame
                            ret, frame = self.cap.read()
                            if ret and frame is not None:
                                print(f"✅ Camera {index} working with backend {backend}")
                                camera_found = True
                                break
                            else:
                                self.cap.release()
                        else:
                            self.cap.release()
                    except Exception as e:
                        print(f"❌ Camera {index} failed: {e}")
                        if hasattr(self, 'cap') and self.cap:
                            self.cap.release()
                        continue
                
                if camera_found:
                    break
            
            if not camera_found:
                self._provide_feedback("Could not access any webcam. Starting demo mode without camera.")
                # Start demo mode without camera
                self.is_running = True
                self._provide_feedback("Demo mode: Mouse control active (no camera)")
                return True
            
            self.is_running = True
            self._provide_feedback("Mouse gesture control started - camera window opening")
            
            # Start gesture detection in a separate thread
            self.gesture_thread = threading.Thread(target=self._gesture_detection_loop)
            self.gesture_thread.daemon = True
            self.gesture_thread.start()
            
            return True
            
        except Exception as e:
            self._provide_feedback(f"Error starting mouse control: {e}")
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
            return False
    
    def stop_gesture_control(self):
        """Stop mouse gesture control"""
        try:
            self.is_running = False
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
            if OPENCV_AVAILABLE:
                cv2.destroyAllWindows()
            self._provide_feedback("Mouse gesture control stopped")
        except Exception as e:
            print(f"Error stopping gesture control: {e}")
            self.is_running = False
    
    def _gesture_detection_loop(self):
        """Simple gesture detection loop with optimized performance"""
        print("🎥 Gesture detection loop started")
        
        # Check if we have a camera
        if not hasattr(self, 'cap') or self.cap is None:
            print("📱 Running in demo mode (no camera)")
            self._demo_mode_loop()
            return
        
        # Set camera properties for better performance
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduce resolution
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)  # Limit FPS
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
        except:
            pass  # Ignore if properties can't be set
        
        frame_count = 0
        last_fps_time = time.time()
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️ Could not read frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                height, width, _ = frame.shape
                
                # Process every other frame to reduce CPU load
                frame_count += 1
                if frame_count % 2 == 0:
                    continue
                
                # Detect hand
                hand_pos, contour, finger_count = self._simple_hand_detection(frame)
                # Smooth the position for steadier cursor control
                hand_pos_smoothed = self._smooth_position(hand_pos) if hand_pos else None
                
                # Draw mode info with better visibility
                mode_text = "Mouse Gesture Control"
                cv2.putText(frame, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Draw status
                status_text = "ACTIVE"
                status_color = (0, 255, 0)
                cv2.putText(frame, f"Status: {status_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                
                # Draw instructions
                cv2.putText(frame, "Control mouse pointer with hand movements", (10, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, "2 fingers = Left Click | 3 fingers = Right Click", (10, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, "Move hand = Move mouse", (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Process gestures
                if hand_pos_smoothed:
                    current_time = time.time()
                    if current_time - self.last_gesture_time > self.gesture_cooldown:
                        # Check for finger-based gestures first with debounce
                        if finger_count == 2 and (self.last_click_type != 'left' or not self.click_reset_required):
                            self.mouse_gestures["two_fingers"]()
                            self.last_click_type = 'left'
                            self.click_reset_required = True
                            self.last_gesture_time = current_time
                            cv2.putText(frame, "Gesture: Two Fingers", (10, 90), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                            cv2.putText(frame, "Action: Left Click", (10, 120), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        elif finger_count == 3 and (self.last_click_type != 'right' or not self.click_reset_required):
                            self.mouse_gestures["three_fingers"]()
                            self.last_click_type = 'right'
                            self.click_reset_required = True
                            self.last_gesture_time = current_time
                            cv2.putText(frame, "Gesture: Three Fingers", (10, 90), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                            cv2.putText(frame, "Action: Right Click", (10, 120), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        else:
                            # Check for movement gestures
                            gesture = self._detect_hand_movement(hand_pos_smoothed, self.last_hand_position)
                            
                            if gesture:
                                if gesture in self.mouse_gestures:
                                    self.mouse_gestures[gesture]()
                                    self.last_gesture_time = current_time
                                    
                                    # Draw gesture name with better positioning
                                    cv2.putText(frame, f"Gesture: {gesture}", (10, 90), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                                    
                                    # Draw action feedback
                                    action_text = f"Action: {gesture.replace('_', ' ').title()}"
                                    cv2.putText(frame, action_text, (10, 120), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    # Reset click debounce when hand not showing 2 or 3 fingers
                    if finger_count not in (2, 3):
                        self.click_reset_required = False
                        self.last_click_type = None

                    self.last_hand_position = hand_pos_smoothed
                
                # Display the frame
                cv2.imshow('Synbi Simple Gesture Control', frame)
                
                # Set window properties (try to keep it on top)
                try:
                    cv2.setWindowProperty('Synbi Simple Gesture Control', cv2.WND_PROP_TOPMOST, 1)
                except:
                    pass  # Ignore if not supported
                
                # Frame rate control - wait for key with timeout
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Exit key pressed, stopping gesture control")
                    break
                
                # Add small delay to prevent excessive CPU usage
                time.sleep(0.01)  # 10ms delay
                    
            except Exception as e:
                print(f"❌ Gesture detection error: {e}")
                time.sleep(0.1)
                continue
        
        # Cleanup
        print("🧹 Cleaning up gesture detection...")
        if self.cap:
            self.cap.release()
        if OPENCV_AVAILABLE:
            cv2.destroyAllWindows()
        print("✅ Gesture detection cleanup complete")
    
    def _demo_mode_loop(self):
        """Demo mode loop when camera is not available"""
        print("🎮 Demo mode: Mouse control active without camera")
        print("💡 In demo mode, you can still use voice commands to test mouse actions")
        
        while self.is_running:
            try:
                # In demo mode, just wait and provide feedback
                time.sleep(1)
                
                # Simulate some demo actions every 10 seconds
                if int(time.time()) % 10 == 0:
                    self._provide_feedback("Demo mode: Mouse gestures would work here")
                
            except Exception as e:
                print(f"❌ Demo mode error: {e}")
                time.sleep(1)
        
        print("✅ Demo mode stopped")

# Create a global instance
simple_gesture_controller = SimpleGestureController()

# Convenience functions
def start_simple_gesture_control():
    """Start simple gesture control"""
    return simple_gesture_controller.start_gesture_control()

def stop_simple_gesture_control():
    """Stop simple gesture control"""
    simple_gesture_controller.stop_gesture_control()

def set_simple_gesture_mode(mode: str):
    """Set simple gesture control mode (always mouse mode)"""
    return True  # Always return True since we only have mouse mode

def get_simple_gesture_mode():
    """Get current simple gesture mode"""
    return simple_gesture_controller.get_mode()

def get_available_simple_gesture_modes():
    """Get available simple gesture modes"""
    return simple_gesture_controller.get_available_modes()

def set_simple_gesture_feedback_callback(callback):
    """Set feedback callback for simple gesture actions"""
    simple_gesture_controller.set_feedback_callback(callback)
