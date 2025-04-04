# tweet_scraper.py
from playwright.sync_api import sync_playwright
import time

class TweetScraper:
    def __init__(self, username):
        self.username = username
        self.tweets = []

    def scrape(self, max_scrolls=3):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = f'https://twitter.com/{self.username}'
            page.goto(url)
            print(f"Scraping tweets from: {url}")

            # Scroll down multiple times to load tweets
            for _ in range(max_scrolls):
                page.mouse.wheel(0, 3000)
                time.sleep(2)

            tweet_elements = page.query_selector_all('article')

            for tweet in tweet_elements:
                try:
                    content = tweet.inner_text()
                    images = tweet.query_selector_all('img')
                    media_urls = [img.get_attribute('src') for img in images if 'profile_images' not in img.get_attribute('src')]
                    
                    self.tweets.append({
                        'text': content,
                        'media': media_urls
                    })
                except Exception as e:
                    print("Skipping a tweet due to error:", e)

            browser.close()

    def get_tweets(self):
        return self.tweets
