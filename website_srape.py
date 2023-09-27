import requests
# from bs4 import BeautifulSoup
import re
import youtube_dl

def general_video_scraper(url, video_path='.'):
    try:
        # Using youtube_dl to attempt video extraction
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{video_path}.%(ext)s'
            # 'outtmpl': f'{output_path}/%(title)s.%(ext)s'
            # 'outtmpl': 'downloaded_video.%(ext)s'
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Video downloaded from {url} using youtube_dl")

    except Exception as e:
        if 'imgur' in url:
            imgur_video_save(url, video_path)
        # elif 'youtube' in url:
        #     download_youtube_video(url)
        else:
            print(f'Can\'t download video from this website. {url}')

def imgur_video_save(url, save_path = None):
    video_id = url.split('/')[-1]
    
    # Define the direct link to the video based on Imgur's pattern (this might change if Imgur updates their system)
    video_url = f'https://i.imgur.com/{video_id}.mp4'

    # Download the video
    response = requests.get(video_url, stream=True)
    
    if save_path is None:
        save_path = f"test_output/{video_id}.mp4"
    
    if '.mp4' not in save_path:
        save_path += '.mp4'

    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Imgur Video saved {url}")
    else:
        print(f"Imgur Failed to download. Status code: {response.status_code}; {url}")

# Deprecated
def imgur_video_scrape(url, page):
    page.goto(url)
    
    try:
        # Wait for the video element to be loaded.
        video_element = page.wait_for_selector('video > source', timeout=15000) # Timeout 3 seconds
    except Exception as e:
        print(e)
        print("No video element found")
        return
    video_url = video_element.get_attribute('src')

    if not video_url:
        print("No video URL found")
        return None

    headers = {'User-Agent': 'Mozilla/5.0'}
    video_data = requests.get(video_url, headers=headers).content

    name_from_url = url.split('/')[-1].split('.')[0]
    
    video_name = re.sub(r'[^a-zA-Z0-9]', '_', name_from_url)

    video_data = requests.get(video_url, headers=headers).content
    
    with open(f"test_output/{video_name}.mp4", "wb") as f:
        f.write(video_data)

    print(f"Video downloaded from {url}")

    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    # video_tag = soup.find('video')
    # video_url = video_tag.source['src']
    
def download_youtube_video(youtube_url, output_path='.'):
    if not isinstance(youtube_url, list):
        youtube_url = [youtube_url]
        
    ydl_opts = {
        'format': 'best', # best format (usually mp4)
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # save file with video title as filename
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])