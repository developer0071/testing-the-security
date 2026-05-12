import os
import time
import argparse
from playwright.sync_api import sync_playwright

def run_provisioning(target_url, limit, delay_ms):
    print(f"Initiating bulk registration test on: {target_url}")
    print(f"Target: {limit} users. Delay: {delay_ms}ms between requests.")
    
    os.makedirs("artifacts", exist_ok=True)
    delay_sec = delay_ms / 1000.0

    with sync_playwright() as p:
        # High-efficiency cloud arguments
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox', '--incognito']
        )

        for i in range(limit):
            print(f"\n--- Starting User Registration {i+1}/{limit} ---")
            
            # Opening a fresh context per user ensures zero cookie/cache crossover
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()

            try:
                response = page.goto(target_url, wait_until="networkidle", timeout=30000)
                if response.status >= 400:
                    raise Exception(f"HTTP Error: {response.status}")

                page.get_by_role("link", name="Sign in").click()
                page.get_by_role("button", name="Create account").click()
                page.get_by_text("Job Seeker").click()

                # Generate a unique tracking email for this specific loop iteration
                test_email = f"qa.bot.{int(time.time())}.{i+1}@gmail.com"
                
                print(f"Injecting data: {test_email}")
                page.get_by_placeholder("Jahongir").fill(f"QABot")
                page.get_by_placeholder("Djurayev").fill(f"Test{i+1}")
                page.get_by_placeholder("you@example.com").fill(test_email)
                
                page.locator('input[type="password"]').first.fill("TestSecure123!")
                page.locator('input[type="password"]').last.fill("TestSecure123!")
                
                page.get_by_role("button", name="Create account").last.click()
                page.wait_for_url("**/search", timeout=20000) 
                
                print(f"[✓] Success: {test_email}")
                
                # Capture a screenshot of the final iteration to prove it finished
                if i == limit - 1:
                    page.screenshot(path="artifacts/final_success_state.png")

            except Exception as e:
                print(f"[✗] Iteration {i+1} failed: {e}")
                page.screenshot(path=f"artifacts/error_state_loop_{i+1}.png")
                # We don't raise the error here, so the loop can try the next user if one fails
            finally:
                context.close() # Clean up RAM before the next iteration
                
            if i < limit - 1:
                print(f"Waiting {delay_ms}ms before next registration...")
                time.sleep(delay_sec)

        browser.close()
        print("\nProvisioning sequence complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--limit", type=int, default=1, help="Number of users to create")
    parser.add_argument("--delay", type=int, default=1000, help="Delay in ms between registrations")
    args = parser.parse_args()
    
    run_provisioning(target_url=args.url, limit=args.limit, delay_ms=args.delay)