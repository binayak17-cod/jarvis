#!/usr/bin/env python3
"""
Synbi Startup Script
Automatically starts Synbi when run
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run Synbi
    from Synbi import main_process
    print("🚀 Starting Synbi...")
    main_process()
except ImportError as e:
    print(f"❌ Error importing Synbi: {e}")
    print("Make sure Synbi.py is in the same directory")
except Exception as e:
    print(f"❌ Error starting Synbi: {e}")
    input("Press Enter to exit...")




