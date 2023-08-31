# Reddit Video Scraper
# 1. Download video content (as MP4)
# 2. Post title
# 3. Post text
# 4. Post body text
# 5. All comments and associated ratings information (as JSON)
# 6. Most upvoted comment text and its associated rating

import praw
import requests

import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Access the variables using os.environ
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CILENT_SECRET = os.environ.get("REDDIT_CILENT_SECRET")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT")

# Replace with your own Reddit API credentials
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CILENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# URL of the Reddit post
post_url = "https://www.reddit.com/r/strength_training/comments/1655isb/back_rounding_on_heavy_deadlift_infoquestion_in/"

# Extract video URL, post title, and post text
submission = reddit.submission(url=post_url)
video_url = submission.media["reddit_video"]["fallback_url"]
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

# Print or process the extracted information as needed
print("Video URL:", video_url)
print("Post Title:", post_title)
print("Post Text:", post_text)
print("Post Body Text:", post_body_text)
print("All Comments:", comments_data)
print("Most Upvoted Comment:", most_upvoted_comment)

# You can download the video using requests library
video_response = requests.get(video_url)
with open("reddit_video.mp4", "wb") as video_file:
    video_file.write(video_response.content)

# Download the video content
video_filename = submission.media.get("mp4")
with open(video_filename, "wb") as f:
    f.write(submission.media.get("mp4"))