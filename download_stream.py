import yt_dlp
import os
import json
import time
import subprocess
from datetime import datetime, timedelta

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@onet/streams'

def check_if_recorded(file_name):
    record_info_file = 'record_info.json'
    if not os.path.exists(record_info_file):
        return False
    with open(record_info_file, 'r') as f:
        record_info = json.load(f)
    if file_name in record_info:
        last_record_time = datetime.fromisoformat(record_info[file_name])
        if datetime.now() - last_record_time < timedelta(days=7):
            return True
    return False

def update_record_info(file_name):
    record_info_file = 'record_info.json'
    if os.path.exists(record_info_file):
        with open(record_info_file, 'r') as f:
            record_info = json.load(f)
    else:
        record_info = {}
    record_info[file_name] = datetime.now().isoformat()
    with open(record_info_file, 'w') as f:
        json.dump(record_info, f)

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
            file_name = f"{channel_name}-{datetime.now().strftime('%Y-%m-%d')}.mp4"
            
            if not check_if_recorded(file_name):
                print(f"Rozpoczęto nagrywanie streamu: {info['title']}")
                
                # Pobierz URL streamu
                stream_url = info['formats'][-1]['url']
                
                # Użyj FFmpeg do nagrania streamu
                ffmpeg_command = [
                    'ffmpeg',
                    '-i', stream_url,
                    '-c', 'copy',
                    '-t', '20',  # Limit nagrywania do 3 godzin (10800 sekund)
                    file_name
                ]
                
                subprocess.run(ffmpeg_command)
                
                update_record_info(file_name)
                return file_name
            else:
                print(f"Stream {info['title']} był już nagrywany w ciągu ostatnich 7 dni. Pomijam.")
                return None
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
    while True:
        print("Sprawdzanie aktywnych streamów...")
        live_stream_url = check_for_live_streams()
        
        if live_stream_url:
            print(f"Znaleziono aktywny stream: {live_stream_url}")
            recorded_file = record_live_stream(live_stream_url)
            if recorded_file:
                print(f"Pomyślnie nagrano plik: {recorded_file}")
            else:
                print("Nie udało się nagrać streamu lub stream był już nagrywany.")
        else:
            print("Nie znaleziono aktywnych streamów.")
        
        print("Oczekiwanie 5 minut przed kolejnym sprawdzeniem...")
        time.sleep(300)  # Czekaj 5 minut przed kolejnym sprawdzeniem
