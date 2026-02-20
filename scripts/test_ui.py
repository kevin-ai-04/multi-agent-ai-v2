import os
import time
from playwright.sync_api import sync_playwright

# Set HOME environment variable to USERPROFILE to fix potential path issues
if "HOME" not in os.environ:
    os.environ["HOME"] = os.environ.get("USERPROFILE")

def run_ui_tests():
    print("Starting UI Tests with Playwright...")
    
    with sync_playwright() as p:
        # Launch browser (headless=True for CI/Background execution)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Navigate to App
            print("Navigating to http://localhost:8501...")
            page.goto("http://localhost:8501", timeout=60000)
            
            # Wait for app to load (look for title)
            page.wait_for_selector("h1", timeout=30000)
            print("✅ App Loaded")
            
            # 2. Test Num2Text
            print("\nTest 1: Num2Text (42)")
            # Streamlit chat input is often an input or textarea
            page.fill("input[data-testid='stChatInput']", "42")
            page.press("input[data-testid='stChatInput']", "Enter")
            
            # Wait for response (look for output text)
            # This is tricky because Streamlit updates dynamically. 
            # We wait for the specific text "forty-two"
            try:
                page.wait_for_selector("text=forty-two", timeout=15000)
                print("✅ Num2Text Passed: Found 'forty-two'")
            except Exception:
                print("❌ Num2Text Failed: Did not find 'forty-two'")
                # Capture screenshot for debugging
                page.screenshot(path="debug_num2text.png")
            
            # 3. Test Text2Num
            print("\nTest 2: Text2Num (one hundred)")
            page.fill("input[data-testid='stChatInput']", "one hundred")
            page.press("input[data-testid='stChatInput']", "Enter")
            
            try:
                page.wait_for_selector("text=100", timeout=15000)
                print("✅ Text2Num Passed: Found '100'")
            except Exception:
                print("❌ Text2Num Failed: Did not find '100'")
                page.screenshot(path="debug_text2num.png")

            # 4. Test Orchestrator Logic Status
            # Check if we can find "Routing to..." text in the steps
            # Might need to expand the expander if not auto-expanded.
            # But the backend test covered logic well.
            
            # 5. Test Service Unavailable
            print("\nTest 3: Service Unavailable")
            # Click toggle to disable Agent A
            # Toggles in Streamlit can be tricky to select by text.
            # Assuming first toggle is Agent A.
            
            # Find checkbox/toggle. 
            # This is fragile, so we might skip if selectors are complex, 
            # but let's try finding by label text.
            try:
                toggle = page.get_by_text("Enable Agent A (Num2Text)")
                if toggle:
                    toggle.click()
                    print("Clicked Toggle A")
                    time.sleep(1)
                    
                    page.fill("input[data-testid='stChatInput']", "55")
                    page.press("input[data-testid='stChatInput']", "Enter")
                    
                    page.wait_for_selector("text=Service Unavailable", timeout=15000)
                    print("✅ Service Unavailable Passed")
                else:
                     print("⚠️ Could not find toggle")
            except Exception as e:
                print(f"❌ Service Unavailable Test Failed: {e}")
                page.screenshot(path="debug_unavailable.png")

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            page.screenshot(path="debug_critical.png")
            
        finally:
            browser.close()
            print("\nUI Tests Completed.")

if __name__ == "__main__":
    run_ui_tests()
