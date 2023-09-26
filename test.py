import os

import praw
from dotenv import load_dotenv

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
    submission = reddit.submission(url="https://www.reddit.com/r/xxfitness/comments/119edqq/squat_form_check/")
    post_title = submission.title
    post_text = submission.selftext
    
    print('post_title: ', post_title)
    print('post_text: ', post_text)
    
    

if __name__ =="__main__":
    main()