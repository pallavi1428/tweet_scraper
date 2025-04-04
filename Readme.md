## Tweet Scraper

A simple Python-based Twitter scraper that uses playwright to collect tweets and media (images) from any public Twitter profile.

---

### Features

- Scrape tweet **text** and **media (image URLs)** from a public profile  
- Scrolls the page to load more tweets automatically  
- Easy to use and extend  
- Fully headless browser automation

---

### Requirements

- Python 3.7+
- [Playwright](https://playwright.dev/python/)

---

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/tweet_scraper.git
cd tweet_scraper
```

2. **Install dependencies**
```bash
pip install playwright
playwright install
```

---

### How It Works

The scraper launches a **headless Chromium browser**, navigates to the specified Twitter profile, scrolls the page multiple times to load tweets, and extracts:
- The **text** of each tweet
- The **image URLs** (excluding profile pics)

All the data is stored in a Python list of dictionaries for easy access and further processing.

---

### 📝 Usage

Create a Python script (like `usage.py`):

```python
from tweet_scraper import TweetScraper

scraper = TweetScraper("elonmusk")
scraper.scrape(max_scrolls=5)

for idx, tweet in enumerate(scraper.get_tweets()):
    print(f"\nTweet {idx+1}")
    print("Text:", tweet['text'][:100], "...")
    print("Media:", tweet['media'])
```

---

### Output Format

Each tweet is stored like this:

```python
{
  'text': 'Tweet content here...',
  'media': ['https://image-url.com/image1.jpg', 'https://image-url.com/image2.jpg']
}
```

---

### Project Structure

```
tweet_scraper/
│
├── tweet_scraper.py      # The main scraping logic
├── usage.py              # Example usage script
└── README.md             # You are here
```

---

### Tips

- Increase `max_scrolls` to scrape more tweets.
- You can customize the `TweetScraper` to extract other content like likes, retweets, or timestamps.

---

### Disclaimer

- This scraper is intended for **educational and research purposes**.
- Use responsibly and always respect Twitter's [Terms of Service](https://twitter.com/en/tos).

---
