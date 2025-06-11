#!/usr/bin/env python3
"""
TikTok Automation Bot - Desktop-Only Version
============================================
Features (same as before, but forces desktop site):
- No mobile emulation → always navigates to www.tiktok.com
- Fixed redirection and unregistered actions
- Updated element selectors for current TikTok structure
- Human-like behavior simulation
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random
from pathlib import Path
from colorama import Fore, init, Style
import os
import re

# Initialize colorama
init()

class TikTokBot:
    def __init__(self):
        self.setup_driver()
        self.sent_count = 0
        self.like_count = 0
        self.comment_count = 0
        self.save_count = 0
        self.share_count = 0
        
        # Preset comments
        self.comments = [
            "🔥 This is amazing!",
            "😂 Can't stop laughing!",
            "👏 Great content!",
            "💯 So relatable!",
            "❤️ Love this!",
            "🙌 Perfect timing!",
            "😍 Absolutely stunning!",
            "🤩 Mind blown!",
            "👌 Quality content!",
            "🎯 Hit different!"
        ]
        
        # Updated TikTok XPaths for current structure
        self.xpaths = {
            # Cookie/popup handling
            "cookie_accept": [
                "//button[contains(text(), 'Accept all')]",
                "//button[contains(text(), 'Accept')]",
                "//button[@aria-label='Accept all cookies']"
            ],
            "cookie_decline": [
                "//button[contains(text(), 'Decline')]",
                "//button[contains(text(), 'Reject')]"
            ],
            "close_buttons": [
                "//button[@aria-label='Close']",
                "//div[@role='button' and @aria-label='Close']",
                "//button[contains(@class, 'close')]"
            ],
            
            # Video interaction buttons
            "like_button": [
                "//div[@data-e2e='like-icon']",  # Updated selector
                "//button[contains(@class, 'like-button')]", 
                "//div[contains(@class, 'DivLikeButton')]"
            ],
            
            "comment_button": [
                "//div[@data-e2e='comment-icon']", 
                "//button[contains(@class, 'comment-button')]"
            ],
            
            "save_button": [
                "//div[@data-e2e='bookmark-icon']",
                "//button[contains(@class, 'bookmark-button')]"
            ],
            
            "share_button": [
                "//div[@data-e2e='share-icon']",
                "//button[contains(@class, 'share-button')]"
            ],
            
            # Comment system
            "comment_input": [
                "//div[@contenteditable='true']",
                "//div[@role='textbox']"
            ],
            
            "comment_post": [
                "//div[@data-e2e='comment-post']",
                "//button[contains(text(), 'Post')]"
            ],
            
            # Share modal close
            "share_modal_close": [
                "//div[contains(@class, 'share-modal-close')]",
                "//button[@aria-label='Close']"
            ]
        }
        
    def setup_driver(self):
        """Initialize Chrome driver in desktop mode (no mobile emulation)."""
        options = uc.ChromeOptions()
        
        # ===   REMOVE MOBILE EMULATION   ===
        # Simply do not add any mobile emulation options here.
        
        # (Optional) If you want to force a desktop user-agent, you can add:
        desktop_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={desktop_user_agent}")
        
        # Stealth options remain the same
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = uc.Chrome(options=options)
        
        # Set window to a typical desktop resolution
        self.driver.set_window_size(1280, 800)
        
        # Execute stealth JavaScript
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def human_delay(self, min_delay=1, max_delay=3):
        """Random human-like delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def load_cookies(self, cookies_file="cookies.json"):
        """Load cookies from file"""
        cookies_path = Path(cookies_file)
        if not cookies_path.exists():
            print(f"{Fore.RED}[!] Cookie file not found: {cookies_file}")
            return False
            
        try:
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # Go to desktop TikTok first
            self.driver.get("https://www.tiktok.com/")
            self.human_delay(2, 4)
            
            # Add cookies
            added = 0
            for cookie in cookies:
                if 'tiktok.com' in cookie.get('domain', ''):
                    try:
                        # Prepare cookie dictionary
                        cookie_dict = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie['domain'],
                            'path': cookie.get('path', '/'),
                            'secure': cookie.get('secure', False),
                            'httpOnly': cookie.get('httpOnly', False)
                        }
                        if cookie.get('expiry'):
                            cookie_dict['expiry'] = int(cookie['expiry'])
                        
                        self.driver.add_cookie(cookie_dict)
                        added += 1
                    except Exception as e:
                        print(f"{Fore.YELLOW}[!] Failed to add cookie {cookie['name']}: {e}")
            
            print(f"{Fore.GREEN}[+] Added {added} cookies")
            
            # Refresh to apply cookies
            self.driver.refresh()
            self.human_delay(3, 5)
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to load cookies: {e}")
            return False
    
    def dismiss_popups(self):
        """Dismiss all popups and overlays"""
        popup_selectors = []
        popup_selectors.extend(self.xpaths["cookie_accept"])
        popup_selectors.extend(self.xpaths["cookie_decline"])
        popup_selectors.extend(self.xpaths["close_buttons"])
        
        for selector in popup_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        self.js_click(element, "Popup")
                        self.human_delay(0.5, 1.5)
                        break
            except Exception:
                continue
                
        # JavaScript popup removal
        try:
            self.driver.execute_script("""
                const popups = [
                    'div[data-role*="modal"]', 
                    'div[class*="overlay"]',
                    'div[class*="cookie"]',
                    'div[class*="popup"]'
                ];
                popups.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => el.remove());
                });
            """)
        except Exception:
            pass
    
    def js_click(self, element, action_name="Element"):
        """Click element using JavaScript for reliability"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            print(f"{Fore.GREEN}[+] {action_name} clicked")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to click {action_name}: {str(e)[:50]}")
            return False
    
    def find_and_click(self, xpath_list, action_name, required=False):
        """Find element from xpath list and click it"""
        for xpath in xpath_list:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                if self.js_click(element, action_name):
                    return True
            except TimeoutException:
                continue
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Error with xpath {xpath}: {str(e)[:50]}")
                continue
        
        if required:
            print(f"{Fore.RED}[!] Failed to find/click {action_name}")
        return False
    
    def is_video_playing(self):
        """Check if video is actually playing"""
        try:
            return self.driver.execute_script("""
                const video = document.querySelector('video');
                return video && video.readyState > 2 && video.currentTime > 0;
            """)
        except:
            return False
    
    def verify_on_correct_page(self, video_id):
        """Check if we're still on the correct video page"""
        current_url = self.driver.current_url
        return video_id in current_url
    
    def click_like_button(self):
        """Click like button with better element targeting"""
        try:
            like_button = self.driver.find_element(
                By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[1]"
            )
            self.driver.execute_script("arguments[0].click();", like_button)
            self.like_count += 1
            print(f"{Fore.GREEN}[+] Video liked! Total: {self.like_count}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Like failed: {str(e)[:100]}")
            return False
    
    def like_video(self):
        """Like the current video"""
        if self.click_like_button():
            self.human_delay(1, 2)
            return True
        return False
    
    def save_video(self):
        """Save/collect the current video"""
        if self.find_and_click(self.xpaths["save_button"], "Save Button"):
            self.save_count += 1
            print(f"{Fore.GREEN}[+] Video saved! Total: {self.save_count}")
            self.human_delay(1, 2)
            return True
        return False
    
    def share_video(self):
        """Share the current video and close modal"""
        if self.find_and_click(self.xpaths["share_button"], "Share Button"):
            self.share_count += 1
            print(f"{Fore.GREEN}[+] Share modal opened")
            
            # Close share modal
            self.human_delay(1, 2)
            self.find_and_click(self.xpaths["share_modal_close"], "Share Modal Close")
            print(f"{Fore.GREEN}[+] Share modal closed")
            self.human_delay(1, 2)
            return True
        return False
    
    def post_comment(self):
        """Post a random comment"""
        # Open comment section
        if not self.find_and_click(self.xpaths["comment_button"], "Comment Button"):
            return False
        
        self.human_delay(2, 3)
        
        # Find comment input
        comment_text = random.choice(self.comments)
        comment_posted = False
        
        for xpath in self.xpaths["comment_input"]:
            try:
                comment_input = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                
                # Clear and type comment
                self.driver.execute_script("arguments[0].innerText = '';", comment_input)
                
                # Type with human-like delays
                for char in comment_text:
                    comment_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_delay(0.5, 1)
                
                # Post comment
                if self.find_and_click(self.xpaths["comment_post"], "Post Comment"):
                    self.comment_count += 1
                    print(f"{Fore.GREEN}[+] Comment posted: '{comment_text}' | Total: {self.comment_count}")
                    comment_posted = True
                    break
                    
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Comment input error: {str(e)[:50]}")
                continue
        
        # Close comment section
        self.find_and_click(self.xpaths["close_buttons"], "Close Comments")
        self.human_delay(1, 2)
        return comment_posted
    
    def extract_video_id(self, url):
        """Extract video ID from TikTok URL"""
        pattern = r'/video/(\d+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    
    def process_video(self, video_url):
        """Process a single video with all actions"""
        print(f"\n{Fore.CYAN}[+] Processing video: {video_url}")
        
        try:
            # Extract video ID for verification
            video_id = self.extract_video_id(video_url)
            if not video_id:
                print(f"{Fore.RED}[!] Invalid TikTok URL: {video_url}")
                return False
                
            # Navigate to video (desktop site)
            self.driver.get(video_url)
            self.human_delay(3, 5)
            
            # Verify we're on the correct page
            if not self.verify_on_correct_page(video_id):
                print(f"{Fore.RED}[!] Redirected to wrong page")
                return False
            
            # Dismiss popups
            self.dismiss_popups()
            
            # Wait for video to load
            video_loaded = WebDriverWait(self.driver, 15).until(
                lambda d: self.is_video_playing()
            )
            
            if not video_loaded:
                print(f"{Fore.RED}[!] Video failed to load")
                return False
                
            print(f"{Fore.GREEN}[✓] Video loaded and playing")
            
            # Scroll down to ensure elements are visible
            self.driver.execute_script("window.scrollBy(0, 200);")
            self.human_delay(1, 2)
            
            success_count = 0
            
            # Like video
            if self.like_video():
                success_count += 1
            
            # Save video
            if self.save_video():
                success_count += 1
            
            # Post comment
            if self.post_comment():
                success_count += 1
            
            # Share video
            if self.share_video():
                success_count += 1
            
            print(f"{Fore.GREEN}[+] Video processed! Actions: {success_count}/4")
            return True
            
        except TimeoutException:
            print(f"{Fore.RED}[!] Timed out waiting for video to load")
            return False
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing video: {e}")
            return False
    
    def run_bot(self, video_urls, cookies_file="cookies.json"):
        """Main bot execution"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}TikTok Automation Bot (Desktop Mode) Started")
        print(f"{Fore.CYAN}{'='*60}")
        
        try:
            # Load cookies for login
            if self.load_cookies(cookies_file):
                print(f"{Fore.GREEN}[+] Logged in successfully!")
            else:
                print(f"{Fore.YELLOW}[!] Continuing without cookies (may require manual login)")
            
            # Process each video
            for i, url in enumerate(video_urls, 1):
                print(f"\n{Fore.YELLOW}[{i}/{len(video_urls)}] Processing video...")
                self.process_video(url)
                time.sleep(5)
                if i < len(video_urls):
                    delay = random.uniform(15, 25)
                    print(f"{Fore.CYAN}[+] Waiting {delay:.1f}s before next video...")
                    time.sleep(delay)
            
            # Final statistics
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}Bot execution completed!")
            print(f"{Fore.GREEN}Likes: {self.like_count}")
            print(f"{Fore.GREEN}Comments: {self.comment_count}")
            print(f"{Fore.GREEN}Saves: {self.save_count}")
            print(f"{Fore.GREEN}Shares: {self.share_count}")
            print(f"{Fore.CYAN}{'='*60}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Bot stopped by user")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Fatal error: {e}")
        finally:
            self.driver.quit()

def main():
    """Main function with CLI interface"""
    print(f"""{Fore.BLUE}
 ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ████████╗
 ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
    ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██████╔╝██║   ██║   ██║   
    ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
    ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██████╔╝╚██████╔╝   ██║   
    ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
    {Style.RESET_ALL}""")
    
    print(f"{Fore.GREEN}[+] TikTok Automation Bot v3.0 (Desktop-Only)")
    print(f"{Fore.YELLOW}[!] Make sure you have cookies.json file in the same directory")
    print(f"{Fore.CYAN}[+] This bot will like, comment, save, and share TikTok videos on the desktop site")
    print()
    
    # Get video URLs
    video_urls = []
    print(f"{Fore.CYAN}[+] Enter TikTok video URLs (one per line, empty line to finish):")
    
    while True:
        url = input(f"{Fore.WHITE}URL: ").strip()
        if not url:
            break
        if "tiktok.com" in url and "/video/" in url:
            video_urls.append(url)
            print(f"{Fore.GREEN}[✓] Added: {url}")
        else:
            print(f"{Fore.RED}[!] Invalid TikTok video URL. Must contain '/video/'")
    
    if not video_urls:
        print(f"{Fore.RED}[!] No valid URLs provided")
        return
    
    # Initialize and run bot
    bot = TikTokBot()
    bot.run_bot(video_urls)

if __name__ == "__main__":
    main()
