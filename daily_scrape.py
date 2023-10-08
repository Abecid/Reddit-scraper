import json
from tqdm import tqdm
from datetime import datetime

import pytz
import praw

from utils import extract_replies
from subreddit_scrape import load_existing_data, save_data_to_file, get_keys_in_json, get_submission, post_exists

def check_post_posted_recently(posted_datetime, day=7):
    # Get the post's datetime
    posted_datetime = datetime.datetime.utcfromtimestamp(posted_datetime)

    # Get the current time in Pacific Time Zone (California is in the Pacific Time Zone)
    current_datetime_pacific = datetime.datetime.now(pytz.timezone('US/Pacific'))

    # Convert the current time back to UTC to be consistent with submission.created_utc
    current_datetime_utc = current_datetime_pacific.astimezone(pytz.utc)

    # Check if the post was made within the last 7 days
    is_within_week = (current_datetime_utc - posted_datetime) < datetime.timedelta(days=7)

    print(is_within_week)  #

def get_updated_comments(submission, subreddit_name, output_path, post_data, original_json):
    posted_datetime = submission.created_utc
    
    if check_post_posted_recently():
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
        original_json['Comments'] = comments_data
        return original_json
    else:
        return original_json

def get_updated_sumbission(submission, subreddit_name, output_path, post_data):
    if not post_exists(submission.id, post_data):
        return get_submission(submission, subreddit_name, output_path, post_data)
    else:
        return get_updated_comments(submission, subreddit_name, output_path, post_data)

def save_daily_scrape(input_filename, reddit, output_path="output"):
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
        post_data = load_existing_data(f'{output_path}/subreddits/{subreddit_name}/submissions.json')
        
        video_links_saved_json = []
        videos_links_saved_failed_json = []
        
        external_video_info = load_existing_data(f'{output_path}/subreddits/{subreddit_name}/video_link_info.json')
        if len(external_video_info) > 0:
            video_links_saved_json = external_video_info.get("Videos saved from external links", [])
            video_links_saved_json = [{"Post ID": item["Post ID"], "External url": item["External url"]} for item in video_links_saved_json]
            videos_links_saved_failed_json = external_video_info.get("Videos failed to save from external links", [])
            videos_links_saved_failed_json = [{"Post ID": item["Post ID"], "External url": item["External url"]} for item in videos_links_saved_failed_json]
    for submission in tqdm(subreddit.top(limit=subreddit_json.get("max", 10), time_filter='all')):  # Adjust the limit as needed
        # Check if the post has a video
        submission_json = get_updated_sumbission(submission, subreddit_name, output_path, post_data)
        if submission_json is not None:
            if submission_json.get("Video Failed", False) is False: 
                post_data.append(submission_json)
                if submission_json.get("External url", None) is not None:
                    # video_links_saved_json.append(submission_json)
                    video_links_saved_json.append(get_keys_in_json(submission_json, ["Post ID", "External url"]))
            else: videos_links_saved_failed_json.append(submission_json)
    
    filepath = f'{output_path}/subreddits/{subreddit_name}/submissions.json'
    save_data_to_file(post_data, filepath)
    subreddit_info_object = {
        "length": len(post_data),
        "sort types completed": idx+1
    }
    subreddit_info_filepath = f'{output_path}/subreddits/{subreddit_name}/info.json'
    save_data_to_file(subreddit_info_object, subreddit_info_filepath)
    
    subreddit_video_in_link_info = {
        "Total Videos Saved from External Links": len(video_links_saved_json),
        "Total Videos failed to save from external links": len(videos_links_saved_failed_json),
        "Last sort type": "new",
        "Videos saved from external links": video_links_saved_json,
        "Videos failed to save from external links": videos_links_saved_failed_json
    }
    subreddit_video_in_link_info_path = f'{output_path}/subreddits/{subreddit_name}/video_link_info.json'
    save_data_to_file(subreddit_video_in_link_info, subreddit_video_in_link_info_path)

def main():
    pass

if __name__ == "__main__":
    main()