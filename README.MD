# Video Scraping from Reddit   
This script scrapes videos and content from reddit   
1. Download video content (as MP4)
2. Post title
3. Post text
4. Post body text
5. All comments and associated ratings information (as JSON)
6. Most upvoted comment text and its associated rating

## 1. Install dependencies
```
pip install -r requirements.txt
```


## 2. Add environment variables
1. Create a .env file
```
touch .env
```
2. Add environment variables
```
REDDIT_CLIENT_ID=<client_id>
REDDIT_CILENT_SECRET=<client_secret>
REDDIT_USER_AGENT=<User Agent>
```

## 3. Run program
```python
python3 main.py
```