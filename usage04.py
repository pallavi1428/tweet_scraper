from twee04 import TweetScraper
import gradio as gr
import time
import os
import random
from datetime import datetime
from typing import Generator, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

def estimate_duration(num_tweets: int) -> str:
    """Calculate realistic time estimate"""
    base_time = max(30, num_tweets * 1.5)  # Base 1.5 seconds per tweet
    variance = num_tweets * 0.7  # Add some variability
    est_seconds = base_time + random.uniform(-variance, variance)
    
    if est_seconds < 60:
        return f"{int(est_seconds)} seconds"
    else:
        return f"{int(est_seconds//60)} minutes {int(est_seconds%60)} seconds"

def scrape_tweets(
    username: str, 
    num_tweets: int, 
    use_auth: bool
) -> Generator[Tuple[str, Optional[str]], None, None]:
    """Careful scraping process with live updates"""
    start_time = time.time()
    username = username.strip().replace('@', '').strip()
    
    # Validation
    if not username:
        yield "❌ Please enter a valid username (without @)", None
        return
    
    try:
        num_tweets = min(int(num_tweets), 2000)
        if num_tweets < 10:
            yield "❌ Minimum 10 tweets required", None
            return
    except ValueError:
        yield "❌ Please enter a valid number between 10-2000", None
        return
    
    # Initialization
    est_duration = estimate_duration(num_tweets)
    status = (
        f"🧭 Starting careful scrape of {num_tweets} tweets from @{username}\n"
        f"⏳ Estimated time: ~{est_duration}\n"
        f"🔐 Mode: {'Authenticated' if use_auth else 'Public'}\n"
        "🐢 Working at human-like pace..."
    )
    yield status, None
    
    scraper = None
    try:
        scraper = TweetScraper(username, auth=use_auth)
        
        # Authentication phase
        if use_auth:
            auth_status = (
                "🔐 Beginning authentication...\n"
                "👉 Please observe the browser window\n"
                "⏱️ This may take 20-40 seconds"
            )
            yield auth_status, None
            time.sleep(2)  # Let user read message
        
        # Scraping with live updates
        last_update = time.time()
        collected = 0
        
        def scraping_task():
            nonlocal collected
            try:
                result = scraper.scrape(num_tweets=num_tweets)
                collected = len(result) if result else 0
            except Exception as e:
                print(f"Scraping error: {str(e)}")
        
        # Start thread
        import threading
        thread = threading.Thread(target=scraping_task)
        thread.start()
        
        # Progress monitoring
        while thread.is_alive():
            current_count = len(scraper.tweets) if scraper else 0
            if current_count > collected:
                collected = current_count
                elapsed = time.time() - start_time
                progress = (
                    f"⏳ Collected {collected}/{num_tweets} tweets\n"
                    f"📈 Progress: {collected/max(1,num_tweets):.1%}\n"
                    f"⏱️ Elapsed: {elapsed:.1f}s\n"
                    "👉 Keep browser window visible"
                )
                yield progress, None
            
            # Heartbeat every 10 seconds
            if time.time() - last_update > 10:
                last_update = time.time()
                if collected > 0:
                    speed = collected / max(1, elapsed)
                    yield (
                        f"💓 Still working... ({speed:.1f} tweets/sec)\n"
                        f"🐢 Current count: {collected}/{num_tweets}", 
                        None
                    )
            
            time.sleep(0.5)
        
        # Final processing
        if not scraper or not scraper.tweets:
            yield "❌ No tweets collected. Account may be private or rate-limited", None
            return
        
        # Save results
        filename = scraper.save_to_json()
        elapsed = time.time() - start_time
        
        # Build output
        output = [
            f"✅ Successfully collected {collected} tweets",
            f"⏱️ Time taken: {elapsed:.1f} seconds",
            f"📊 Average speed: {collected/max(1,elapsed):.1f} tweets/sec",
            f"💾 Saved to: {os.path.basename(filename)}",
            "\nSample tweets:"
        ]
        
        # Add sample tweets
        for idx, tweet in enumerate(scraper.tweets[:3]):
            text = (tweet['text'][:70] + '...') if len(tweet['text']) > 70 else tweet['text']
            media = f" [📷{len(tweet['media'])}]" if tweet['media'] else ""
            date = datetime.fromisoformat(tweet['timestamp']).strftime('%b %d') if tweet.get('timestamp') else ""
            output.append(f"\n{idx+1}. {text}{media} {date}")
        
        output.append("\n⚠️ Note: Use this data responsibly")
        yield "\n".join(output), filename
    
    except Exception as e:
        error_msg = str(e)
        if "Timeout" in error_msg:
            error_msg += "\n\n💡 Try reducing the number of tweets"
        elif "rate limit" in error_msg.lower():
            error_msg += "\n\n⏳ Twitter may have temporarily limited you"
        yield f"❌ Error: {error_msg}", None
    finally:
        if scraper:
            del scraper

def create_ui():
    """Create clean Gradio interface"""
    with gr.Blocks(
        title="Careful Twitter Scraper", 
        theme=gr.themes.Soft(),
        css="""
        .status-box {font-family: monospace}
        .download-box {border: 1px dashed #ccc}
        """
    ) as ui:
        gr.Markdown("""
        # 🐢 Careful Twitter/X Scraper  
        ### Scrapes at human-like pace to avoid detection
        
        **Important:**  
        • For best results, keep browser window visible  
        • First run requires manual login if using auth  
        • Don't interact with browser during scraping  
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                inputs = gr.Column()
                inputs.username = gr.Textbox(
                    label="Username (without @)",
                    placeholder="elonmusk",
                    max_lines=1
                )
                inputs.num_tweets = gr.Slider(
                    label="Number of Tweets",
                    minimum=10,
                    maximum=500,
                    value=100,
                    step=10,
                    info="10-500 recommended"
                )
                inputs.auth = gr.Checkbox(
                    label="Use Authentication",
                    value=True,
                    info="Required for >100 tweets"
                )
                inputs.submit = gr.Button(
                    "Begin Scraping", 
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
                **Recommendations:**  
                • 10-100 tweets: Standard speed  
                • 100-300 tweets: Slower pace  
                • 300+ tweets: Very slow with auth  
                """)
            
            with gr.Column(scale=2):
                outputs = gr.Column()
                outputs.status = gr.Textbox(
                    label="Scraping Status",
                    interactive=False,
                    lines=10,
                    autoscroll=True,
                    elem_classes=["status-box"]
                )
                outputs.download = gr.File(
                    label="Download Results",
                    file_types=[".json"],
                    elem_classes=["download-box"]
                )
        
        inputs.submit.click(
            fn=scrape_tweets,
            inputs=[inputs.username, inputs.num_tweets, inputs.auth],
            outputs=[outputs.status, outputs.download]
        )
    
    return ui

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("Starting Careful Twitter Scraper...")
    
    interface = create_ui()
    interface.launch(
        server_name="localhost",
        server_port=7860,
        share=False,
        inbrowser=True,
        favicon_path="🐢"
    )