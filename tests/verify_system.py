import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys

def verify_imports():
    print("🧪 Verifying backend imports...")
    try:
        from backend.agents import convert_num_to_text, convert_text_to_num, orchestrator_router
        print("✅ backend.agents imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import backend.agents: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in backend.agents: {e}")
        return False

    try:
        from backend.graph import app
        print("✅ backend.graph imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import backend.graph: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in backend.graph: {e}")
        return False

    try:
        from backend.api import app as fastapi_app
        print("✅ backend.api imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import backend.api: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in backend.api: {e}")
        return False

    print("✨ All backend imports verified!")
    return True

if __name__ == "__main__":
    if not verify_imports():
        sys.exit(1)
