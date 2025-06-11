#!/usr/bin/env python3
"""
TikTok Automation Bot – v4.1
=====================================================================
✔ Pauses the video via JS                 (pause_video)
✔ Likes / saves / comments in original order
✔ Likes N top-level comments via exact XPaths (like_sequential_comments)
✔ Re-checks that the main “like” persists, re-likes if TikTok un-hearts
✔ Asks user “How many comments should I like per video?”
=====================================================================
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
import sys
from pathlib import Path
from colorama import Fore, init, Style

# Initialize colorama
init()


class TikTokBot:
    def __init__(self, comments_to_like: int = 0):
        # -------- browser / counters --------
        self.setup_driver()
        self.sent_count = 0
        self.like_count = 0
        self.comment_count = 0
        self.save_count = 0
        self.share_count = 0
        self.comments_to_like = comments_to_like   # NEW

        # -------- preset comment pool --------
        self.comments = [
            "This is amazing!", "Can't stop laughing!", "Great content!",
            "So relatable!", "Love this!", "Perfect timing!",
            "Absolutely stunning!", "Mind blown!", "Quality content!",
            "Hit different!", "Pure magic!", "Fire content!",
            "So inspiring!", "Brilliant!", "King/Queen energy!"
        ]

        # -------- XPaths (identical to your v4.0) --------
        self.xpaths = {
            # Main action container
            "action_container": "//div[@class='css-1npmxy5-DivActionItemContainer er2ywmz0']",

            # Individual action buttons
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

    # ------------------------------------------------------------------ #
    # ---------------------  INITIALISE CHROME  ------------------------ #
    # ------------------------------------------------------------------ #
    def setup_driver(self):
        options = uc.ChromeOptions()

        desktop_ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36")
        options.add_argument(f"--user-agent={desktop_ua}")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')

        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            }
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = uc.Chrome(options=options)
        self.driver.set_window_size(1280, 800)

        # Extra stealth
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins',  {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages',{get: () => ['en-US','en']});
            window.chrome = { runtime: {} };
        """)

    # ------------------------------------------------------------------ #
    # ---------------------  UTILITY HELPERS  -------------------------- #
    # ------------------------------------------------------------------ #
    def human_delay(self, lo=1, hi=3):
        time.sleep(random.uniform(lo, hi))

    def click_element_multiple_ways(self, element, tag="Element"):
        """Try JS click, normal click, ActionChains, key presses …"""
        methods = [
            ("JS Click",          lambda: self.driver.execute_script("arguments[0].click();", element)),
            ("Direct Click",      element.click),
            ("ActionChains",      lambda: ActionChains(self.driver).move_to_element(element).click().perform()),
            ("Offset Click",      lambda: ActionChains(self.driver).move_to_element_with_offset(element, 0, 0).click().perform()),
            ("ENTER key",         lambda: element.send_keys(Keys.ENTER)),
            ("SPACE key",         lambda: element.send_keys(Keys.SPACE)),
            ("JS dispatch",       lambda: self.driver.execute_script(
                                        "arguments[0].dispatchEvent(new MouseEvent('click',{bubbles:true}))", element))
        ]
        for name, fn in methods:
            try:
                fn()
                print(f"{Fore.GREEN}[+] {tag} clicked via {name}")
                return True
            except Exception:
                continue
        print(f"{Fore.RED}[!] All click strategies failed for {tag}")
        return False

    def find_and_click_element(self, xpaths, tag, timeout=10):
        for xp in xpaths:
            try:
                print(f"{Fore.CYAN}[+] Trying xpath: {xp[:60]}…")
                el = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xp)))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
                self.human_delay(0.4, 0.8)
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
                if self.click_element_multiple_ways(el, tag):
                    return True
            except TimeoutException:
                continue
        print(f"{Fore.RED}[!] Could not click {tag}")
        return False

    # ------------------------------------------------------------------ #
    # -----------------------  PAUSE VIDEO (NEW)  ---------------------- #
    # ------------------------------------------------------------------ #
    def pause_video(self):
        try:
            self.driver.execute_script("""
                const v=document.querySelector('video');
                if(v && !v.paused){v.pause();}
            """)
            print(f"{Fore.GREEN}[+] Video paused")
        except Exception as e:
            print(f"{Fore.YELLOW}[!] pause_video failed: {e}")

    # ------------------------------------------------------------------ #
    # -----------------------  POPUP DISMISSAL  ------------------------ #
    # ------------------------------------------------------------------ #
    def dismiss_popups(self):
        # known accept / close buttons
        for xp in self.xpaths["cookie_accept"] + self.xpaths["close_buttons"]:
            try:
                for el in self.driver.find_elements(By.XPATH, xp):
                    if el.is_displayed() and el.is_enabled():
                        self.click_element_multiple_ways(el, "Popup")
                        self.human_delay(0.3, 0.8)
            except Exception:
                pass
        # brute force hide
        self.driver.execute_script("""
            const killers=[
              'div[role="dialog"]','div[class*="modal"]','div[class*="overlay"]',
              'div[class*="popup"]','div[class*="cookie"]','[class*="Banner"]'];
            killers.forEach(sel=>{
              document.querySelectorAll(sel).forEach(el=>{el.style.display='none';});
            });
        """)

    # ------------------------------------------------------------------ #
    # ---------------------  LOAD COOKIES (unchanged)  ----------------- #
    # ------------------------------------------------------------------ #
    def load_cookies(self, cookies_file="cookies.json"):
        p = Path(cookies_file)
        if not p.exists():
            print(f"{Fore.RED}[!] Cookie file not found")
            return False
        try:
            with open(p, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            self.driver.get("https://www.tiktok.com/")
            self.human_delay(3, 5)
            added = 0
            for c in cookies:
                if "tiktok.com" in c.get("domain", ""):
                    cookie_dict = {
                        'name': c['name'], 'value': c['value'],
                        'domain': c['domain'].lstrip('.'),
                        'path': c.get('path', '/'),
                        'secure': c.get('secure', False),
                        'httpOnly': c.get('httpOnly', False)
                    }
                    if c.get("expirationDate"):
                        cookie_dict['expiry'] = int(c['expirationDate'])
                    try:
                        self.driver.add_cookie(cookie_dict)
                        added += 1
                    except Exception:
                        pass
            print(f"{Fore.GREEN}[+] Added {added} cookies")
            self.driver.refresh()
            self.human_delay(3, 5)
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to load cookies: {e}")
            return False

    # ------------------------------------------------------------------ #
    # ------------------  VIDEO-LIKE STATE CHECK  ---------------------- #
    # ------------------------------------------------------------------ #
    def is_video_liked(self):
        for xp in self.xpaths["like_button"]:
            try:
                el = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, xp)))
                if "active" in el.get_attribute("class").lower():
                    return True
                if "rgb(255, 0, 0)" in el.value_of_css_property("color"):
                    return True
                if el.get_attribute("aria-pressed") == "true":
                    return True
            except Exception:
                pass
        return False

    # ------------------------------------------------------------------ #
    # ------------------  LIKE-PERSISTENCE (NEW)  ---------------------- #
    # ------------------------------------------------------------------ #
    def enforce_like_persistence(self, attempts=2):
        self.driver.execute_script("window.scrollTo(0,0)")
        time.sleep(1.2)
        for _ in range(attempts):
            if self.is_video_liked():
                print(f"{Fore.GREEN}[✓] Like persisted")
                return True
            print(f"{Fore.YELLOW}[!] Like dropped – re-liking")
            if not self.like_video():
                return False
            time.sleep(1.2)
        return self.is_video_liked()

    # ------------------------------------------------------------------ #
    # ------------------  LIKE VIDEO (unchanged)  ---------------------- #
    # ------------------------------------------------------------------ #
    def like_video(self):
        print(f"{Fore.CYAN}[+] Checking like status …")
        if self.is_video_liked():
            print(f"{Fore.GREEN}[✓] Already liked")
            return True
        print(f"{Fore.CYAN}[+] Liking video …")
        if self.find_and_click_element(self.xpaths["like_button"], "Like Button"):
            time.sleep(1.5)
            if self.is_video_liked():
                self.like_count += 1
                print(f"{Fore.GREEN}[+] Video liked (total {self.like_count})")
                return True
            print(f"{Fore.RED}[!] Like verification failed")
        return False

    # ------------------------------------------------------------------ #
    # ------------------  SAVE VIDEO (unchanged)  ---------------------- #
    # ------------------------------------------------------------------ #
    def save_video(self):
        print(f"{Fore.CYAN}[+] Saving video …")
        if self.find_and_click_element(self.xpaths["save_button"], "Save Button"):
            self.save_count += 1
            print(f"{Fore.GREEN}[+] Video saved (total {self.save_count})")
            self.human_delay(1, 2)
            return True
        return False

    # ------------------------------------------------------------------ #
    # ------------------  OPEN COMMENTS (unchanged)  ------------------- #
    # ------------------------------------------------------------------ #
    def open_comments(self):
        print(f"{Fore.CYAN}[+] Opening comments …")
        if self.find_and_click_element(self.xpaths["comment_button"], "Comment Button"):
            self.human_delay(2, 3)
            return True
        return False

    # ------------------------------------------------------------------ #
    # ------------------  POST COMMENT (unchanged)  -------------------- #
    # ------------------------------------------------------------------ #
    def post_comment(self):
        comment_txt = random.choice(self.comments)
        print(f"{Fore.CYAN}[+] Posting comment: {comment_txt}")

        # click input container
        for xp in self.xpaths["comment_input_container"]:
            try:
                cont = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xp)))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", cont)
                self.human_delay(0.4, 0.8)
                if self.click_element_multiple_ways(cont, "Comment Input Container"):
                    break
            except Exception:
                continue
        else:
            print(f"{Fore.RED}[!] Could not click input container")
            return False

        # type comment
        for xp in self.xpaths["comment_input_field"]:
            try:
                fld = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xp)))
                fld.clear()
                for ch in comment_txt:
                    fld.send_keys(ch)
                    time.sleep(random.uniform(0.05, 0.15))
                print(f"{Fore.GREEN}[+] Text entered")
                break
            except Exception:
                continue
        else:
            print(f"{Fore.RED}[!] Could not type comment")
            return False

        self.human_delay(0.8, 1.5)
        if self.find_and_click_element(self.xpaths["comment_post_button"], "Post Button"):
            self.comment_count += 1
            print(f"{Fore.GREEN}[+] Comment posted (total {self.comment_count})")
            self.human_delay(2, 3)
            return True
        return False

    # ------------------------------------------------------------------ #
    # -----------  LIKE TOP-LEVEL COMMENTS (NEW)  ---------------------- #
    # ------------------------------------------------------------------ #
    def like_sequential_comments(self, max_idx: int):
        """
        Like comment 1 … max_idx using absolute XPath pattern you supplied.
        Stops if a like button is not found for a given index.
        """
        if max_idx <= 0:
            return False

        liked = 0
        base = ("/html/body/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[2]/"
                "div[2]/div[{i}]/div[1]/div[2]/div[2]/div[2]")

        for i in range(1, max_idx + 1):
            xp = base.format(i=i)
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xp)))
                if self.click_element_multiple_ways(btn, f"Comment Like #{i}"):
                    liked += 1
                time.sleep(random.uniform(0.4, 0.8))
            except TimeoutException:
                print(f"{Fore.YELLOW}[!] Comment {i} like button not found – stopping")
                break

        if liked:
            print(f"{Fore.GREEN}[+] Liked {liked} comment(s)")
        else:
            print(f"{Fore.YELLOW}[!] No comments liked")
        return liked > 0

    # ------------------------------------------------------------------ #
    # ------------------  PAGE-LOAD / CONTAINER CHECK  ----------------- #
    # ------------------------------------------------------------------ #
    def wait_for_page_load(self):
        try:
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete")
            self.human_delay(2, 4)
            return True
        except TimeoutException:
            print(f"{Fore.YELLOW}[!] Page load timeout")
            return False

    def verify_action_container(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, self.xpaths["action_container"])))
            print(f"{Fore.GREEN}[+] Action container present")
            return True
        except TimeoutException:
            print(f"{Fore.RED}[!] Action container missing")
            return False

    # ------------------------------------------------------------------ #
    # ------------------  HANDLE A SINGLE VIDEO  ----------------------- #
    # ------------------------------------------------------------------ #
    def process_video(self, url):
        print(f"\n{Fore.CYAN}{'='*60}\n[+] Processing {url}\n{'='*60}")

        try:
            self.driver.get(url)

            if not self.wait_for_page_load():
                return False

            self.pause_video()        # NEW
            self.dismiss_popups()
            if not self.verify_action_container():
                return False

            success = 0

            # 1) save 2) like 3) open comments 4) comment
            if self.save_video():
                success += 1
            if self.like_video():
                success += 1
            if self.open_comments():
                success += 1
                if self.post_comment():
                    success += 1
                self.like_sequential_comments(self.comments_to_like)

            # verify like still on
            if not self.enforce_like_persistence():
                print(f"{Fore.RED}[!] Like persistence failed")
            else:
                print(f"{Fore.GREEN}[✓] Like verified")

            print(f"{Fore.GREEN}[+] Actions succeeded {success}/4")
            return success >= 3

        except Exception as e:
            print(f"{Fore.RED}[!] Error processing video: {e}")
            return False

    # ------------------------------------------------------------------ #
    # ------------------  MAIN BOT LOOP (unchanged)  ------------------- #
    # ------------------------------------------------------------------ #
    def run_bot(self, video_urls, cookies_file="cookies.json"):
        print(f"{Fore.BLUE}{'='*60}")
        print(f"{Fore.BLUE}TikTok Automation Bot v4.1 – started")
        print(f"{Fore.BLUE}{'='*60}")

        if self.load_cookies(cookies_file):
            print(f"{Fore.GREEN}[+] Logged in via cookies")
        else:
            print(f"{Fore.YELLOW}[!] Running without cookies")

        successes = 0
        for idx, url in enumerate(video_urls, 1):
            print(f"{Fore.YELLOW}[{idx}/{len(video_urls)}] Video …")
            if self.process_video(url):
                successes += 1
            if idx < len(video_urls):
                delay = random.uniform(20, 30)
                print(f"{Fore.CYAN}[+] Waiting {delay:.1f}s before next video …")
                time.sleep(delay)

        print(f"\n{Fore.BLUE}{'='*60}")
        print(f"{Fore.GREEN}Completed!  {successes}/{len(video_urls)} videos successful")
        print(f"{Fore.GREEN}Likes: {self.like_count}  Comments: {self.comment_count}  Saves: {self.save_count}")
        print(f"{Fore.BLUE}{'='*60}")
        print(f"{Fore.CYAN}[+] Closing browser …")
        self.driver.quit()


