import os
import re

import praw
from dotenv import load_dotenv
# from playwright.sync_api import sync_playwright

from website_srape import general_video_scraper, imgur_video_scrape, download_youtube_video, imgur_video_save

# Load variables from .env file into environment
load_dotenv()

REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CILENT_SECRET = os.environ.get("REDDIT_CILENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

def main():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CILENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=False)
    #     context = browser.new_context(
    #         user_agent="A common browser user agent",
    #         accept_downloads=True,
    #         viewport={'width': 1280, 'height': 800},
    #         extra_http_headers={
    #             'Accept-Language': 'en-US,en;q=0.9',
    #             # Any other headers that a normal browser would send
    #         }
    #     )
    #     page = context.new_page()
    #     # page = browser.new_page()
    # browser.close()
    
    submission = reddit.submission(url="https://www.reddit.com/r/xxfitness/comments/119edqq/squat_form_check/")
    post_title = submission.title
    post_text = submission.selftext
    
    print('post_title: ', post_title)
    print('post_text: ', post_text)
    
    match = re.search(r'https?://imgur\.com[a-zA-Z0-9/]*', post_text)
    if match:
        imgur_url = match.group(0)
        print(imgur_url)
        imgur_video_save(imgur_url)
        # imgur_video_scrape(imgur_url, page)
        # general_video_scraper(imgur_url)
    
    # if "https://imgur.com" in post_text:
    #     imgur_url = post_text.split("https://imgur.com")[1].split()[0]
    
    
    

if __name__ =="__main__":
    main()