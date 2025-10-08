#!/usr/bin/env python3
"""
Synbi Main Entry Point
Run this file to start Synbi
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from Synbi import main_process
        print("🚀 Starting Synbi...")
        main_process()
    except ImportError as e:
        print(f"❌ Error importing Synbi: {e}")
        print("Make sure Synbi.py is in the same directory")
    except Exception as e:
        print(f"❌ Error starting Synbi: {e}")
        input("Press Enter to exit...")
