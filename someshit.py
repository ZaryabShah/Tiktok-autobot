#!/usr/bin/env python3
# tiktok_demo_bot_playwright.py - Playwright version

import json
import random
import shelve
import sys
import time
import requests
from pathlib import Path
from typing import List, Tuple, Optional
from playwright.sync_api import sync_playwright, TimeoutError, Error
from faker import Faker

# ========================= USER CONFIG ================================
COOKIE_FILE = Path(r"C:\Users\Shahzeb\Desktop\Python\tiktok_bot\saved_cookies\cookies.JSON")
PROXY_RAW = """
72.9.171.237,12323,14acfa7f9a57c,74f453f102
72.9.168.192,12323,14acfa7f9a57c,74f453f102
72.9.171.59,12323,14acfa7f9a57c,74f453f102
84.55.9.31,12323,14acfa7f9a57c,74f453f102
84.55.9.214,12323,14acfa7f9a57c,74f453f102
185.134.193.213,12323,14acfa7f9a57c,74f453f102
""".strip().splitlines()

COMMENTS = [
    "This is 🔥 Had to drop a like!",
    "no way 😂 actually works",
    "Legit the most accurate tracker I've tried!",
    "bookmarking this - super handy",
    "first app that actually does the job lmao",
]

DELAY = (2.0, 4.0)                # Random human-sleep window
ACCOUNT_KEY = "default"           # Only one TikTok account for now
CAPTCHA_API_KEY = "95a48de2c0msh428436f5f09baebp191df7jsn5192af7e037f"
MAX_CAPTCHA_RETRIES = 2           # Max attempts to solve captcha
ACTION_RETRIES = 3                # Retries for individual actions
LOGIN_CHECK_TIMEOUT = 15          # Seconds to verify login status

# ========================= SELECTORS (July 2025) =======================
XP = {
    # Cookie dialogs
    "decline_cookies": "//button[contains(., 'Decline') and contains(., 'optional cookies')]",
    "accept_cookies": "//button[contains(., 'Accept') and contains(., 'cookies')]",
    
    # Video controls
    "video_player": "//div[@data-e2e='video-player']",
    "pause_button": "//div[contains(@class, 'play-button')]",
    
    # Operator bar
    "bar": "//div[contains(@class,'DivOperaterArea')]",
    "like": [
        "//div[@data-e2e='video-like-button']",  # Old UI
        "//*[@id='app']/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[1]/div/div[2]"  # New UI
    ],
    "comment": "//div[@data-e2e='video-comment-button']",
    "share": "//div[@data-e2e='video-share-button']",

    # Share sheet
    "share_sheet": "//div[contains(@class,'DivShareContainer') or contains(@class, 'share-sheet')]",
    "save_button": "//div[@aria-label='Save video' or contains(@aria-label, 'Save')]",
    "share_close": "//button[@aria-label='Close' or @data-e2e='share-close']",

    # Comment workflow
    "comment_box": [
        "//div[contains(@placeholder, 'Add comment')]",  # New UI
        "//div[contains(@data-e2e,'comment-input')]"     # Old UI
    ],
    "comment_input": "//div[@role='textbox']",
    "comment_post": [
        "//div[text()='Post']",                 # New UI
        "//button[@data-e2e='comment-post']"     # Old UI
    ],
    "comment_like": "(//div[@data-e2e='comment-list']//button[@data-e2e='like-icon'])[last()]",

    # Captcha elements
    "captcha_iframe": "//iframe[contains(@src,'captcha') or contains(@src,'challenge')]",
    "captcha_image1": "//img[@data-e2e='captcha-image1']",
    "captcha_image2": "//img[@data-e2e='captcha-image2']",
    "captcha_wheel": "//div[@data-e2e='captcha-wheel']",
    "captcha_submit": "//button[@data-e2e='captcha-submit']",
    
    # Login indicators
    "avatar_icon": "//div[@data-e2e='top-avatar']",
    "upload_button": "//div[contains(text(),'Upload')]",
    
    # Misc overlays
    "close_button": "//button[@aria-label='Close']",
    "not_now_button": "//button[text()='Not now' or text()='Not Now']",
}

