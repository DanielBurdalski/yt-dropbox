import streamlink
import os
import subprocess
from datetime import datetime
import sys
import time

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@Telewizja_Republika/streams'

def print_message(message):
    print(message, flush=True)

def get_channel_name(channel_url):
    try:
        streams = streamlink.streams(channel_url)
        if streams:
            plugin = streams.session.plugins["youtube"].get_author()
            return plugin
    except Exception as e:
        print_message(f"Błąd podczas pobierania nazwy kanału: {e}")
    return None

def record_live_stream(video_url):
    try:
        channel_name = get_channel_name(CHANNEL_URL) or "unknown"
        file_name = f"{channel_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        
        # Użyj Streamlink do nagrania streamu
        streamlink_command = [
            'streamlink',
            '--stream-segment-threads', '2',
            '--stream-timeout', '60',
            '--hls-live-restart',
            '--hls-timeout', '60',
            '-o', file_name,
            video_url, 'best'
        ]
        
        process = subprocess.Popen(streamlink_command)
        time.sleep(120)  # Nagrywaj przez 120 s
        process.terminate()
        
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
    try:
        streams = streamlink.streams(CHANNEL_URL)
        if streams:
            return CHANNEL_URL
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
