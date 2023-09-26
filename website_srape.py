import requests
from bs4 import BeautifulSoup

def website_video_scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    video_tag = soup.find('video')
    video_url = video_tag.source['src']