# Popup dismissal priority (order matters)
POPUPS = [
    XP["decline_cookies"],
    XP["accept_cookies"],
    XP["close_button"],
    XP["not_now_button"],
    "//button[contains(text(),'Accept all')]",
    "//button[contains(text(),'Continue watching')]",
    "//div[@role='dialog']//button[.//*[@aria-label='Close']]",
]

# ========================= INTERNALS =================================
fake = Faker()
PROXY_POOL = [
    f"{u}:{pwd}@{h}:{p}" for h, p, u, pwd in (row.split(",") for row in PROXY_RAW)
]
PROXY_DB = Path("_proxy_bindings.db")

# ========================= UTILITIES =================================
def zzz(a: float = DELAY[0], b: float = DELAY[1]) -> None:
    """Randomized human-like delay"""
    time.sleep(random.uniform(a, b))

def pick_proxy(key: str = ACCOUNT_KEY) -> str:
    """Select a healthy proxy from the pool"""
    with shelve.open(str(PROXY_DB)) as db:
        now = time.time()
        for k, (px, ts) in list(db.items()):
            if ts and now - ts > 24 * 3600:  # Rehabilitate after 24h
                db[k] = (px, None)
                
        if key in db and db[key][1] is None:
            return db[key][0]
            
        taken = {v[0] for v in db.values() if v[1] is None}
        for proxy in PROXY_POOL:
            if proxy not in taken:
                db[key] = (proxy, None)
                return proxy
    raise RuntimeError("No healthy proxies available")

def mark_bad(proxy: str, key: str = ACCOUNT_KEY) -> None:
    """Flag a proxy as temporarily unusable"""
    with shelve.open(str(PROXY_DB)) as db:
        db[key] = (proxy, time.time())

def load_cookies(context, path: Path) -> bool:
    """Inject saved cookies into browser and verify"""
    with path.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    
    cookies = []
    seen = set()
    for c in raw:
        dom = c["domain"].lstrip(".")
        if (c["name"], dom) in seen: 
            continue
        seen.add((c["name"], dom))
        cookies.append({
            "name": c["name"],
            "value": c["value"],
            "domain": dom,
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
            "expires": c.get("expirationDate", time.time() + 3600)
        })
    
    context.add_cookies(cookies)
    return True

def visible(page, xp: str) -> bool:
    """Check if element is visible"""
    try:
        return page.locator(xp).is_visible(timeout=2000)
    except (TimeoutError, Error):
        return False

def dismiss_popups(page, max_loops: int = 3) -> None:
    """Dismiss various popups and overlays"""
    for _ in range(max_loops):
        found_any = False
        for selector in POPUPS:
            if visible(page, selector):
                try:
                    page.locator(selector).click(timeout=2000)
                    print(f"Dismissed popup: {selector}")
                    zzz(1, 2)
                    found_any = True
                except (TimeoutError, Error):
                    pass
        if not found_any:
            break

def try_click(page, selector, label: str, retries: int = ACTION_RETRIES) -> bool:
    """
    Attempt to click element with intelligent retries
    - selector can be string or list of strings (fallback)
    """
    if isinstance(selector, str):
        selectors = [selector]
    else:
        selectors = selector
        
    for attempt in range(1, retries + 1):
        dismiss_popups(page)
        
        for xp in selectors:
            try:
                if page.locator(xp).is_visible(timeout=2000):
                    page.locator(xp).click(timeout=3000)
                    print(f"{label} ✅")
                    zzz()
                    return True
            except (TimeoutError, Error):
                print(f"{label} intercepted - retry {attempt}/{retries}")
                zzz(1, 2)
                break  # Break to next attempt
        else:
            # No visible elements in this attempt
            zzz(1.5, 2.5)
            
    print(f"{label} ❌ not found after {retries} attempts")
    return False

