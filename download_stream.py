import os
import sys
import yt_dlp
from doodstream import DoodStream

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@MajsterProjekt/streams'
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def is_file_uploaded(filename):
    try:
        response = d.my_uploads()
        if 'result' in response and isinstance(response['result'], list):
            for file in response['result']:
                if filename in file['title']:
                    print(f"Plik '{filename}' jest już przesłany.")
                    return True
    except Exception as e:
        print(f"Błąd podczas sprawdzania plików na DoodStream: {e}")
    return False

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
                        filename = f"{entry['title']}-{entry['id']}"
                        if is_file_uploaded(filename):
                            print(f"Plik '{filename}' jest już przesłany. Pobieranie anulowane.")
                            return None
                        print(f"Znaleziono ostatni stream: {entry['title']}")
                        # Pobierz stream
                        ydl.download([entry['webpage_url']])
                        return f"{filename}.{entry['ext']}"
            
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
