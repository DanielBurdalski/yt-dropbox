import yt_dlp
import os
import subprocess
from datetime import datetime
import sys
import traceback

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@PaszaTV/streams'

def print_message(message):
    print(message, flush=True)

def get_channel_name(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            return info['channel']
        except Exception as e:
            print_message(f"Błąd podczas pobierania nazwy kanału: {e}")
            return None

def record_live_stream(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',  # Pobierz najlepsze wideo 720p i najlepszy dźwięk
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            channel_name = get_channel_name(CHANNEL_URL)
            if not channel_name:
                channel_name = "unknown"
            
            file_name = f"{channel_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
            
            # Pobierz URL streamu
            formats = info['formats']
            video_url = None
            audio_url = None

            for f in formats:
                if f.get('height') == 720 and f.get('vcodec') != 'none':
                    video_url = f['url']
                if f.get('acodec') != 'none':
                    audio_url = f['url']
            
            if not video_url or not audio_url:
                print_message("Nie znaleziono odpowiedniego strumienia wideo lub audio.")
                return None
            
            # Użyj FFmpeg do nagrania streamu
            ffmpeg_command = [
                'ffmpeg',
                '-i', video_url,
                '-i', audio_url,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-t', '600',  # Limit nagrywania do 600 sekund
                file_name
            ]
            
            subprocess.run(ffmpeg_command, capture_output=True, text=True)
            
            if os.path.exists(file_name):
                print_message(f"Plik został pomyślnie utworzony: {file_name}")
                return file_name
            else:
                print_message(f"Plik nie został utworzony: {file_name}")
                return None
        except Exception as e:
            print_message(f"Wystąpił błąd podczas nagrywania: {e}")
            return None

def check_for_live_streams():
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(CHANNEL_URL, download=False)
            if info is None:
                return None
            if 'entries' in info:
                for entry in info['entries']:
                    if entry.get('is_live'):
                        return entry['webpage_url']
            return None
        except Exception as e:
            print_message(f"Wystąpił błąd podczas sprawdzania streamów: {e}")
            return None

if __name__ == "__main__":
    print_message("Rozpoczęcie działania skryptu")
    
    try:
        live_stream_url = check_for_live_streams()
    except Exception as e:
        print_message(f"Nieoczekiwany błąd podczas sprawdzania streamów: {e}")
        sys.exit(1)
    
    if live_stream_url:
        print_message(f"Znaleziono aktywny stream: {live_stream_url}")
        recorded_file = record_live_stream(live_stream_url)
        if recorded_file:
            print_message(f"Pomyślnie nagrano plik: {recorded_file}")
        else:
            print_message("Nie udało się nagrać streamu.")
    else:
        print_message("Nie znaleziono aktywnych streamów.")
    
    print_message("Zakończenie działania skryptu")