def solve_captcha(page) -> bool:
    """Solve TikTok captcha using API service"""
    print("⚠️ Captcha detected - attempting to solve...")
    
    # Switch to captcha iframe
    iframe = page.locator(XP["captcha_iframe"])
    frame = iframe.content_frame()
    
    # Extract image URLs
    try:
        img1 = frame.locator(XP["captcha_image1"]).get_attribute("src", timeout=5000)
        img2 = frame.locator(XP["captcha_image2"]).get_attribute("src", timeout=5000)
        print(f"Captcha images: {img1[:50]}... and {img2[:50]}...")
    except Exception as e:
        print(f"Failed to get captcha images: {e}")
        return False

    # Call captcha solving API
    payload = {
        "cap_type": "whirl",
        "url1": img1,
        "url2": img2
    }
    headers = {
        "x-rapidapi-key": CAPTCHA_API_KEY,
        "x-rapidapi-host": "tiktok-captcha-solver2.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://tiktok-captcha-solver2.p.rapidapi.com/tiktok/captcha",
            json=payload,
            headers=headers,
            timeout=15
        )
        result = response.json()
        print(f"Captcha API response: {result}")
        
        if "angle" in result:
            angle = result["angle"]
            print(f"Solved captcha - required angle: {angle}°")
            # TODO: Implement rotation logic here
            # For now, just submit
            frame.locator(XP["captcha_submit"]).click()
            zzz(3)
            print("✅ Captcha submitted")
            return True
        else:
            print("❌ Captcha solution not found in response")
            
    except Exception as e:
        print(f"Captcha API error: {e}")
    
    return False

def verify_login(page) -> bool:
    """Check if we're properly logged in"""
    start_time = time.time()
    while time.time() - start_time < LOGIN_CHECK_TIMEOUT:
        if visible(page, XP["avatar_icon"]) or visible(page, XP["upload_button"]):
            print("✅ Verified logged in status")
            return True
        zzz(1)
    print("❌ Failed to verify login status")
    return False

# ========================= VIDEO HANDLING =============================
def ensure_video_ready(page) -> bool:
    """Prepare video for interaction"""
    # Pause video to prevent controls from disappearing
    if not try_click(page, XP["video_player"], "pause video", 2):
        print("⚠️ Couldn't pause video - proceeding anyway")
    
    # Ensure controls are visible
    timeout = time.time() + 10
    while not visible(page, XP["bar"]) and time.time() < timeout:
        page.mouse.wheel(0, 100)  # Scroll down
        zzz(0.5, 1)
        page.mouse.wheel(0, -100)  # Scroll up
        zzz(0.5, 1)
    
    return visible(page, XP["bar"])

def handle_like(page) -> None:
    """Handle like action with state detection and retries"""
    print("Attempting like action...")
    
    # Check if already liked
    for selector in XP["like"]:
        try:
            if page.locator(f"{selector}//*[name()='svg' and @fill='#FE2C55']").is_visible(timeout=1000):
                print("❤️ Already liked")
                return
        except (TimeoutError, Error):
            pass
            
    # Attempt to like with retries
    if try_click(page, XP["like"], "like", ACTION_RETRIES):
        # Verify like succeeded
        zzz(2, 3)
        for selector in XP["like"]:
            try:
                if page.locator(f"{selector}//*[name()='svg' and @fill='#FE2C55']").is_visible(timeout=1000):
                    print("❤️ Like successful")
                    return
            except (TimeoutError, Error):
                pass
        print("⚠️ Like action uncertain")
    else:
        print("❌ Failed to like video")

def handle_share(page) -> None:
    """Handle share and save actions with robust closing"""
    print("Attempting share action...")
    if try_click(page, XP["share"], "share", ACTION_RETRIES):
        zzz(2, 3)
        if visible(page, XP["share_sheet"]):
            # Try to save video
            if try_click(page, XP["save_button"], "save video", ACTION_RETRIES):
                zzz(1, 2)
            # Always close share sheet
            for _ in range(ACTION_RETRIES):
                if try_click(page, XP["share_close"], "close share sheet", 1):
                    break
                else:
                    # Alternative close method
                    page.keyboard.press("Escape")
                    zzz(1)

