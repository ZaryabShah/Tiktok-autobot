#!/usr/bin/env python3
# improved_functions.py - Helper functions for TikTok bot captcha solving and error handling

import random
import time
import requests
from seleniumbase import SB
from selenium.webdriver.common.by import By

def solve_modern_slider_captcha(sb: SB) -> bool:
    """Solve the modern TikTok slider captcha with circular puzzle as shown in the screenshots"""
    print("🧩 Attempting to solve modern slider captcha (circular puzzle)...")
    
    # Take screenshot for debugging
    try:
        sb.save_screenshot("modern_slider_captcha.png")
        print("📷 Saved modern slider captcha screenshot")
    except Exception as e:
        print(f"⚠️ Could not save screenshot: {e}")
    
    # Wait to ensure everything is loaded
    time.sleep(random.uniform(3, 5))
    
    # First check if we can use the API to solve this captcha
    try:
        print("🔍 Looking for captcha images for API-based solution...")
        # Try to find the specific captcha images using the provided XPath
        specific_selector1 = "//*[@id='captcha-verify-container-main-page']/div[2]/div[1]/img[1]"
        specific_selector2 = "//*[@id='captcha-verify-container-main-page']/div[2]/div[1]/img[2]"
        
        img1 = None
        img2 = None
        
        if sb.is_element_visible(specific_selector1):
            img1 = sb.get_attribute(specific_selector1, "src")
            print(f"✅ Found first captcha image: {img1[:30]}...")
            
            # Try to find the second image
            if sb.is_element_visible(specific_selector2):
                img2 = sb.get_attribute(specific_selector2, "src")
                print(f"✅ Found second captcha image: {img2[:30]}...")
            else:
                # Try to find nearby images
                img2 = sb.execute_script("""
                    const img1 = document.evaluate(arguments[0], document, null, 
                              XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (!img1 || !img1.parentElement) return null;
                    
                    // Get the parent and search for other images
                    const parent = img1.parentElement;
                    const images = parent.querySelectorAll('img');
                    for (let img of images) {
                        if (img !== img1 && img.src) {
                            return img.src;
                        }
                    }
                    return null;
                """, specific_selector1)
                
            if img1 and img2:
                print("✅ Found both captcha images - attempting API solution")
                
                # Prepare API call
                payload = {
                    "cap_type": "whirl",
                    "url1": img1,
                    "url2": img2
                }
                headers = {
                    "x-rapidapi-key": "95a48de2c0msh428436f5f09baebp191df7jsn5192af7e037f",
                    "x-rapidapi-host": "tiktok-captcha-solver2.p.rapidapi.com",
                    "Content-Type": "application/json"
                }
                
                try:
                    response = requests.post(
                        "https://tiktok-captcha-solver2.p.rapidapi.com/tiktok/captcha",
                        json=payload,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ API response: {result}")
                        
                        if "angle" in result:
                            angle = result["angle"]
                            print(f"✅ Solved captcha with API - angle: {angle}°")
                            
                            # Apply the rotation
                            sb.execute_script(f"""
                                const captchaImage = document.querySelector('.captcha_verify_img, [class*="cap-h-"] img');
                                if (captchaImage) {{
                                    captchaImage.style.transform = 'rotate({angle}deg)';
                                    console.log('Applied rotation: {angle} degrees');
                                }}
                            """)
                            
                            time.sleep(random.uniform(2, 3))
                            
                            # Click the verify button
                            submit_clicked = sb.execute_script("""
                                const verifyButtons = [
                                    document.querySelector('button.verify'),
                                    document.querySelector('.captcha_verify_submit'),
                                    document.querySelector('[class*="verify"]'),
                                    document.querySelector('button:contains("Submit")'),
                                    document.querySelector('button:contains("Verify")')
                                ];
                                
                                const btn = verifyButtons.find(b => b);
                                if (btn) {
                                    btn.click();
                                    return true;
                                }
                                return false;
                            """)
                            
                            if submit_clicked:
                                print("✅ Clicked verify button after API solution")
                                time.sleep(random.uniform(5, 7))
                                return True
                except Exception as e:
                    print(f"⚠️ API call failed: {e}")
                    # Fall through to slider method
    except Exception as e:
        print(f"⚠️ Error trying API solution: {e}")
        
    print("🔄 Falling back to slider method...")
    
    # Try to find the slider arrow button with multiple approaches
    try:
        # Use JavaScript to find and interact with the slider
        slider_info = sb.execute_script("""
            // Try to find the slider arrow
            const sliders = [
                document.querySelector('button.arrow'),
                document.querySelector('.secsdk-captcha-drag-icon'),
                document.querySelector('[class*="slider-thumb"]'),
                document.querySelector('[class*="drag"]'),
                // Additional selectors based on screenshots
                document.querySelector('div.cap-flex img + img'),  // Second image in the flex container
                document.querySelector('img[style*="clip-path: circle(50%)"]'),
                document.querySelector('button[class*="arrow"]')
            ];
            
            const slider = sliders.find(s => s && s.offsetParent !== null);
            if (!slider) return { found: false };
            
            // Get the track/container
            const trackParent = slider.parentElement;
            let track = trackParent;
            
            // Try to find appropriate container if this isn't it
            if (!trackParent || trackParent.clientWidth < 100) {
                const possibleTracks = [
                    document.querySelector('[class*="slider-track"]'),
                    document.querySelector('[class*="drag-area"]'),
                    document.querySelector('[class*="cap-flex"]')
                ];
                track = possibleTracks.find(t => t) || trackParent;
            }
            
            return {
                found: true,
                sliderElement: slider.tagName,
                trackWidth: track ? track.clientWidth : 0,
                containerWidth: document.querySelector('.cap-flex') ? 
                               document.querySelector('.cap-flex').clientWidth : 0
            };
        """)
        
        if slider_info and slider_info.get('found'):
            print(f"✅ Found slider element: {slider_info.get('sliderElement')}")
            print(f"📏 Track width: {slider_info.get('trackWidth')}px")
            
            # Calculate the distance to slide based on the container width
            track_width = slider_info.get('trackWidth') or slider_info.get('containerWidth') or 280
            distance = int(track_width * 0.95)  # Slide almost to the end
            print(f"🔄 Planning to slide {distance}px")
            
            # First attempt with executeScript for more reliable interaction
            sb.execute_script("""
                // Helper function for smoother sliding with delays
                function smoothSlide(element, distance) {
                    const trackRect = element.parentElement.getBoundingClientRect();
                    const startX = trackRect.left + 10;
                    const startY = trackRect.top + (trackRect.height / 2);
                    
                    // Create and dispatch mousedown event
                    element.dispatchEvent(new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: startX,
                        clientY: startY
                    }));
                    
                    // Small delay before moving
                    setTimeout(() => {
                        // Create move events with increasing distance
                        const steps = 10;
                        const stepSize = distance / steps;
                        
                        for (let i = 1; i <= steps; i++) {
                            const moveX = startX + (stepSize * i);
                            setTimeout(() => {
                                element.dispatchEvent(new MouseEvent('mousemove', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window,
                                    clientX: moveX,
                                    clientY: startY
                                }));
                                
                                // On the last step, do mouseup
                                if (i === steps) {
                                    setTimeout(() => {
                                        element.dispatchEvent(new MouseEvent('mouseup', {
                                            bubbles: true,
                                            cancelable: true,
                                            view: window,
                                            clientX: moveX,
                                            clientY: startY
                                        }));
                                    }, 50);
                                }
                            }, i * 30); // Gradually increasing delay
                        }
                    }, 100);
                }
                
                // Find the slider again
                const sliders = [
                    document.querySelector('button.arrow'),
                    document.querySelector('.secsdk-captcha-drag-icon'),
                    document.querySelector('[class*="slider-thumb"]'),
                    document.querySelector('[class*="drag"]'),
                    document.querySelector('div.cap-flex img + img')
                ];
                
                const slider = sliders.find(s => s);
                if (!slider) return false;
                
                // Start the smooth sliding
                smoothSlide(slider, arguments[0]);
                return true;
            """, distance)
            
            print("✅ Executed JavaScript slider movement")
            time.sleep(random.uniform(3, 5))  # Wait for animation to complete
            
            # Take a screenshot to verify the result
            try:
                sb.save_screenshot("after_slider_captcha.png")
            except Exception:
                pass
            
            # Check if captcha is still present after our attempt
            captcha_still_present = sb.execute_script("""
                return !!(
                    document.querySelector('[class*="captcha"]') ||
                    document.querySelector('div:contains("Drag the slider")') ||
                    document.querySelector('button.arrow') ||
                    document.querySelector('[class*="slider-thumb"]')
                );
            """)
            
            if captcha_still_present:
                print("⚠️ Captcha still appears to be present, trying again")
                # Try one more time with a different approach
                try:
                    print("🔄 Making second attempt with pure JavaScript")
                    sb.execute_script("""
                        // Try to find any element that looks like a slider
                        const sliders = Array.from(document.querySelectorAll('button, div, img'))
                            .filter(el => {
                                const style = window.getComputedStyle(el);
                                const rect = el.getBoundingClientRect();
                                
                                // Look for small, visible interactive elements
                                return el.offsetParent !== null && 
                                      rect.width < 100 && 
                                      rect.height < 100 &&
                                      (
                                          (el.tagName === 'BUTTON') ||
                                          (style.cursor === 'pointer') ||
                                          (el.tagName === 'IMG' && style.clipPath && style.clipPath.includes('circle'))
                                      );
                            });
                        
                        if (!sliders.length) return false;
                        
                        // Find the best candidate slider
                        const slider = sliders[0];
                        const rect = slider.getBoundingClientRect();
                        
                        // Simulate a sequence of events for the drag
                        const events = [
                            new MouseEvent('mousedown', { bubbles: true, clientX: rect.left + 5, clientY: rect.top + 5 }),
                        ];
                        
                        // Create a series of mouse moves
                        const moves = 10;
                        const distance = window.innerWidth * 0.7; // Move most of the way across screen
                        
                        for (let i = 1; i <= moves; i++) {
                            const x = rect.left + 5 + (distance * (i / moves));
                            events.push(
                                new MouseEvent('mousemove', { bubbles: true, clientX: x, clientY: rect.top + 5 })
                            );
                        }
                        
                        // Add mouseup at the end
                        events.push(
                            new MouseEvent('mouseup', { 
                                bubbles: true, 
                                clientX: rect.left + 5 + distance, 
                                clientY: rect.top + 5 
                            })
                        );
                        
                        // Dispatch all events in sequence
                        events.forEach(event => {
                            slider.dispatchEvent(event);
                        });
                        
                        return true;
                    """)
                    print("✅ Executed pure JavaScript slider movement")
                    time.sleep(random.uniform(4, 6))
                except Exception:
                    pass
            
            # Success!
            return True
            
    except Exception as e:
        print(f"❌ Error during modern slider captcha solving: {e}")
        return False

def handle_notifications_safely(sb: SB):
    """Handle notifications and popups while avoiding 'Invalid selector type' errors"""
    print("🔍 Checking for popups and notifications safely...")
    
    # First check for simple notification dialogs with direct selectors
    notification_simple_selectors = [
        "//button[text()='Allow']",
        "//button[text()='Allow all']",
        "//button[text()='Accept']",
        "//button[text()='Not now']"
    ]
    
    # Process each selector individually to avoid list-related errors
    for selector in notification_simple_selectors:
        try:
            # Explicitly check for visibility with a single selector
            if sb.is_element_visible(selector):
                print(f"📢 Found simple notification button: {selector}")
                sb.click(selector)
                print("✅ Clicked notification button")
                time.sleep(random.uniform(1, 2))
                break
        except Exception as e:
            print(f"⚠️ Error checking selector {selector}: {e}")
            continue
    
    # Use JavaScript as fallback for popup dismissal
    try:
        sb.execute_script("""
            // Common popup and notification button text
            const buttonTexts = ['allow', 'accept', 'continue', 'ok', 'got it', 'dismiss'];
            
            // Find and click buttons with these texts
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {
                const text = (btn.textContent || '').toLowerCase();
                if (buttonTexts.some(t => text.includes(t)) && btn.offsetParent !== null) {
                    console.log('Clicking button with text: ' + text);
                    btn.click();
                    return true;
                }
            }
            return false;
        """)
    except Exception as e:
        print(f"⚠️ JavaScript popup handling error: {e}")
    
    # Handle notification allow/deny dialogs which sometimes appear
    print("🔔 Checking for notification permission dialogs...")
    try:
        # Process notification selectors one by one to avoid list issues
        notification_selectors = [
            "//button[contains(text(), 'Allow')]",
            "//button[contains(text(), 'Allow all')]",
            "//button[@aria-label='Allow']",
            "//div[contains(text(), 'notification')]//button"
        ]
        
        for selector in notification_selectors:
            try:
                if sb.is_element_visible(selector):
                    print(f"🔔 Found notification dialog with selector: {selector}")
                    sb.click(selector)
                    print("✅ Clicked notification allow button")
                    time.sleep(random.uniform(2, 3))
                    break
            except Exception as click_err:
                print(f"⚠️ Failed to click notification selector {selector}: {click_err}")
                continue
        
        # Fallback to JavaScript for more complex notification dialogs
        sb.execute_script("""
            // Try to find and click notification allow buttons
            const notificationTexts = ['allow', 'notifications', 'permission'];
            
            // Look for buttons containing notification-related text
            const buttons = Array.from(document.querySelectorAll('button'));
            const allowBtn = buttons.find(btn => {
                const text = (btn.textContent || '').toLowerCase();
                return notificationTexts.some(keyword => text.includes(keyword)) && 
                      !text.includes('not now') && !text.includes('later');
            });
            
            if (allowBtn) {
                console.log('Found notification dialog via JS, clicking Allow');
                allowBtn.click();
                return true;
            }
            
            // Look for notification dialog and click the primary button
            const dialog = document.querySelector('[role="dialog"]');
            if (dialog && dialog.innerText.toLowerCase().includes('notification')) {
                const dialogBtn = dialog.querySelector('button');
                if (dialogBtn) {
                    dialogBtn.click();
                    return true;
                }
            }
            
            return false;
        """)
    except Exception as e:
        print(f"⚠️ Error handling notification dialog: {e}")
