import yt_dlp
import os
from datetime import datetime, timedelta

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@MajsterProjekt/streams'
UPLOADS_FILE = 'uploads.txt'

def has_been_downloaded(file_name):
    """Sprawdza, czy plik o podanej nazwie został już pobrany."""
    if not os.path.exists(UPLOADS_FILE):
        return False
    with open(UPLOADS_FILE, 'r') as f:
        downloaded_files = f.read().splitlines()
    return file_name in downloaded_files

def mark_as_downloaded(file_name):
    """Zapisuje nazwę pobranego pliku do uploads.txt."""
    with open(UPLOADS_FILE, 'a') as f:
        f.write(file_name + '\n')

def get_last_stream():
    # Konfiguracja yt-dlp
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
        'outtmpl': '%(title)s-%(id)s.%(ext)s',
        'playlistend': 1,  # Pobierz tylko najnowszy stream
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Pobierz informacje o streamach
            info = ydl.extract_info(CHANNEL_URL, download=False)
            
            if 'entries' in info:
                # Wybierz ostatni zakończony stream
                for entry in info['entries']:
                    if entry.get('live_status') == 'was_live':
                        file_name = f"{entry['title']}-{entry['id']}.{entry['ext']}"
                        
                        # Sprawdź, czy plik został już pobrany
                        if has_been_downloaded(file_name):
                            print(f"Plik '{file_name}' został już pobrany.")
                            return None
                        
                        print(f"Znaleziono ostatni stream: {entry['title']}")
                        # Pobierz stream
                        ydl.download([entry['webpage_url']])
                        
                        # Zapisz nazwę pobranego pliku
                        mark_as_downloaded(file_name)
                        
                        return file_name
            
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
        print("Nie udało się pobrać streamu.")