def handle_comment(page) -> None:
    """Handle comment actions with robust typing and posting"""
    print("Attempting comment action...")
    if try_click(page, XP["comment_box"], "open comment box", ACTION_RETRIES):
        zzz(1, 2)
        # Type comment
        comment = random.choice(COMMENTS)
        
        # Robust typing with fallback
        for selector in XP["comment_box"]:
            try:
                if page.locator(selector).is_visible(timeout=1000):
                    page.locator(selector).fill(comment)
                    print(f"💬 Typed comment: {comment[:20]}...")
                    break
            except (TimeoutError, Error):
                continue
        
        zzz(1, 2)
        
        # Post comment
        if try_click(page, XP["comment_post"], "post comment", ACTION_RETRIES):
            zzz(2, 3)
            # Like own comment
            try_click(page, XP["comment_like"], "like own comment", ACTION_RETRIES)
        else:
            # Clear comment if failed to post
            try:
                page.locator(XP["comment_box"][0]).fill("")
            except (TimeoutError, Error):
                pass

def handle_video(page, url: str) -> bool:
    """Full workflow for a single video with enhanced robustness"""
    print(f"\n▶ Processing: {url}")
    page.goto(url, timeout=60000)
    zzz(7, 10)
    
    # Initial popup dismissal with priority on cookies
    for _ in range(3):
        dismiss_popups(page)
        if visible(page, XP["decline_cookies"]):
            if try_click(page, XP["decline_cookies"], "decline cookies", 2):
                break
        elif visible(page, XP["accept_cookies"]):
            if try_click(page, XP["accept_cookies"], "accept cookies", 2):
                break
        zzz(1)
    
    # Handle captcha before any actions
    captcha_attempts = 0
    while visible(page, XP["captcha_iframe"]) and captcha_attempts < MAX_CAPTCHA_RETRIES:
        if solve_captcha(page):
            break
        captcha_attempts += 1
        zzz(5, 7)
    
    if visible(page, XP["captcha_iframe"]):
        print("❌ Captcha not solved - skipping video")
        return False
    
    # Prepare video for interaction
    if not ensure_video_ready(page):
        print("❌ Video controls not available - skipping")
        return False
    
    # Execute actions with individual retry mechanisms
    handle_like(page)
    handle_share(page)
    handle_comment(page)
    
    print("✅ Video processed successfully")
    return True

# ========================= MAIN LOOP =================================
def run_all(urls: List[str]) -> None:
    """Process all URLs with proxy rotation and login verification"""
    pending = urls[:]
    while pending:
        proxy = pick_proxy()
        ip = proxy.split("@")[-1].split(":")[0]
        print(f"\n=== Using proxy: {ip} ===\n")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    proxy={"server": f"http://{proxy}"},
                    args=[
                        f"--user-agent={fake.chrome()}",
                        "--disable-images",
                        "--disable-gpu"
                    ]
                )
                context = browser.new_context()
                page = context.new_page()
                
                # Initial setup with robust cookie handling
                page.goto("https://www.tiktok.com/", timeout=60000)
                zzz(3, 5)
                
                # Load cookies and verify login
                load_cookies(context, COOKIE_FILE)
                page.reload()
                zzz(5, 7)
                
                if not verify_login(page):
                    print("❌ Login verification failed - skipping session")
                    mark_bad(proxy)
                    continue
                
                # Process videos
                for url in pending[:]:
                    success = handle_video(page, url)
                    if success:
                        pending.remove(url)
                    zzz(3, 5)  # Between videos
                
                browser.close()
        
        except RuntimeError as e:  # Captcha error
            print(f"⚠️ {e} - quarantining proxy {ip}")
            mark_bad(proxy)
        except Exception as e:
            print(f"🚨 Fatal error: {e}")
            break

# ========================= ENTRY POINT ===============================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tiktok_demo_bot_playwright.py <video_url> [more URLs...]")
        sys.exit(1)
        
    run_all(sys.argv[1:])
    print("\nBot finished processing all URLs")