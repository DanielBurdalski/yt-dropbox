try:
    import yt_dlp
except ImportError:
    print("yt_dlp library is not installed. Please install it with `pip install yt-dlp`.")
    sys.exit(1)

import requests
from datetime import datetime
import os
import sys

# Zastąp to własnym kluczem API
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

CHANNEL_URL = 'https://www.youtube.com/@PaszaTV/streams'

def get_last_completed_live_stream(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                # Zwracanie drugiego strumienia
                live_entries = [entry for entry in info['entries'] if entry.get('ie_key') == 'Youtube' and entry.get('live_status') == 'was_live']
                if len(live_entries) > 1:
                    return f"https://www.youtube.com/watch?v={live_entries[1]['id']}"
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None
    return None

def list_available_formats(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            print("Available formats:")
            for f in formats:
                print(f"Format ID: {f['format_id']}, Resolution: {f.get('format_note', 'N/A')}, Extension: {f.get('ext', 'N/A')}")
        except Exception as e:
            print(f"Error listing formats: {e}")

def upload_to_doodstream(file_path):
    upload_url = 'https://doodstream.com.tr/api/upload'
    headers = {
        'Authorization': f'Bearer {DOODSTREAM_API_KEY}',
    }
    with open(file_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, files={'file': f})
    if response.status_code == 200:
        print("File uploaded successfully!")
    else:
        print(f"Failed to upload file: {response.status_code}, {response.text}")

def archive_last_live():
    last_live_url = get_last_completed_live_stream(CHANNEL_URL)
    if not last_live_url:
        print("Brak dostępnej zakończonej transmisji na żywo.")
        return

    # List available formats to debug
    list_available_formats(last_live_url)
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s-%(id)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(last_live_url, download=True)
            upload_date = datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%d_%m_%Y')
            filename = f"PaszaTV-{upload_date}.{info['ext']}"
            os.rename(ydl.prepare_filename(info), filename)

            upload_to_doodstream(filename)
        except Exception as e:
            print(f"Error during download or upload: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == "__main__":
    try:
        archive_last_live()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
