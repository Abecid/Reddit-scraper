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

from utils import extract_replies

# Load variables from .env file into environment
load_dotenv()

# Access the variables using os.environ
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CILENT_SECRET = os.environ.get("REDDIT_CILENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

def post_exists(post_id, existing_posts):
    return any(post["Post ID"] == post_id for post in existing_posts)

def load_existing_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as jsonfile:
            return json.load(jsonfile)
    return []

def save_data_to_file(post_data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as jsonfile:
        json.dump(post_data, jsonfile, indent=4)

def save_submission(submission, subreddit, output_path="output"):
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

    most_upvoted_comment = None
    
    if len(comments_data) > 0:        
        # Find the most upvoted comment
        most_upvoted_comment = max(comments_data, key=lambda x: x["upvotes"])
        
        # Find the highest rated comment
        highest_reated_comment = max(comments_data, key=lambda x: x["upvotes"] - x["downvotes"])
        
        comments_data = sorted(comments_data, key=lambda x: x["upvotes"] - x["downvotes"], reverse=True)
        
        # most_upvoted_comment_text  = most_upvoted_comment["text"].replace("\n", " ")
        # most_upvoted_comment_rating = most_upvoted_comment["upvotes"] - most_upvoted_comment["downvotes"]

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
        
        # video_path = f"{output_path}/subreddits/{subreddit}/videos/{datetime_str}_{clean_video_filename}"
        video_path = f"{output_path}/subreddits/{subreddit}/videos/{post_id}.mp4"
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
        "Most Upvoted Comment": most_upvoted_comment,
        # "Most Upvoted Comment": most_upvoted_comment_text,
        # "Most Upvoted Comment Rating": most_upvoted_comment_rating,
        # "Comment Path": comment_path,
        "Comments": comments_data        
    }
    
    return submission_json

def save_subreddits(input_filename, reddit, output_path="output", use_all_sort_types=False, restart=True):
    input_data = json.load(open(f'input/{input_filename}'))
    input_data_len = len(input_data)
    
    print(f"Saving total {input_data_len} subreddits")
    
    for index, subreddit_json in enumerate(input_data):
        print(f"[{index+1}/{input_data_len}] Saving subreddit: {subreddit_json['name']}")
        subreddit_name = subreddit_json["name"]
        
        # Define the subreddit
        # subreddit = reddit.subreddit("SUBREDDIT_NAME")
        subreddit = reddit.subreddit(subreddit_name)
        
        sort_types = [
            {
                "name": "top",
                "func": subreddit.top,
                "time_filter": 'all'
            }
            ,
            {
                "name": "new",
                "func": subreddit.new,
                "time_filter": False
            }, 
            {
                "name": "hot",
                "func": subreddit.hot,
                "time_filter": False
            }, 
            {
                "name": "controversial",
                "func": subreddit.controversial,
                "time_filter": 'all'
            },
            {
                "name": "rising",
                "func": subreddit.rising,
                "time_filter": False
            }
        ]
        
        post_data = []
        if restart is False:
            post_data = load_existing_data(f'{output_path}/subreddits/{subreddit_name}/submissions.json')
        
        if use_all_sort_types:
            for idx, sort_type in enumerate(sort_types):
                print(f"Saving subreddit: {subreddit_name} with sort type: {sort_type['name']} ({idx+1}/{len(sort_types)})")
                if sort_type["time_filter"]:
                    for submission in tqdm(sort_type["func"](limit=subreddit_json.get("max", 10), time_filter=sort_type["time_filter"])):
                        if submission.is_video and not post_exists(submission.id, post_data):
                            submission_json = save_submission(submission, subreddit_name, output_path)
                            post_data.append(submission_json)
                else:
                    for submission in tqdm(sort_type["func"](limit=subreddit_json.get("max", 10))):
                        if submission.is_video and not post_exists(submission.id, post_data):
                            submission_json = save_submission(submission, subreddit_name, output_path)
                            post_data.append(submission_json)
                filepath = f'{output_path}/subreddits/{subreddit_name}/submissions.json'
                save_data_to_file(post_data, filepath)
                subreddit_info_object = {
                    "length": len(post_data),
                    "sort types completed": idx+1
                }
                subreddit_info_filepath = f'{output_path}/subreddits/{subreddit_name}/info.json'
                save_data_to_file(subreddit_info_object, subreddit_info_filepath)
                
        else:
            # Fetch the posts
            for submission in tqdm(subreddit.top(limit=subreddit_json.get("max", 10), time_filter='all')):  # Adjust the limit as needed
                # Check if the post has a video
                if submission.is_video:
                    submission_json = save_submission(submission, subreddit_name, output_path)
                    post_data.append(submission_json)
            
            filepath = f'{output_path}/subreddits/{subreddit_name}/submissions.json'
            save_data_to_file(post_data, filepath)
        
        # os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # with open(filepath, 'w') as jsonfile:
        #     json.dump(post_data, jsonfile, indent=4)

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