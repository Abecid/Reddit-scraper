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

# Load variables from .env file into environment
load_dotenv()

# Access the variables using os.environ
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CILENT_SECRET = os.environ.get("REDDIT_CILENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

# URL of the Reddit post
post_url = "https://www.reddit.com/r/strength_training/comments/1655isb/back_rounding_on_heavy_deadlift_infoquestion_in/"
urls = [post_url]

def main():
    # Replace with your own Reddit API credentials
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CILENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    csv_filename = "reddit_data.csv"
    csv_output = f"output/{csv_filename}"
    with open(csv_output, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Post Title", "Post Text", "Post Body Text", "Video URL", "Video Filename", "Video Path", "Most Upvoted Comment", "Most Upvoted Comment Rating", "Comment Path"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()  # Write header row
        for post_url in urls:
            # Extract video URL, post title, and post text
            submission = reddit.submission(url=post_url)
            
            video_url = submission.media["reddit_video"]["fallback_url"]
            video_filename = submission.media['reddit_video']['fallback_url'].split('/')[-1]
            if '.mp4' not in video_filename:
                video_filename += '.mp4'
            
            post_title = submission.title
            post_text = submission.selftext
            post_body_text = submission.selftext # content

            # Extract comments and their ratings information
            comments_data = []
            for comment in submission.comments:
                comment_data = {
                    "text": comment.body,
                    "upvotes": comment.score,
                    "downvotes": comment.downs
                }
                comments_data.append(comment_data)

            # Find the most upvoted comment
            most_upvoted_comment = max(comments_data, key=lambda x: x["upvotes"])
            
            # Find the highest rated comment
            highest_reated_comment = max(comments_data, key=lambda x: x["upvotes"] - x["downvotes"])
            
            comments_data = sorted(comments_data, key=lambda x: x["upvotes"] - x["downvotes"], reverse=True)

            # Print or process the extracted information as needed
            print("Video URL:", video_url)
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
                "Post Body Text": post_body_text,
                "Video Path": video_path,
                "Most Upvoted Comment": most_upvoted_comment["text"],
                "Most Upvoted Comment Rating": most_upvoted_comment["upvotes"] - most_upvoted_comment["downvotes"],
                "Comment Path": comment_path
            })
    
if __name__ == "__main__":
    main()
