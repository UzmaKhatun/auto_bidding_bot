from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./session",
        headless=False
    )
    page = browser.new_page()
    page.goto("https://www.linkedin.com/login")
    
    print("Login manually in the browser window")
    print("After login press Enter here...")
    input()
    
    browser.close()
    print("Session saved successfully!")