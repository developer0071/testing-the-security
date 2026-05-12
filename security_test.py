import time
import argparse
import os
import glob
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

FRAME_PATH = "static/monitor.png"
MAX_ERROR_DUMPS = 5
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}

def run_garbage_collection():
    try:
        error_files = sorted(glob.glob("static/error_dump_*.png"), key=os.path.getmtime)
        while len(error_files) > MAX_ERROR_DUMPS:
            os.remove(error_files.pop(0))
    except Exception:
        pass

def capture_frame(page):
    try:
        page.screenshot(path=FRAME_PATH)
    except:
        pass

def is_allowed_target(url):
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.hostname in ALLOWED_HOSTS

def run_security_flow(target_url, iterations, delay_ms):
    if not is_allowed_target(target_url):
        raise ValueError("This local runner only accepts localhost, 127.0.0.1, or ::1 targets.")

    delay_sec = delay_ms / 1000.0
    run_garbage_collection()
    os.makedirs("static", exist_ok=True)

    with sync_playwright() as p:
        # Set headless=False if you want to visibly see the browser popping up alongside your UI
        # Set headless=True to test the "CCTV" telemetry stream exactly as the VM will do it
        browser = p.chromium.launch(
            headless=True, 
            args=['--disable-dev-shm-usage', '--disable-disk-cache', '--incognito']
        ) 
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        for i in range(iterations):
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                capture_frame(page)

                button = page.get_by_role("button").first
                if button.count() > 0:
                    button.click()
                    time.sleep(0.5)
                    capture_frame(page)

                page.mouse.wheel(0, 300)
                time.sleep(0.5)
                capture_frame(page)

                time.sleep(delay_sec)

            except Exception as e:
                page.screenshot(path=f"static/error_dump_{i}.png")
                run_garbage_collection() 
                break 

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000/test-target")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--rate", type=int, default=1000)
    args = parser.parse_args()
    
    run_security_flow(target_url=args.url, iterations=args.limit, delay_ms=args.rate)
