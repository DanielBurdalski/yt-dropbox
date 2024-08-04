import sys
from yt_dlp import YoutubeDL

def check_live_stream(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
# skrypt sprawdza czy na kanale jest aktualnie transmisja na żywo
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            for entry in info['entries']:
                if entry.get('is_live'):
                    print(f"Znaleziono aktywną transmisję: {entry['title']}")
                    print(f"URL transmisji: https://www.youtube.com/watch?v={entry['id']}")
                    sys.exit(0)
            print("Brak aktywnej transmisji na żywo.")
            sys.exit(1)
        except Exception as e:
            print(f"Błąd podczas sprawdzania transmisji: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python check_live_stream.py <channel_url>")
        sys.exit(1)

    channel_url = sys.argv[1]
    check_live_stream(channel_url)
