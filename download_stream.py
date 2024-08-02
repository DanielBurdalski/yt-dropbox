import yt_dlp
import os
import json
import subprocess
from datetime import datetime
import sys
import traceback

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@izakLIVE/streams'

def print_debug(message):
    print(f"DEBUG: {message}", flush=True)

def get_channel_name(channel_url):
    print_debug(f"Pobieranie nazwy kanału dla URL: {channel_url}")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            channel_name = info['channel']
            print_debug(f"Pobrano nazwę kanału: {channel_name}")
            return channel_name
        except Exception as e:
            print_debug(f"Błąd podczas pobierania nazwy kanału: {e}")
            print_debug(f"Pełny traceback: {traceback.format_exc()}")
            return None

def record_live_stream(video_url):
    print_debug(f"Rozpoczęcie nagrywania streamu: {video_url}")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            channel_name = get_channel_name(CHANNEL_URL)
            if not channel_name:
                print_debug("Nie udało się pobrać nazwy kanału, używam 'unknown'")
                channel_name = "unknown"
            
            file_name = f"{channel_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
            
            print_debug(f"Przygotowanie do nagrywania: {info['title']}")
            
            # Pobierz URL streamu
            stream_url = info['formats'][-1]['url']
            print_debug(f"URL streamu: {stream_url}")
            
            # Użyj FFmpeg do nagrania streamu
            ffmpeg_command = [
                'ffmpeg',
                '-i', stream_url,
                '-c', 'copy',
                '-t', '20',  # Limit nagrywania do 20 sekund
                '-v', 'verbose',  # Dodaj szczegółowe logi FFmpeg
                file_name
            ]
            
            print_debug(f"Uruchamianie komendy FFmpeg: {' '.join(ffmpeg_command)}")
            result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
            print_debug(f"Wyjście FFmpeg: {result.stdout}")
            print_debug(f"Błędy FFmpeg: {result.stderr}")
            
            if os.path.exists(file_name):
                print_debug(f"Plik został pomyślnie utworzony: {file_name}")
                return file_name
            else:
                print_debug(f"Plik nie został utworzony: {file_name}")
                return None
        except Exception as e:
            print_debug(f"Wystąpił błąd podczas nagrywania: {e}")
            print_debug(f"Pełny traceback: {traceback.format_exc()}")
            return None

def check_for_live_streams():
    print_debug(f"Sprawdzanie aktywnych streamów dla kanału: {CHANNEL_URL}")
    ydl_opts = {
        'quiet': False,  # Zmienione na False, aby zobaczyć więcej informacji
        'no_warnings': False,  # Zmienione na False, aby zobaczyć ostrzeżenia
        'ignoreerrors': True,  # Ignoruj niektóre błędy, aby kontynuować
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print_debug("Rozpoczęcie extract_info")
            info = ydl.extract_info(CHANNEL_URL, download=False)
            print_debug("Zakończenie extract_info")
            if info is None:
                print_debug("extract_info zwróciło None")
                return None
            if 'entries' in info:
                for entry in info['entries']:
                    if entry.get('is_live'):
                        print_debug(f"Znaleziono aktywny stream: {entry['webpage_url']}")
                        return entry['webpage_url']
            print_debug("Nie znaleziono aktywnych streamów")
            return None
        except Exception as e:
            print_debug(f"Wystąpił błąd podczas sprawdzania streamów: {e}")
            print_debug(f"Pełny traceback: {traceback.format_exc()}")
            return None

if __name__ == "__main__":
    print_debug("Rozpoczęcie działania skryptu")
    print_debug(f"Wersja Pythona: {sys.version}")
    print_debug(f"Ścieżka Pythona: {sys.executable}")
    print_debug(f"Bieżący katalog: {os.getcwd()}")
    print_debug(f"Zawartość katalogu: {os.listdir('.')}")
    
    print_debug("Sprawdzanie aktywnych streamów...")
    try:
        live_stream_url = check_for_live_streams()
    except Exception as e:
        print_debug(f"Nieoczekiwany błąd podczas sprawdzania streamów: {e}")
        print_debug(f"Pełny traceback: {traceback.format_exc()}")
        sys.exit(1)
    
    if live_stream_url:
        print_debug(f"Znaleziono aktywny stream: {live_stream_url}")
        recorded_file = record_live_stream(live_stream_url)
        if recorded_file:
            print_debug(f"Pomyślnie nagrano plik: {recorded_file}")
        else:
            print_debug("Nie udało się nagrać streamu.")
    else:
        print_debug("Nie znaleziono aktywnych streamów.")
    
    print_debug("Zakończenie działania skryptu")
