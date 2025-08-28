#!/usr/bin/env python3
"""
Setup script for Unified Ads Campaign Insights Prototype
Runs the complete data pipeline and starts services
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    return run_command("pip install -r requirements.txt", "Dependency installation")

def setup_data_pipeline():
    """Run the complete data pipeline"""
    steps = [
        ("python src/data_generator.py", "Mock data generation"),
        ("python src/data_processor.py", "Data processing and normalization"),
        ("python src/anomaly_detector.py", "Anomaly detection"),
        ("python src/insights_generator.py", "Insights generation")
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            return False
    
    return True

def start_services():
    """Start the API and dashboard services"""
    print("\n🚀 Starting services...")
    print("📊 API will be available at: http://localhost:8000")
    print("📈 Dashboard will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop services\n")
    
    try:
        # Start FastAPI in background
        api_process = subprocess.Popen(
            ["python", "src/api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give API time to start
        time.sleep(3)
        
        # Start Streamlit dashboard
        dashboard_process = subprocess.Popen(
            ["streamlit", "run", "src/dashboard.py", "--server.port=8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("✅ Services started successfully!")
        print("\n📋 Available endpoints:")
        print("  • API Documentation: http://localhost:8000/docs")
        print("  • Health Check: http://localhost:8000/health")
        print("  • Dashboard: http://localhost:8501")
        
        # Wait for user interruption
        try:
            api_process.wait()
            dashboard_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            api_process.terminate()
            dashboard_process.terminate()
            print("✅ Services stopped")
            
    except Exception as e:
        print(f"❌ Failed to start services: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🎯 Unified Ads Campaign Insights Prototype Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Setup data pipeline
    if not setup_data_pipeline():
        print("❌ Data pipeline setup failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📊 Data Summary:")
    
    # Show data summary
    try:
        import pandas as pd
        if os.path.exists('data/unified_ad_data_with_anomalies.csv'):
            df = pd.read_csv('data/unified_ad_data_with_anomalies.csv')
            print(f"  • Total records: {len(df):,}")
            print(f"  • Platforms: {', '.join(df['platform'].unique())}")
            print(f"  • Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"  • Campaigns: {df['campaign_name'].nunique()}")
    except Exception as e:
        print(f"  • Could not load data summary: {e}")
    
    # Ask user if they want to start services
    response = input("\n🚀 Start API and Dashboard services? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        start_services()
    else:
        print("\n✅ Setup complete! You can manually start services later:")
        print("  • API: python src/api.py")
        print("  • Dashboard: streamlit run src/dashboard.py")

if __name__ == "__main__":
    main()
