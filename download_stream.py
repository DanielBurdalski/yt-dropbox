import yt_dlp
import os
from datetime import datetime, timedelta

# URL kanału
CHANNEL_URL = 'https://www.youtube.com/@MajsterProjekt/streams'

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
                        print(f"Znaleziono ostatni stream: {entry['title']}")
                        # Pobierz stream
                        ydl.download([entry['webpage_url']])
                        return f"{entry['title']}-{entry['id']}.{entry['ext']}"
            
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
