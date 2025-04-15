## Tweet Scraper

A simple Python-based Twitter scraper that uses Playwright to scrape tweets along with media URLs from any public Twitter profile, and outputs the data in JSON format.
---

## Setup Instructions

### 1. **Clone the repository**
```bash
git clone https://github.com/yourusername/tweet_scraper.git
cd tweet_scraper
```

### 2. Install Dependencies
Install all required packages using:
Ensure Python 3.12 is installed on your machine.

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project directory with the following structure:

```
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
```

### 4. Run the Scraper
Start the scraping tool by running:

```bash
python usage04.py
```

---

## Features

- **Login with Twitter credentials**
- **Gradio UI for easy interaction**
- **Select tweet range from 10 to 500**
- **Live streaming of scraping progress**
- **Tweets exported in JSON format**
- **Headless browser automation**

---

## Usage

- After launching the script, a Gradio UI will appear in your browser.
- Choose the number of tweets you want to scrape (between 10 to 500).
- A headless browser will open automatically.
- **Do not minimize or interact with the browser** while it is running.
- Once scraping completes, you can **download the tweets in JSON format** directly from the Gradio interface.

---

## Troubleshooting

- **Login fails:** Double-check your `.env` credentials.
- **UI doesn't open:** Ensure you’re using Python 3.12 and all dependencies are installed.
- **Browser closes unexpectedly:** Don’t minimize the browser window during scraping.

---

## Future Improvements (Planned)
- Increase range of tweets 
- Improve UI

---

### Output Format

Each tweet is stored like this:

```python
{
  'text': 'Tweet content here...',
  'media': ['https://image-url.com/image1.jpg', 'https://image-url.com/image2.jpg']
}
```

### Disclaimer

- This scraper is intended for **educational and research purposes**.
- Use responsibly and always respect Twitter's [Terms of Service](https://twitter.com/en/tos).

---
