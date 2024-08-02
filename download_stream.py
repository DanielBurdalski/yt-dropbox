import yt_dlp
import os
import json
import subprocess
from datetime import datetime

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@PaszaTV/streams'

def get_channel_name(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return info['channel']

def record_live_stream(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            channel_name = get_channel_name(CHANNEL_URL)
            file_name = f"{channel_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
            
            print(f"Rozpoczęto nagrywanie streamu: {info['title']}")
            
            # Pobierz URL streamu
            stream_url = info['formats'][-1]['url']
            
            # Użyj FFmpeg do nagrania streamu
            ffmpeg_command = [
                'ffmpeg',
                '-i', stream_url,
                '-c', 'copy',
                '-t', '20',  # Limit nagrywania do 20 sekund
                file_name
            ]
            
            subprocess.run(ffmpeg_command)
            
            return file_name
        except Exception as e:
            print(f"Wystąpił błąd podczas nagrywania: {e}")
            return None

def check_for_live_streams():
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(CHANNEL_URL, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry.get('is_live'):
                        return entry['webpage_url']
            return None
        except Exception as e:
            print(f"Wystąpił błąd podczas sprawdzania streamów: {e}")
            return None

if __name__ == "__main__":
    print("Sprawdzanie aktywnych streamów...")
    live_stream_url = check_for_live_streams()
    
    if live_stream_url:
        print(f"Znaleziono aktywny stream: {live_stream_url}")
        recorded_file = record_live_stream(live_stream_url)
        if recorded_file:
            print(f"Pomyślnie nagrano plik: {recorded_file}")
        else:
            print("Nie udało się nagrać streamu.")
    else:
        print("Nie znaleziono aktywnych streamów.")
