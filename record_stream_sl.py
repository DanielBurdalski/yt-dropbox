import streamlink
import os
import subprocess
from datetime import datetime
import sys
import time
import requests
import re

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@ProboszczProboszcz/streams'

def print_message(message):
    print(message, flush=True)

def get_channel_name(channel_url):
    try:
        response = requests.get(channel_url)
        match = re.search(r'<meta property="og:title" content="(.*?)"', response.text)
        if match:
            return match.group(1)
    except Exception as e:
        print_message(f"Błąd podczas pobierania nazwy kanału: {e}")
    return None

def record_live_stream(video_url):
    try:
        channel_name = get_channel_name(CHANNEL_URL) or "unknown"
        file_name = f"{channel_name}-{datetime.now().strftime('%d-%m-%Y_%H-%M')}.mp4"
        
        streamlink_command = [
            'streamlink',
            '--stream-segment-threads', '2',
            '--stream-timeout', '60',
            '--hls-live-restart',
            '--hls-timeout', '60',
            '-o', file_name,
            video_url, 'best'
        ]
        
        print_message(f"Rozpoczęcie nagrywania: {' '.join(streamlink_command)}")
        process = subprocess.Popen(streamlink_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(100)  # Nagrywaj przez 100 sekund
        process.terminate()
        
        stdout, stderr = process.communicate()
        print_message(f"Streamlink stdout: {stdout.decode()}")
        print_message(f"Streamlink stderr: {stderr.decode()}")
        
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
        print_message(f"Sprawdzanie streamów dla URL: {CHANNEL_URL}")
        response = requests.get(CHANNEL_URL)
        match = re.search(r'(?:"watchEndpoint":{"videoId":")(.*?)(?:")', response.text)
        if match:
            video_id = match.group(1)
            live_url = f"https://www.youtube.com/watch?v={video_id}"
            print_message(f"Znaleziono potencjalny aktywny stream: {live_url}")
            
            # Sprawdź, czy stream jest rzeczywiście aktywny
            streams = streamlink.streams(live_url)
            if streams:
                print_message(f"Potwierdzono aktywny stream: {live_url}")
                return live_url
            else:
                print_message(f"Stream nie jest aktywny: {live_url}")
        else:
            print_message("Nie znaleziono żadnych streamów na stronie kanału")
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
