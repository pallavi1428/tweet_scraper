from tweet_scraper import TweetScraper

scraper = TweetScraper("PrajwalTomar_")
scraper.scrape(max_scrolls=5)

for idx, tweet in enumerate(scraper.get_tweets()):
    print(f"\nTweet {idx+1}")
    print("Text:", tweet['text'][:800], "...")
    print("Media:", tweet['media'])
