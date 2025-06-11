#!/usr/bin/env python3
"""
TikTok Automation Bot - Updated with Exact XPaths
=================================================
Updated to use the exact TikTok selectors and structure provided.
Uses specific paths for like, save, comment, and post buttons.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
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
            "This is amazing!",
            "Can't stop laughing!",
            "Great content!",
            "So relatable!",
            "Love this!",
            "Perfect timing!",
            "Absolutely stunning!",
            "Mind blown!",
            "Quality content!",
            "Hit different!",
            "Pure magic!",
            "Fire content!",
            "So inspiring!",
            "Brilliant!",
            "King/Queen energy!"
        ]
        
        # Updated TikTok XPaths based on exact structure provided
        self.xpaths = {
            # Main action container
            "action_container": "//div[@class='css-1npmxy5-DivActionItemContainer er2ywmz0']",
            
            # Individual action buttons (in order: like, comment, save, share)
            "like_button": [
                "//*[@id='main-content-video_detail']/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[1]",
                "//button[@class='css-rninf8-ButtonActionItem edu4zum0'][1]",
                "//span[@data-e2e='like-icon']/parent::button",
                "//div[@class='css-1npmxy5-DivActionItemContainer er2ywmz0']/button[1]"
            ],
            
            "save_button": [
                "//*[@id='main-content-video_detail']/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/div/button",
                "//div[@aria-expanded='false'][@aria-haspopup='dialog']/button",
                "//span[@data-e2e='undefined-icon']/parent::button",
                "//use[@xlink:href='#uncollect-7652bb5c']/parent::*/parent::*/parent::button"
            ],
            
            "comment_button": [
                "//*[@id='main-content-video_detail']/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[2]",
                "//span[@data-e2e='comment-icon']/parent::button",
                "//div[@class='css-1npmxy5-DivActionItemContainer er2ywmz0']/button[2]"
            ],
            
            "share_button": [
                "//*[@id='main-content-video_detail']/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[3]",
                "//span[@data-e2e='share-icon']/parent::button",
                "//use[@xlink:href='#pc-share-078b3fae']/parent::*/parent::*/parent::button"
            ],
            
            # Comment system
            "comment_input_container": [
                "//*[@id='main-content-video_detail']/div/div[2]/div[1]/div[2]/div[1]/div/div/div[1]/div",
                "//div[@data-e2e='comment-input']",
                "//div[@class='css-1yh5t6t-DivInputAreaContainer e1rzzhjk2']"
            ],
            
            "comment_input_field": [
                "//div[@data-e2e='comment-input']//div[@contenteditable='true']",
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[@class='css-1yh5t6t-DivInputAreaContainer e1rzzhjk2']//div[@contenteditable='true']"
            ],
            
            "comment_post_button": [
                "//*[@id='main-content-video_detail']/div/div[2]/div[1]/div[2]/div[1]/div/div/div[2]",
                "//div[@data-e2e='comment-post']",
                "//div[@class='css-wnoky3-DivPostButton e1rzzhjk6']",
                "//div[@aria-label='Post'][@role='button']"
            ],
            
            # Popup handling
            "cookie_accept": [
                "//button[contains(text(), 'Accept all')]",
                "//button[contains(text(), 'Accept')]",
                "//button[@aria-label='Accept all cookies']"
            ],
            "close_buttons": [
                "//button[@aria-label='Close']",
                "//div[@role='button' and @aria-label='Close']",
                "//button[contains(@class, 'close')]"
            ]
        }
        
    def is_video_liked(self):
        """Check if video is already liked by examining button state"""
        for xpath in self.xpaths["like_button"]:
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                # Check for active state indicators:
                # 1. Check for active class in button
                if "active" in element.get_attribute("class").lower():
                    return True
                    
                # 2. Check for filled heart icon (red color)
                if "rgb(255, 0, 0)" in element.value_of_css_property("color"):
                    return True
                    
                # 3. Check aria-pressed attribute
                if element.get_attribute("aria-pressed") == "true":
                    return True
                    
            except Exception:
                continue
        return False
    def setup_driver(self):
        """Initialize Chrome driver in desktop mode with enhanced stealth"""
        options = uc.ChromeOptions()

        # Desktop user agent
        desktop_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={desktop_user_agent}")

        # Enhanced stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')

        # ⚠️ REMOVE problematic experimental options
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)

        # Set prefs
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            }
        }
        options.add_experimental_option("prefs", prefs)

        # Launch the driver
        self.driver = uc.Chrome(options=options)
        self.driver.set_window_size(1280, 800)

        # Enhanced stealth patch
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}};
        """)


    def human_delay(self, min_delay=1, max_delay=3):
        """Random human-like delay with variance"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def load_cookies(self, cookies_file="cookies.json"):
        """Load cookies from file with enhanced error handling"""
        cookies_path = Path(cookies_file)
        if not cookies_path.exists():
            print(f"{Fore.RED}[!] Cookie file not found: {cookies_file}")
            return False
            
        try:
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # Navigate to TikTok first
            print(f"{Fore.CYAN}[+] Loading TikTok homepage...")
            self.driver.get("https://www.tiktok.com/")
            self.human_delay(3, 5)
            
            # Add cookies
            added = 0
            for cookie in cookies:
                if 'tiktok.com' in cookie.get('domain', ''):
                    try:
                        cookie_dict = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie['domain'].lstrip('.'),
                            'path': cookie.get('path', '/'),
                            'secure': cookie.get('secure', False),
                            'httpOnly': cookie.get('httpOnly', False)
                        }
                        if cookie.get('expirationDate'):
                            cookie_dict['expiry'] = int(cookie['expirationDate'])
                        
                        self.driver.add_cookie(cookie_dict)
                        added += 1
                    except Exception as e:
                        continue
            
            print(f"{Fore.GREEN}[+] Added {added} cookies")
            
            # Refresh to apply cookies
            self.driver.refresh()
            self.human_delay(3, 5)
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to load cookies: {e}")
            return False
    
    def dismiss_popups(self):
        """Dismiss all popups and overlays with multiple strategies"""
        # Strategy 1: Click known popup buttons
        popup_selectors = self.xpaths["cookie_accept"] + self.xpaths["close_buttons"]
        
        for selector in popup_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        self.click_element_multiple_ways(element, "Popup")
                        self.human_delay(0.5, 1.5)
                        break
            except Exception:
                continue
        
        # Strategy 2: JavaScript removal of common overlays
        try:
            self.driver.execute_script("""
                // Remove common overlay selectors
                const overlaySelectors = [
                    'div[role="dialog"]',
                    'div[class*="modal"]',
                    'div[class*="overlay"]',
                    'div[class*="popup"]',
                    'div[class*="cookie"]',
                    '[class*="Banner"]'
                ];
                
                overlaySelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        if (el.style) {
                            el.style.display = 'none';
                            el.remove();
                        }
                    });
                });
                
                // Remove fixed position elements that might be overlays
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.position === 'fixed' && 
                        (style.zIndex > 1000 || el.textContent.toLowerCase().includes('cookie'))) {
                        el.style.display = 'none';
                    }
                });
            """)
        except Exception:
            pass
    
    def click_element_multiple_ways(self, element, action_name="Element"):
        """Try multiple methods to click an element with enhanced reliability"""
        methods = [
            ("JavaScript Click", lambda: self.driver.execute_script("arguments[0].click();", element)),
            ("Direct Click", lambda: element.click()),
            ("ActionChains Move+Click", lambda: ActionChains(self.driver).move_to_element(element).click().perform()),
            ("ActionChains Offset Click", lambda: ActionChains(self.driver).move_to_element_with_offset(element, 0, 0).click().perform()),
            ("Send Enter Key", lambda: element.send_keys(Keys.ENTER)),
            ("Send Space Key", lambda: element.send_keys(Keys.SPACE)),
            ("Force JS Click", lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", element))
        ]
        
        for method_name, method in methods:
            try:
                method()
                print(f"{Fore.GREEN}[+] {action_name} clicked using {method_name}")
                return True
            except Exception as e:
                print(f"{Fore.YELLOW}[!] {method_name} failed for {action_name}: {str(e)[:50]}")
                continue
        
        print(f"{Fore.RED}[!] All click methods failed for {action_name}")
        return False
    
    def find_and_click_element(self, xpath_list, action_name, timeout=10):
        """Find element from xpath list and click using multiple methods"""
        for xpath in xpath_list:
            try:
                print(f"{Fore.CYAN}[+] Trying xpath: {xpath[:60]}...")
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self.human_delay(0.5, 1)
                
                # Wait for element to be clickable
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                
                if self.click_element_multiple_ways(element, action_name):
                    return True
                    
            except TimeoutException:
                print(f"{Fore.YELLOW}[!] Timeout waiting for {action_name} with xpath: {xpath[:60]}")
                continue
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Error with {action_name} xpath {xpath[:60]}: {str(e)[:50]}")
                continue
        
        print(f"{Fore.RED}[!] Failed to find/click {action_name} with all xpaths")
        return False
    
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        try:
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.human_delay(2, 4)
            return True
        except TimeoutException:
            print(f"{Fore.YELLOW}[!] Page load timeout")
            return False
    
    def verify_action_container(self):
        """Verify the main action container is present"""
        try:
            container = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, self.xpaths["action_container"]))
            )
            print(f"{Fore.GREEN}[+] Action container found")
            return True
        except TimeoutException:
            print(f"{Fore.RED}[!] Action container not found")
            return False
    
    def like_video(self):
        """Click like button only if video isn't already liked"""
        print(f"{Fore.CYAN}[+] Checking video like status...")
        
        if self.is_video_liked():
            print(f"{Fore.GREEN}[✓] Video already liked - skipping")
            return True  # Considered successful since desired state exists

        print(f"{Fore.CYAN}[+] Attempting to like video...")
        
        if self.find_and_click_element(self.xpaths["like_button"], "Like Button"):
            # Verify like succeeded
            time.sleep(1.5)
            if self.is_video_liked():
                self.like_count += 1
                print(f"{Fore.GREEN}[+] Video liked! Total likes: {self.like_count}")
                return True
            else:
                print(f"{Fore.RED}[!] Like action failed verification")
        return False
    
    def save_video(self):
        """Click the save/collect button (button inside div)"""
        print(f"{Fore.CYAN}[+] Attempting to save video...")
        
        if self.find_and_click_element(self.xpaths["save_button"], "Save Button"):
            self.save_count += 1
            print(f"{Fore.GREEN}[+] Video saved! Total saves: {self.save_count}")
            self.human_delay(1, 2)
            return True
        return False
    
    def open_comments(self):
        """Click the comment button (second button in action container)"""
        print(f"{Fore.CYAN}[+] Opening comments section...")
        
        if self.find_and_click_element(self.xpaths["comment_button"], "Comment Button"):
            print(f"{Fore.GREEN}[+] Comments section opened")
            self.human_delay(2, 3)  # Wait for comments to load
            return True
        return False
    
    def post_comment(self):
        """Post a random comment"""
        print(f"{Fore.CYAN}[+] Attempting to post comment...")
        
        # Select random comment
        comment_text = random.choice(self.comments)
        print(f"{Fore.CYAN}[+] Selected comment: '{comment_text}'")
        
        # Find and click comment input container
        input_clicked = False
        for xpath in self.xpaths["comment_input_container"]:
            try:
                input_container = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                
                # Scroll into view and click
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_container)
                self.human_delay(0.5, 1)
                
                if self.click_element_multiple_ways(input_container, "Comment Input Container"):
                    input_clicked = True
                    break
                    
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Failed to click comment container: {str(e)[:50]}")
                continue
        
        if not input_clicked:
            print(f"{Fore.RED}[!] Could not click comment input container")
            return False
        
        self.human_delay(1, 2)
        
        # Find the actual input field and type comment
        comment_typed = False
        for xpath in self.xpaths["comment_input_field"]:
            try:
                input_field = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                
                # Clear any existing text
                input_field.clear()
                
                # Type comment character by character (human-like)
                for char in comment_text:
                    input_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                comment_typed = True
                print(f"{Fore.GREEN}[+] Comment typed successfully")
                break
                
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Failed to type in comment field: {str(e)[:50]}")
                continue
        
        if not comment_typed:
            print(f"{Fore.RED}[!] Could not type comment")
            return False
        
        self.human_delay(1, 2)
        
        # Click post button
        if self.find_and_click_element(self.xpaths["comment_post_button"], "Post Button"):
            self.comment_count += 1
            print(f"{Fore.GREEN}[+] Comment posted: '{comment_text}' | Total comments: {self.comment_count}")
            self.human_delay(2, 3)
            return True
        
        return False
    
    def like_existing_comments(self, max_likes=3):
        """Like existing comments in the comment section"""
        print(f"{Fore.CYAN}[+] Looking for existing comments to like...")
        
        try:
            # Find comment like buttons
            like_buttons = self.driver.find_elements(
                By.XPATH, 
                "//div[@data-e2e='comment-item']//button[contains(@class, 'like') or @data-e2e='like-icon']"
            )
            
            liked_count = 0
            for i, button in enumerate(like_buttons[:max_likes]):
                try:
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    self.human_delay(0.5, 1)
                    
                    if self.click_element_multiple_ways(button, f"Comment Like {i+1}"):
                        liked_count += 1
                        self.human_delay(0.5, 1.5)
                    
                except Exception as e:
                    print(f"{Fore.YELLOW}[!] Failed to like comment {i+1}: {str(e)[:50]}")
                    continue
            
            if liked_count > 0:
                print(f"{Fore.GREEN}[+] Liked {liked_count} existing comments")
            else:
                print(f"{Fore.YELLOW}[!] No comments liked")
            
            return liked_count > 0
            
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Error liking existing comments: {e}")
            return False
    
    def process_video(self, video_url):
        """Process a single video with all actions in correct order"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}[+] Processing video: {video_url}")
        print(f"{Fore.CYAN}{'='*60}")
        
        try:
            # Navigate to video
            print(f"{Fore.CYAN}[+] Navigating to video...")
            self.driver.get(video_url)
            
            # Wait for page to load
            if not self.wait_for_page_load():
                print(f"{Fore.RED}[!] Page failed to load properly")
                return False
            
            # Dismiss popups
            print(f"{Fore.CYAN}[+] Dismissing popups...")
            self.dismiss_popups()
            
            # Verify action container is present
            if not self.verify_action_container():
                print(f"{Fore.RED}[!] Action container not found - video may not have loaded")
                return False
            
            success_count = 0
            
            # Step 1: Like the video
            
            # Step 2: Save the video  
            if self.save_video():
                success_count += 1
            
            if self.like_video():
                success_count += 1
            # Step 3: Open comments section
            if self.open_comments():
                success_count += 1
                
                # Step 4: Post a comment
                if self.post_comment():
                    success_count += 1
                
                # Step 5: Like existing comments
                # self.like_existing_comments()
            
            print(f"\n{Fore.GREEN}[+] Video processing completed!")
            print(f"{Fore.GREEN}[+] Successful actions: {success_count}/4")
            print(f"{Fore.CYAN}{'='*60}")
            
            return success_count >= 3  # Consider successful if at least 3/4 actions worked
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing video: {e}")
            return False
    
    def run_bot(self, video_urls, cookies_file="cookies.json"):
        """Main bot execution with enhanced error handling"""
        print(f"{Fore.BLUE}{'='*60}")
        print(f"{Fore.BLUE}TikTok Automation Bot v4.0 - Started")
        print(f"{Fore.BLUE}Using exact TikTok XPaths and structure")
        print(f"{Fore.BLUE}{'='*60}")
        
        try:
            # Load cookies for login
            if self.load_cookies(cookies_file):
                print(f"{Fore.GREEN}[+] Logged in successfully!")
            else:
                print(f"{Fore.YELLOW}[!] Continuing without cookies")
            
            successful_videos = 0
            
            # Process each video
            for i, url in enumerate(video_urls, 1):
                print(f"\n{Fore.YELLOW}[{i}/{len(video_urls)}] Starting video {i}...")
                
                if self.process_video(url):
                    successful_videos += 1
                    print(f"{Fore.GREEN}[+] Video {i} processed successfully!")
                else:
                    print(f"{Fore.RED}[!] Video {i} processing failed!")
                
                # Wait between videos (except for last one)
                if i < len(video_urls):
                    delay = random.uniform(20, 30)
                    print(f"{Fore.CYAN}[+] Waiting {delay:.1f}s before next video...")
                    time.sleep(delay)
            
            # Final statistics
            print(f"\n{Fore.BLUE}{'='*60}")
            print(f"{Fore.GREEN}Bot execution completed!")
            # print(f"{Fore.GREEN}Videos processed: {successful_videos}/{len(video_urls)}")
            # print(f"{Fore.GREEN}Total Likes: {self.like_count}")
            # print(f"{Fore.GREEN}Total Comments: {self.comment_count}")
            # print(f"{Fore.GREEN}Total Saves: {self.save_count}")
            # print(f"{Fore.GREEN}Total Shares: {self.share_count}")
            print(f"{Fore.BLUE}{'='*60}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Bot stopped by user (Ctrl+C)")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Fatal error: {e}")
        finally:
            print(f"{Fore.CYAN}[+] Closing browser...")
            self.driver.quit()

def main():
    """Main function with enhanced CLI interface"""
    print(f"""{Fore.BLUE}
 ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ████████╗
 ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
    ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██████╔╝██║   ██║   ██║   
    ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
    ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██████╔╝╚██████╔╝   ██║   
    ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
    {Style.RESET_ALL}""")
    
    print(f"{Fore.GREEN}[+] TikTok Automation Bot v4.0 - Enhanced with Exact XPaths")
    print(f"{Fore.YELLOW}[!] Make sure you have cookies.json file in the same directory")
    print(f"{Fore.CYAN}[+] This bot will: Like → Save → Comment → Post on TikTok videos")
    print(f"{Fore.CYAN}[+] Using exact TikTok structure and selectors")
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
        input("Press Enter to exit...")
        return
    
    print(f"\n{Fore.CYAN}[+] Ready to process {len(video_urls)} video(s)")
    input(f"{Fore.YELLOW}Press Enter to start the bot...")
    
    # Initialize and run bot
    bot = TikTokBot()
    bot.run_bot(video_urls)
    
    input(f"\n{Fore.CYAN}Press Enter to exit...")

if __name__ == "__main__":
    main()