# Newest Posts: subreddit.new(limit=1000)
# Retrieves the most recent posts, ordered from newest to oldest.

# Top Posts: subreddit.top(limit=1000, time_filter='all')
# Retrieves the top posts based on upvotes. You can specify a time_filter which can be 'hour', 'day', 'week', 'month', 'year', or 'all'.

# Hot Posts: subreddit.hot(limit=1000)
# Retrieves currently trending or "hot" posts on the subreddit.

# Controversial Posts: subreddit.controversial(limit=1000, time_filter='all')
# Retrieves posts that have a close number of upvotes and downvotes.

# Rising Posts: subreddit.rising(limit=1000)
# Retrieves posts that are quickly gaining attention and upvotes.

import os
from datetime import datetime
from tqdm import tqdm

import json
import praw
import requests
from dotenv import load_dotenv

from main import extract_replies

# Load variables from .env file into environment
load_dotenv()

# Access the variables using os.environ
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CILENT_SECRET = os.environ.get("REDDIT_CILENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

def post_exists(post_id, existing_posts):
    return any(post["Post ID"] == post_id for post in existing_posts)

def save_submission(submission, subreddit):
    post_title = submission.title
    post_text = submission.selftext
    post_body_text = submission.selftext # content
    upvotes = submission.score
    downvotes = submission.downs
    posted_datetime = submission.created_utc
    post_id = submission.id
    
    clean_post_title = post_title.replace(" ", "_").replace("/", "_")

    # Extract comments and their ratings information
    comments_data = []
    for comment in submission.comments:
        if not isinstance(comment, praw.models.MoreComments):
            comments_data.append(extract_replies(comment))

    # Find the most upvoted comment
    most_upvoted_comment = max(comments_data, key=lambda x: x["upvotes"])
    
    # Find the highest rated comment
    highest_reated_comment = max(comments_data, key=lambda x: x["upvotes"] - x["downvotes"])
    
    comments_data = sorted(comments_data, key=lambda x: x["upvotes"] - x["downvotes"], reverse=True)

    # Print or process the extracted information as needed
    # print("Post Title:", post_title)
    # print("Post Text:", post_text)
    # print("Post Body Text:", post_body_text)
    # print("All Comments:", comments_data)
    # print("Most Upvoted Comment:", most_upvoted_comment)
    
    # Save comments data to a JSON file
    # json_filename = f"{clean_post_title}_comments.json"
    # comment_path = f"output/comments/{json_filename}"
    # with open(comment_path, "w", encoding="utf-8") as json_file:
    #     json.dump(comments_data, json_file, indent=4)
    
    video_filename, video_path, video_url = None, None, None
    
    if submission.media is not None:
        video_url = submission.media["reddit_video"].get("fallback_url", None)
        video_filename = video_url.split('/')[-1]
        if '.mp4' not in video_filename:
            video_filename += '.mp4'

        # You can download the video using requests library
        video_response = requests.get(video_url, stream=True)
        mp4_index = video_filename.find(".mp4")
        clean_video_filename = video_filename.replace(" ", "_").replace("/", "_")[:mp4_index+4]
        datetime_str = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y_%m_%d_%H_%M_%S')
        
        video_path = f"output/videos/{subreddit}/{datetime_str}_{clean_video_filename}"
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        with open(video_path, "wb") as video_file:
            for chunk in video_response.iter_content(chunk_size=8192):
                video_file.write(chunk)
            # video_file.write(video_response.content)
            
    submission_json = {
        "Post ID": post_id,
        "Post Title": post_title,
        "subreddit": subreddit,
        "date": posted_datetime,
        "Upvotes": upvotes,
        "Downvotes": downvotes,
        "Post Text": post_text,
        "Post Body Text": post_body_text,
        "Video Filename": video_filename,
        "Video URL": video_url,
        "Video Path": video_path,
        "Most Upvoted Comment": most_upvoted_comment["text"].replace("\n", " "),
        "Most Upvoted Comment Rating": most_upvoted_comment["upvotes"] - most_upvoted_comment["downvotes"],
        # "Comment Path": comment_path,
        "Comments": comments_data        
    }
    
    return submission_json

def save_subreddits(input_filename, reddit):
    input_data = json.load(open(f'input/{input_filename}'))
    
    for subreddit_json in input_data:
        subreddit_name = subreddit_json["name"]
        
        # Define the subreddit
        # subreddit = reddit.subreddit("SUBREDDIT_NAME")
        subreddit = reddit.subreddit(subreddit_name)
        
        post_data = []

        # Fetch the posts
        for submission in tqdm(subreddit.top(limit=subreddit_json.get("max", 10), time_filter='all')):  # Adjust the limit as needed
            # Check if the post has a video
            if submission.is_video:
                submission_json = save_submission(submission, subreddit_name)
                post_data.append(submission_json)
            
        filepath = f'output/subreddits/{subreddit_name}.json'
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as jsonfile:
            json.dump(post_data, jsonfile, indent=4)

def main():
    # Set up the Reddit client
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CILENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        # username="YOUR_USERNAME",
        # password="YOUR_PASSWORD",
    )
    
    input_filename = "gym_subreddits.json"
    save_subreddits(input_filename, reddit)


if __name__ == "__main__":
    main()