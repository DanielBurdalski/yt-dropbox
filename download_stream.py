import yt_dlp
import os
from datetime import datetime, timedelta
import json

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@MajsterProjekt/streams'

def check_if_downloaded(file_name):
    download_info_file = 'download_info.json'
    
    if not os.path.exists(download_info_file):
        return False
    
    with open(download_info_file, 'r') as f:
        download_info = json.load(f)
    
    if file_name in download_info:
        last_download_time = datetime.fromisoformat(download_info[file_name])
        if datetime.now() - last_download_time < timedelta(days=7):
            return True
    
    return False

def update_download_info(file_name):
    download_info_file = 'download_info.json'
    
    if os.path.exists(download_info_file):
        with open(download_info_file, 'r') as f:
            download_info = json.load(f)
    else:
        download_info = {}
    
    download_info[file_name] = datetime.now().isoformat()
    
    with open(download_info_file, 'w') as f:
        json.dump(download_info, f)

def get_last_stream():
    # Konfiguracja yt-dlp
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[ext=mp4]',
        'outtmpl': '%(title)s-%(id)s.%(ext)s',
        'playlistend': 1,  # Pobierz tylko najnowszy stream
        'merge_output_format': 'mp4',  # Wymusza format wyjściowy MP4
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Pobierz informacje o streamach
            info = ydl.extract_info(CHANNEL_URL, download=False)
            
            if 'entries' in info:
                # Wybierz ostatni zakończony stream
                for entry in info['entries']:
                    if entry.get('live_status') == 'was_live':
                        file_name = f"{entry['title']}-{entry['id']}.mp4"
                        
                        if not check_if_downloaded(file_name):
                            print(f"Znaleziono ostatni stream do pobrania: {entry['title']}")
                            ydl.download([entry['webpage_url']])
                            update_download_info(file_name)
                            return file_name
                        else:
                            print(f"Stream {entry['title']} był już pobrany w ciągu ostatnich 7 dni. Pomijam.")
                            return None
            
            print("Nie znaleziono odpowiedniego streamu.")
            return None
        except Exception as e:
            print(f"Wystąpił błąd: {e}")
            return None

if __name__ == "__main__":
    downloaded_file = get_last_stream()
    if downloaded_file:
        print(f"Pomyślnie pobrano plik: {downloaded_file}")
    else:
        print("Nie udało się pobrać nowego streamu lub stream był już pobrany.")
