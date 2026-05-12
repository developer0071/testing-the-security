import os
import time
import argparse
import asyncio
from playwright.async_api import async_playwright
from faker import Faker

# Initialize the Faker generator
fake = Faker()

async def register_user(browser, target_url, i, limit):
    print(f"--- Firing User Registration {i+1}/{limit} ---")
    context = await browser.new_context(viewport={"width": 1280, "height": 720})
    page = await context.new_page()
    
    try:
        response = await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        if response.status >= 400:
            raise Exception(f"HTTP Error: {response.status}")

        await page.get_by_role("link", name="Sign in").click()
        
        await page.wait_for_selector("text='Create account'", state="visible")
        await page.get_by_text("Create account").first.click()
        
        await page.wait_for_selector("text='Job Seeker'", state="visible")
        await page.get_by_text("Job Seeker").click()

        # Generate realistic human data
        bot_first_name = fake.first_name()
        bot_last_name = fake.last_name()
        
        # Create an organic-looking email (e.g., john.doe.17155000@gmail.com)
        test_email = f"{bot_first_name.lower()}.{bot_last_name.lower()}.{int(time.time())}.{i+1}@gmail.com"
        
        print(f"Injecting organic data: {bot_first_name} {bot_last_name} ({test_email})")
        
        await page.get_by_placeholder("Jahongir").fill(bot_first_name)
        await page.get_by_placeholder("Djurayev").fill(bot_last_name)
        await page.get_by_placeholder("you@example.com").fill(test_email)
        
        passwords = page.locator('input[type="password"]')
        await passwords.first.fill("TestSecure123!")
        await passwords.last.fill("TestSecure123!")
        
        await page.get_by_role("button", name="Create account").last.click()
        
        # Validate success by looking for the newly generated organic name on the dashboard
        await page.wait_for_selector(f"text='{bot_first_name} {bot_last_name}'", state="visible", timeout=20000) 
        
        print(f"[✓] Success: {test_email}")
        
        if i == limit - 1:
            await page.screenshot(path="artifacts/final_success_state.png")

    except Exception as e:
        print(f"[✗] Iteration {i+1} failed: {e}")
        await page.screenshot(path=f"artifacts/error_state_loop_{i+1}.png")
    finally:
        await context.close()

async def run_provisioning_async(target_url, limit, concurrency):
    print(f"Initiating HIGH-SPEED bulk registration on: {target_url}")
    print(f"Target: {limit} users. Executing {concurrency} in parallel.")
    
    os.makedirs("artifacts", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox', '--incognito', '--disable-gpu']
        )

        sem = asyncio.Semaphore(concurrency)

        async def bounded_register(i):
            async with sem:
                await register_user(browser, target_url, i, limit)

        tasks = [bounded_register(i) for i in range(limit)]
        await asyncio.gather(*tasks)

        await browser.close()
        print("\nProvisioning sequence complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=3) 
    args = parser.parse_args()
    
    asyncio.run(run_provisioning_async(args.url, args.limit, args.concurrency))