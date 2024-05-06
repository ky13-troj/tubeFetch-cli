from pytube import Playlist
import os
import time
import yt_dlp
from datetime import datetime

class PlaylistGenerator:
    def __init__(self, playlist_name):
        self.playlist_name = playlist_name

    def generate_playlist_links(self):
        if 'playlist' in self.playlist_name.lower():
            playlist = Playlist(self.playlist_name)
            video_links = playlist.video_urls
        else:
            video_links = [self.playlist_name]

        with open('links.txt', 'w') as file:
            for link in video_links:
                file.write(link + '\n')

class VideoDownloader:
    def __init__(self, playlist_name, links_file='links.txt', output_directory='downloads', resolution='720p'):
        self.playlist_name = playlist_name
        self.links_file = links_file
        self.output_directory = output_directory
        self.resolution = resolution
        self.total_time = 0

    def sanitize_filename(self, title):
        return title.replace("/", "_")

    def download_video(self):
        with open(self.links_file, 'r') as file:
            video_urls = file.readlines()
            
        today_date = datetime.today().date()
        current_time = datetime.now().time()
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        
        with open(os.path.join(self.output_directory, "video_details.txt"), "a", encoding="utf-8") as video_details_file:
            video_details_file.write(f"Downloading videos from playlist/video: {self.playlist_name}\n\nDate: {today_date}\nTime: {current_time}\n\n")
            for i, video_url in enumerate(video_urls):
                try:
                    start_time = time.time()

                    ydl_opts = {
                        'format': f'bestvideo[height={self.resolution}]+bestaudio/best',
                        'outtmpl': f'{self.output_directory}/%(title)s.%(ext)s',
                        'quiet': True,
                        'extractor_args': {
                            'youtube': {
                                'quiet': True,
                                'nocheckcertificate': True,
                                'source_address': '0.0.0.0',
                            },
                            'youtube:info': {
                                'skip': ['ios', 'android', 'm3u8'],
                            },
                        },
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(video_url, download=True)
                        video_title = info_dict.get('title', 'video')
                        video_details_file.write(f"{i+1}. {video_title} : {video_url}\n\n")

                        if not os.path.exists(self.output_directory):
                            os.makedirs(self.output_directory)

                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        self.total_time += elapsed_time

                        print(f"Time taken: {elapsed_time} seconds\n")

                except yt_dlp.utils.DownloadError as e:
                    if 'Video unavailable' in str(e):
                        print(f"Warning: Video '{video_url}' is unavailable due to copyright restrictions.")
                    else:
                        print(f"Error: {e}")

if __name__ == "__main__":
    banner = '''

 _______  __   __  _______  _______         _______  _______  _______  _______  __   __ 
|       ||  | |  ||  _    ||       |       |       ||       ||       ||       ||  | |  |
|_     _||  | |  || |_|   ||    ___| ____  |    ___||    ___||_     _||       ||  |_|  |
  |   |  |  |_|  ||       ||   |___ |____| |   |___ |   |___   |   |  |       ||       |
  |   |  |       ||  _   | |    ___|       |    ___||    ___|  |   |  |      _||       |
  |   |  |       || |_|   ||   |___        |   |    |   |___   |   |  |     |_ |   _   |
  |___|  |_______||_______||_______|       |___|    |_______|  |___|  |_______||__| |__|

    '''
    print(banner)
    playlist_name = input("Enter the YouTube playlist URL: ")
    
    playlist_generator = PlaylistGenerator(playlist_name)
    playlist_generator.generate_playlist_links()
    
    downloader = VideoDownloader(playlist_name)
    downloader.download_video()
