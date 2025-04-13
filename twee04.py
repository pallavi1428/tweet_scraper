from playwright.sync_api import sync_playwright
import time
import json
import os
import random
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class TweetScraper:
    def __init__(self, username: str, auth: bool = False):
        self.username = username
        self.tweets: List[Dict] = []
        self.auth = auth
        self.cookie_file = "twitter_auth.json"
        self.timeout = 180000  # 3 minute timeout
        self.max_retries = 3
        self.scroll_attempt_limit = 200
        self.start_time = None

    def _human_delay(self, action_type="base", base=1.0):
        """Natural delays with different behaviors"""
        if action_type == "typing":
            delay = base * random.uniform(0.08, 0.3)
            if random.random() < 0.1:  # Occasional hesitation
                delay += random.uniform(0.5, 1.2)
        elif action_type == "navigation":
            delay = base * random.uniform(0.5, 1.8)
        elif action_type == "reading":
            delay = base * random.uniform(0.8, 3.0)
        else:
            delay = base * random.uniform(0.3, 1.2)
        time.sleep(delay)

    def _human_type(self, element, text):
        """Realistic typing with occasional mistakes"""
        for i, char in enumerate(text):
            element.type(char)
            self._human_delay("typing", random.uniform(0.05, 0.2))
            if random.random() < 0.03:  # 3% chance of typo
                element.press("Backspace")
                self._human_delay("typing", 0.3)
                element.type(char)

    def _is_end_of_feed(self, page):
        """Check if we've reached the end of available tweets"""
        return page.evaluate('''() => {
            const nearBottom = window.innerHeight + window.pageYOffset >= 
                             document.body.scrollHeight - 1000;
            const lastTweet = document.querySelector('article:last-child');
            const noNewTweets = lastTweet && 
                              lastTweet.getBoundingClientRect().top < window.innerHeight;
            return nearBottom && noNewTweets;
        }''')

    def _gentle_scroll(self, page):
        """Natural scrolling that stays on the feed"""
        scroll_dist = random.randint(600, 1000)  # About 1 screen height
        scroll_duration = random.uniform(0.7, 1.5)
        
        # Occasionally scroll up slightly first
        if random.random() < 0.3:
            page.mouse.wheel(0, -random.randint(200, 400))
            self._human_delay("navigation", 0.5)
        
        # Main scroll down
        page.mouse.wheel(0, scroll_dist)
        self._human_delay("navigation", scroll_duration)
        
        # Micro-movements (like human hand tremor)
        if random.random() < 0.4:
            page.mouse.wheel(
                random.randint(-30, 30),
                random.randint(-30, 30)
            )
            self._human_delay("navigation", 0.1)

    def _extract_tweet_data(self, tweet):
        """Carefully extract data from a tweet"""
        try:
            # Simulate reading the tweet
            self._human_delay("reading", random.uniform(0.5, 2.0))
            
            tweet_id = tweet.get_attribute('aria-labelledby') or tweet.get_attribute('id')
            text_element = tweet.query_selector('div[data-testid="tweetText"]') or tweet.query_selector('div[lang]')
            text = text_element.inner_text() if text_element else ""
            
            # Get media if present
            media_urls = []
            for img in tweet.query_selector_all('img[alt="Image"], img[alt="Embedded video"]'):
                if src := img.get_attribute('src'):
                    if 'profile_images' not in src and 'emoji' not in src:
                        media_urls.append(src)
            
            # Get timestamp
            time_element = tweet.query_selector('time')
            timestamp = time_element.get_attribute('datetime') if time_element else ""
            
            return {
                'id': tweet_id,
                'text': text,
                'media': media_urls,
                'timestamp': timestamp,
                'collected_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Error extracting tweet: {str(e)}")
            return None

    def _human_scroll(self, page, target_tweets):
        """Main scrolling logic that stays focused"""
        scroll_attempts = 0
        last_count = 0
        
        while len(self.tweets) < target_tweets and scroll_attempts < self.scroll_attempt_limit:
            # Gentle scrolling
            self._gentle_scroll(page)
            
            # Extract visible tweets
            tweet_elements = page.query_selector_all('article')
            new_tweets = 0
            
            for tweet in tweet_elements:
                if len(self.tweets) >= target_tweets:
                    break
                    
                tweet_data = self._extract_tweet_data(tweet)
                if tweet_data and not any(t['id'] == tweet_data['id'] for t in self.tweets):
                    self.tweets.append(tweet_data)
                    new_tweets += 1
            
            # Progress tracking
            scroll_attempts += 1
            if new_tweets > 0:
                last_count = len(self.tweets)
                print(f"📊 Collected {len(self.tweets)}/{target_tweets} tweets")
            else:
                print(f"🔍 No new tweets found (attempt {scroll_attempts})")
                
                # Check if we've reached the end
                if self._is_end_of_feed(page):
                    print("✅ Reached end of feed")
                    break
            
            # Take occasional breaks
            if scroll_attempts % 15 == 0:
                pause = random.uniform(3.0, 8.0)
                print(f"💤 Taking a {pause:.1f}s break...")
                self._human_delay("reading", pause)

    def _login(self, page):
        """Login handling that mimics human behavior"""
        try:
            page.goto("https://x.com/login", timeout=self.timeout)
            self._human_delay("navigation", random.uniform(1.5, 3))
            
            # Username
            username_field = page.wait_for_selector('input[autocomplete="username"]', timeout=30000)  
            self._human_type(username_field, os.getenv('TWITTER_USER'))  
            self._human_delay("navigation", random.uniform(1, 2)) 
            
            # Click next
            next_button = page.query_selector('div[role="button"]:has-text("Next")')  
            if next_button:  
                next_button.click(delay=random.randint(200, 400))  
            else:
                username_field.press("Enter")
            self._human_delay("navigation", random.uniform(1.5, 3))  
            
            # Password
            password_field = page.wait_for_selector('input[autocomplete="current-password"]', timeout=30000)
            self._human_type(password_field, os.getenv('TWITTER_PASS'))  
            self._human_delay("navigation", random.uniform(0.5, 1.5)) 
            
            # Login
            login_button = page.query_selector('div[role="button"]:has-text("Log in")') or \
                       page.query_selector('span:has-text("Log in")') or \
                       page.query_selector('div[data-testid="LoginForm_Login_Button"]')
        
            if login_button:
                login_button.scroll_into_view_if_needed()
                login_button.click(delay=random.randint(300, 800))
            else:
                # Reliable fallback
                password_field.press("Enter")
            
            # Verify login
            page.wait_for_selector('nav[aria-label="Primary"]', timeout=30000)
            self._human_delay("navigation", random.uniform(2, 4))  
            return True
            
        except Exception as e:
            print(f"⚠️ Login failed: {str(e)}")
            return False

    def scrape(self, num_tweets=40):
        """Main scraping method"""
        self.start_time = time.time()
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--start-maximized"],
                timeout=self.timeout,
                slow_mo=100  # Adds slight delay between actions
            )
            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            try:
                page = context.new_page()
                
                # Authentication
                if self.auth and not self._login(page):
                    raise Exception("Login failed")
                
                # Go to profile
                page.goto(f'https://x.com/{self.username}', timeout=self.timeout)
                self._human_delay("navigation", 3)
                
                # Wait for tweets to load
                try:
                    page.wait_for_selector('article', timeout=30000)
                except:
                    print("⚠️ No tweets found initially - proceeding anyway")
                
                # Adjust for large scrapes
                if num_tweets > 100:
                    self.scroll_attempt_limit = 250
                    print(f"🔧 Adjusting for large scrape ({num_tweets} tweets)")
                
                # Main scraping
                self._human_scroll(page, num_tweets)
                
                return self.tweets[:num_tweets]
                
            except Exception as e:
                raise Exception(f"Scraping failed: {str(e)}")
            finally:
                try:
                    context.close()
                    browser.close()
                except:
                    pass

    def save_to_json(self, filename=None):
        """Save results with metadata"""
        if not filename:
            filename = f"tweets_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'metadata': {
                'username': self.username,
                'count': len(self.tweets),
                'collected_at': datetime.now().isoformat()
            },
            'tweets': self.tweets
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename