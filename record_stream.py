import yt_dlp
import os
import subprocess
from datetime import datetime
import sys
import traceback
import time
import re
import random

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@odynlive/streams'

def print_message(message):
    print(message, flush=True)

def get_channel_name(channel_url):
    # Implementacja funkcji, która pobiera nazwę kanału z jego URL
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            return info.get('channel', 'unknown')
        except Exception as e:
            print_message(f"Wystąpił błąd podczas pobierania nazwy kanału: {e}")
            return None

def filter_ffmpeg_output(line, last_status_time):
    filtered_line = ""
    # Dodajemy logikę do filtrowania wyjścia z ffmpeg, jeśli to konieczne
    if "error" in line.lower():
        filtered_line = line
    
    current_time = time.time()
    if current_time - last_status_time > 300:  # Co 5 minut
        print_message(f"Status: {line}")
        last_status_time = current_time

    return filtered_line, last_status_time

def record_live_stream(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            channel_name = get_channel_name(CHANNEL_URL)
            if not channel_name:
                channel_name = "unknown"
            
            file_name = f"{channel_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
            
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
            
            ffmpeg_command = [
                'ffmpeg',
                '-i', video_url,
                '-i', audio_url,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-reconnect', '1',
                '-reconnect_streamed', '1',
                '-reconnect_delay_max', '30',  # Zwiększono maksymalne opóźnienie ponownego połączenia
                '-t', '18000',  # Limit nagrywania do 5 godzin
                '-y',  # Nadpisz plik jeśli istnieje
                file_name
            ]
            
            process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            last_status_time = time.time() - 300
            error_count = 0
            max_errors = 5
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    filtered_output, last_status_time = filter_ffmpeg_output(output.strip(), last_status_time)
                    if filtered_output:
                        print_message(filtered_output)
                    if "HTTP error 429" in output:
                        error_count += 1
                        if error_count > max_errors:
                            print_message("Zbyt wiele błędów 429. Ponowne uruchomienie nagrywania...")
                            process.terminate()
                            time.sleep(random.randint(60, 300))  # Losowe opóźnienie między 1 a 5 minut
                            return record_live_stream(video_url)  # Rekurencyjne wywołanie z tym samym URL
            
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
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(CHANNEL_URL, download=False)
            for entry in info['entries']:
                if entry.get('is_live'):
                    return entry.get('url')
            return None
        except Exception as e:
            print_message(f"Wystąpił błąd podczas sprawdzania streamów: {e}")
            return None

if __name__ == "__main__":
    print_message("Rozpoczęcie działania skryptu")
    
    while True:
        try:
            live_stream_url = check_for_live_streams()
        except Exception as e:
            print_message(f"Nieoczekiwany błąd podczas sprawdzania streamów: {e}")
            time.sleep(60)  # Czekaj minutę przed ponowną próbą
            continue
        
        if live_stream_url:
            print_message(f"Znaleziono aktywny stream: {live_stream_url}")
            recorded_file = record_live_stream(live_stream_url)
            if recorded_file:
                print_message(f"Pomyślnie nagrano plik: {recorded_file}")
            else:
                print_message("Nie udało się nagrać streamu.")
        else:
            print_message("Nie znaleziono aktywnych streamów.")
        
        time.sleep(random.randint(60, 180))  # Losowe opóźnienie między 1 a 3 minuty
    
    print_message("Zakończenie działania skryptu")
