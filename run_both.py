import subprocess
import sys
import time
import threading
import os

def run_fastapi():
    """Run FastAPI backend server"""
    print("🚀 Starting FastAPI Backend Server...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ FastAPI server stopped.")
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")

def run_streamlit():
    """Run Streamlit frontend"""
    print("🎨 Starting Streamlit Frontend...")
    time.sleep(3)  # Wait for FastAPI to start
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ Streamlit server stopped.")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def main():
    print("🔥 AI Skincare Recommendation System - Full Stack Launcher")
    print("=" * 60)
    print("📋 This will start:")
    print("   1. FastAPI Backend (http://localhost:8000)")
    print("   2. Streamlit Frontend (http://localhost:8501)")
    print("=" * 60)
    
    # Check if files exist
    required_files = ["main.py", "streamlit_app.py", ".env"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please make sure all files are in the current directory.")
        return
    
    try:
        # Start FastAPI in a separate thread
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Start Streamlit in main thread
        run_streamlit()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        print("✅ Both servers stopped successfully!")

if __name__ == "__main__":
    main()