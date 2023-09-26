# Reddit Video Scraper
# 1. Download video content (as MP4)
# 2. Post title
# 3. Post text
# 4. Post body text
# 5. All comments and associated ratings information (as JSON)
# 6. Most upvoted comment text and its associated rating

import requests
import csv
import json
import os

import praw
from dotenv import load_dotenv

from subreddit_scrape import save_subreddits

# Load variables from .env file into environment
load_dotenv()

# Access the variables using os.environ
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CILENT_SECRET = os.environ.get("REDDIT_CILENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

# URL of the Reddit post
post_url = "https://www.reddit.com/r/strength_training/comments/1655isb/back_rounding_on_heavy_deadlift_infoquestion_in/"
text_post_url = "https://www.reddit.com/r/Notion/comments/irw19f/cannot_save_changes_what_does_this_mean/"
urls = [post_url, text_post_url]

def extract_replies(comment):
    """
    Recursive function to extract nested comments and their data.
    """
    comment_data = {
        "text": comment.body,
        "upvotes": comment.score,
        "downvotes": comment.downs,
        "user_id": str(comment.author)  # Convert Redditor object to string for user_id
    }

    # If the comment has replies, extract them recursively
    if hasattr(comment, "replies"):
        comment_data["replies"] = [extract_replies(reply) for reply in comment.replies if not isinstance(reply, praw.models.MoreComments)]

    return comment_data

def save_posts(urls, reddit):
    csv_filename = "reddit_data.csv"
    csv_output = f"output/{csv_filename}"
    with open(csv_output, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Post Title", "Post Text", "Post Body Text", "Video URL", "Video Filename", "Video Path", "Most Upvoted Comment", "Most Upvoted Comment Rating", "Comment Path"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()  # Write header row
        for post_url in urls:
            # Extract video URL, post title, and post text
            submission = reddit.submission(url=post_url)
            
            post_title = submission.title
            post_text = submission.selftext
            post_body_text = submission.selftext # content

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
            print("Post Title:", post_title)
            print("Post Text:", post_text)
            print("Post Body Text:", post_body_text)
            print("All Comments:", comments_data)
            print("Most Upvoted Comment:", most_upvoted_comment)
            
            # Save comments data to a JSON file
            clean_post_title = post_title.replace(" ", "_").replace("/", "_")
            json_filename = f"{clean_post_title}_comments.json"
            comment_path = f"output/comments/{json_filename}"
            with open(comment_path, "w", encoding="utf-8") as json_file:
                json.dump(comments_data, json_file, indent=4)
            
            video_filename, video_path, video_url = None, None, None
            
            if submission.media is not None:
                video_url = submission.media["reddit_video"].get("fallback_url", None)
                video_filename = video_url.split('/')[-1]
                if '.mp4' not in video_filename:
                    video_filename += '.mp4'

                # You can download the video using requests library
                video_response = requests.get(video_url)
                mp4_index = video_filename.find(".mp4")
                clean_video_filename = video_filename.replace(" ", "_").replace("/", "_")[:mp4_index+4]
                video_path = f"output/videos/{clean_video_filename}"
                with open(video_path, "wb") as video_file:
                    video_file.write(video_response.content)
                
            csv_writer.writerow({
                "Video URL": video_url,
                "Video Filename": video_filename,
                "Post Title": post_title,
                "Post Text": post_text,
                # "Post Body Text": post_body_text,
                "Video Path": video_path,
                "Most Upvoted Comment": most_upvoted_comment["text"].replace("\n", " "),
                "Most Upvoted Comment Rating": most_upvoted_comment["upvotes"] - most_upvoted_comment["downvotes"],
                "Comment Path": comment_path
            })

def main():
    # Replace with your own Reddit API credentials
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CILENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    input_filename = "gym_subreddits.json"
    output_path = "/home/amir/gymgpt/output"
    save_subreddits(input_filename, reddit, output_path, use_all_sort_types=True, restart=False)
    # save_posts(urls, reddit)
    
if __name__ == "__main__":
    main()
