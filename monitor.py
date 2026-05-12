import os
import argparse
from playwright.sync_api import sync_playwright

def run_check(target_url):
    print(f"Initiating remote health & security check on: {target_url}")
    
    # Create the directory for GitHub Actions to pick up the screenshots
    os.makedirs("artifacts", exist_ok=True)

    with sync_playwright() as p:
        # High-efficiency arguments required for cloud runners
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox', '--incognito']
        )
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        try:
            # 1. Navigate to the target
            response = page.goto(target_url, wait_until="networkidle", timeout=30000)
            print(f"Server responded with HTTP {response.status}")

            if response.status >= 400:
                raise Exception(f"HTTP Error encountered: {response.status}")

            # 2. Add any specific interaction logic here if needed
            # e.g., page.get_by_role("button", name="Login").click()

            # 3. Capture successful state
            page.screenshot(path="artifacts/success_state.png")
            print("[✓] Execution complete. State captured successfully.")

        except Exception as e:
            print(f"[✗] Execution failed: {e}")
            page.screenshot(path="artifacts/error_state.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target URL to test")
    args = parser.parse_args()
    
    run_check(args.url)