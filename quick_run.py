import os
import sys
import subprocess
import platform

def main():
    print("🤖 Starting Multi-Agent System...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    db_path = os.path.join(base_dir, "backend", "data", "procurement.db")
    db_init_script = os.path.join(base_dir, "scripts", "db_init.py")

    # Check if database exists, if not, run db_init
    if not os.path.exists(db_path):
        print(f"📦 Database not found at {db_path}. Initializing...")
        try:
            # Run db_init using the same python interpreter
            subprocess.run([sys.executable, db_init_script], check=True)
            print("✅ Database initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize database: {e}")
            return
    
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
