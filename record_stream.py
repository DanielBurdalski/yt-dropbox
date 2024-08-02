import yt_dlp
import os
import subprocess
from datetime import datetime
import sys
import traceback
import time
import re

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@odynlive/streams'

def print_message(message):
    print(message, flush=True)

def get_channel_name(channel_url):
    # ... (pozostała część funkcji bez zmian)

def filter_ffmpeg_output(line, last_status_time):
    current_time = time.time()
    
    # Filtruj linie, które zawierają specyficzne wzorce
    patterns_to_ignore = [
        r'Opening .* for reading',
        r'Skip \(\'#EXT-X-VERSION',
        r'Skip \(\'#EXT-X-PROGRAM-DATE-TIME',
    ]
    
    # Jeśli linia pasuje do któregokolwiek z wzorców, ignoruj ją
    if any(re.search(pattern, line) for pattern in patterns_to_ignore):
        return None, last_status_time
    
    # Wyświetlaj informacje o postępie lub błędach
    if 'frame=' in line or 'error' in line.lower():
        return line, last_status_time
    
    # Wyświetlaj status co 5 minut
    if current_time - last_status_time >= 300:  # 300 sekund = 5 minut
        status = "Nagrywanie przebiega prawidłowo."
        last_status_time = current_time
        return status, last_status_time
    
    return None, last_status_time

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
            
            # ... (pozostała część kodu do uzyskania URL wideo i audio)
            
            ffmpeg_command = [
                'ffmpeg',
                '-i', video_url,
                '-i', audio_url,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-reconnect', '1',
                '-reconnect_streamed', '1',
                '-reconnect_delay_max', '5',
                '-t', '18000',  # Limit nagrywania do 5 godzin
                '-y',  # Nadpisz plik jeśli istnieje
                file_name
            ]
            
            process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            last_status_time = time.time() - 300  # Inicjalizacja, aby wyświetlić status na początku
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    filtered_output, last_status_time = filter_ffmpeg_output(output.strip(), last_status_time)
                    if filtered_output:
                        print_message(filtered_output)
            
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
    # ... (pozostała część funkcji bez zmian)

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
        
        time.sleep(60)  # Czekaj minutę przed ponownym sprawdzeniem
    
    print_message("Zakończenie działania skryptu")