# ====================================================================== #
#                                CLI                                     #
# ====================================================================== #
def main():
    banner = f"""{Fore.BLUE}
 ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ██████╗  ██████╗ ████████╗
 ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
    ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██████╔╝██║   ██║   ██║   
    ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██╔══██╗██║   ██║   ██║   
    ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██████╔╝╚██████╔╝   ██║   
    ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
{Style.RESET_ALL}"""
    print(banner)
    print(f"{Fore.GREEN}[+] TikTok Automation Bot v4.1 – Like ▸ Save ▸ Comment ▸ Verify ▸ Like comments")

    # collect URLs
    video_urls = []
    print(f"{Fore.CYAN}[+] Enter TikTok video URLs (empty line to finish):")
    while True:
        url = input(Fore.WHITE + "URL: ").strip()
        if not url:
            break
        if "tiktok.com" in url and "/video/" in url:
            video_urls.append(url)
            print(f"{Fore.GREEN}[✓] Added")
        else:
            print(f"{Fore.RED}[!] Must contain '/video/'")

    if not video_urls:
        sys.exit(f"{Fore.RED}No valid URLs – exiting.")

    # number of comments to like
    while True:
        try:
            n = int(input(f"{Fore.CYAN}[+] How many top-level comments to like per video? (0=none) → "))
            if n >= 0:
                break
        except ValueError:
            pass
        print(f"{Fore.RED}[!] Enter a non-negative integer")

    input(Fore.YELLOW + "Press Enter to start …")

    bot = TikTokBot(comments_to_like=n)
    bot.run_bot(video_urls)


if __name__ == "__main__":
    main()
