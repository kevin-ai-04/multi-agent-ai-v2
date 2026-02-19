import os
import sys
import subprocess
import platform

def main():
    print("🤖 Starting Multi-Agent System...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    # Commands
    # We use sys.executable to ensure we use the same python interpreter (virtualenv aware)
    backend_cmd = f"{sys.executable} -m uvicorn backend.api:app --reload"
    frontend_cmd = "npm run dev"

    if platform.system() == "Windows":
        print("🚀 Launching Backend API (New Window)...")
        # cmd /k keeps the window open so logs are visible
        subprocess.Popen(f'start "Backend API" cmd /k "{backend_cmd}"', shell=True)
        
        print("🚀 Launching Frontend (New Window)...")
        subprocess.Popen(f'start "Frontend" cmd /k "{frontend_cmd}"', shell=True, cwd=frontend_dir)
        
    else:
        # Simple fallback for other OSs (prints instructions)
        print("⚠️  This script is designed for Windows new window launching.")
        print(f"👉 Backend: {backend_cmd}")
        print(f"👉 Frontend: cd frontend && {frontend_cmd}")
        return

    print("\n✅ Application handling handed off to new windows.")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:5173")

if __name__ == "__main__":
    main()
