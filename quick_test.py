#!/usr/bin/env python3
"""
Quick test to diagnose Synbi command issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic Synbi functionality"""
    print("🔍 Quick Synbi Diagnostic Test")
    print("=" * 40)
    
    try:
        # Test import
        print("1. Testing imports...")
        import Synbi
        print("✅ Synbi imports successfully")
        
        # Test TTS
        print("\n2. Testing TTS...")
        Synbi.speak("Hello, this is a test")
        print("✅ TTS working")
        
        # Test command function
        print("\n3. Testing command function...")
        print("🎤 This will test voice input (will timeout after 5 seconds)")
        print("💡 Say 'hello' when prompted, or wait for timeout")
        
        request = Synbi.command()
        if request:
            print(f"✅ Voice input received: '{request}'")
        else:
            print("❌ No voice input received")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_text_mode():
    """Test text mode functionality"""
    print("\n4. Testing text mode...")
    try:
        # Simulate text input
        test_request = "hello"
        print(f"🔤 Simulating text input: '{test_request}'")
        
        # Test process_command function
        from Synbi import process_command
        result = process_command(test_request)
        print(f"✅ Command processed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text mode error: {e}")
        return False

if __name__ == "__main__":
    # Run tests
    basic_ok = test_basic_functionality()
    text_ok = test_text_mode()
    
    print("\n📊 Results:")
    print(f"Basic functionality: {'✅ OK' if basic_ok else '❌ FAIL'}")
    print(f"Text mode: {'✅ OK' if text_ok else '❌ FAIL'}")
    
    if basic_ok and text_ok:
        print("\n🎉 All tests passed! Synbi should be working.")
        print("💡 Try running: python Synbi.py")
        print("💡 If voice doesn't work, say 'text mode' to switch to typing")
    else:
        print("\n⚠️ Issues detected. Check the error messages above.")
