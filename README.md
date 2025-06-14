# TikTok Automation Bot

A sophisticated TikTok automation tool that allows you to automate interactions with TikTok videos such as liking, commenting, sharing, and saving videos.

## Features

- **Video Interaction**: Like, comment, share and save TikTok videos
- **Cookie-Based Authentication**: Uses stored cookies for persistent login
- **Proxy Support**: Rotate through proxies to avoid rate limiting
- **Anti-Bot Bypass**: Handles TikTok's anti-bot protection including captchas
- **Graphical Interface**: Easy to use interface to control bot operations
- **Human-Like Behavior**: Random delays and actions to mimic human activity
- **Customizable Comments**: Configure your own comments templates

## Setup Instructions

### Requirements

- Python 3.7 or higher
- Chrome browser installed

### Installation

1. Clone or download this repository to your local machine

2. Install required packages:
```
pip install seleniumbase faker requests
```

3. Configure your settings in the bot controller interface or edit the config section in `test.py`

### Cookie Setup

To use this bot, you need valid TikTok authentication cookies:

1. Launch the bot controller
2. Go to the "Settings" tab
3. Click on "Extract New Cookies"
4. Log in to TikTok manually in the opened browser
5. The cookies will be automatically extracted once you're logged in

Alternatively, you can export cookies from Chrome using a cookie extension and fix their format using the "Fix Cookie Format" button.

### Proxy Setup

1. In the "Proxies" tab, add your proxies in the format: `IP,PORT,USERNAME,PASSWORD` (one proxy per line)
2. You can test your proxies using the "Test Proxies" button

### Usage

1. Launch the bot controller:
```
python bot_controller.py
```

2. Add TikTok video URLs (one per line) in the main tab
   - You can load URLs from a file using the "Load URLs from File" button

3. Configure settings in the Settings tab:
   - Set delay times between actions
   - Choose which actions to perform (like, comment, share, save)

4. Add custom comment templates in the Comments tab
   - One comment per line
   - The bot will randomly select from these comments

5. Click "Start Bot" to begin processing

## Troubleshooting

### Captcha Issues

If the bot consistently fails to solve captchas:
- Check your proxy quality
- Try different proxies
- Make sure your cookies are fresh and valid
- Consider slowing down the delay times

### Login Problems

If login verification fails:
- Ensure your cookie file is up-to-date and properly formatted
- Try extracting new cookies using the "Extract New Cookies" button
- Check TikTok's website for any changes to their authentication system

### Video Controls Not Visible

If the bot can't interact with videos:
- Check the `video_controls_debug.png` screenshot to see what's happening
- TikTok may have updated their UI - adjust the XPath selectors in `test.py`

## Advanced Configuration

Advanced users can modify the following files:
- `test.py` - Core bot functionality and selectors
- `bot_controller.py` - GUI interface and settings management

## Disclaimer

This tool is for educational purposes only. Use responsibly and in compliance with TikTok's terms of service. The authors are not responsible for any misuse or violations.
#   T i k t o k - a u t o b o t  
 #   T i k t o k - a u t o b o t  
 