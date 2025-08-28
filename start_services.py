#!/usr/bin/env python3
"""
Simple service starter with visible output for debugging
"""

import subprocess
import sys
import time
import os

def start_api():
    """Start FastAPI with visible output"""
    print("🚀 Starting FastAPI server...")
    try:
        # Change to project directory
        os.chdir('/home/metanet/ProgramFiles/right-programmers')
        
        # Start API with visible output
        subprocess.run([
            sys.executable, "src/api.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Failed to start API: {e}")

def start_dashboard():
    """Start Streamlit dashboard with visible output"""
    print("🚀 Starting Streamlit dashboard...")
    try:
        # Change to project directory
        os.chdir('/home/metanet/ProgramFiles/right-programmers')
        
        # Start dashboard with visible output
        subprocess.run([
            "streamlit", "run", "src/dashboard.py", 
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python start_services.py [api|dashboard]")
        sys.exit(1)
    
    service = sys.argv[1].lower()
    
    if service == "api":
        start_api()
    elif service == "dashboard":
        start_dashboard()
    else:
        print("Invalid service. Use 'api' or 'dashboard'")
        sys.exit(1)
