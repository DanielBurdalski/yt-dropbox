import os
import sys
import requests
from datetime import datetime

try:
    import yt_dlp
except ImportError:
    print("yt-dlp library is not installed. Please install it with `pip install yt-dlp`.")
    sys.exit(1)

# Get API key from environment variable
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')
if not DOODSTREAM_API_KEY:
    print("DOODSTREAM_API_KEY environment variable is not set.")
    sys.exit(1)

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
                live_entries = [entry for entry in info['entries'] if entry.get('ie_key') == 'Youtube' and entry.get('live_status') == 'was_live']
                if len(live_entries) > 1:
                    return f"https://www.youtube.com/watch?v={live_entries[1]['id']}"
        except Exception as e:
            print(f"Error extracting info: {e}")
    return None

def get_available_formats(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'youtube_include_dash_manifest': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            print("Available formats:")
            for f in formats:
                print(f"Format ID: {f['format_id']}, Extension: {f.get('ext', 'N/A')}, Resolution: {f.get('resolution', 'N/A')}, Filesize: {f.get('filesize', 'N/A')}, Protocol: {f.get('protocol', 'N/A')}")
            return formats
        except Exception as e:
            print(f"Error getting available formats: {e}")
            return []

def upload_to_doodstream(file_path):
    upload_url = 'https://doodstream.com.tr/api/upload'
    headers = {
        'Authorization': f'Bearer {DOODSTREAM_API_KEY}',
    }
    with open(file_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, files={'file': f})
    if response.status_code == 200:
        print("File uploaded successfully!")
        return response.json()  # Return the response data
    else:
        print(f"Failed to upload file: {response.status_code}, {response.text}")
        return None

def archive_last_live():
    last_live_url = get_last_completed_live_stream(CHANNEL_URL)
    if not last_live_url:
        print("No completed live stream available.")
        return

    formats = get_available_formats(last_live_url)
    if not formats:
        print("No formats available for download.")
        return

    # Try to find the best format that's not a dash manifest
    best_format = next((f for f in formats if f.get('protocol') != 'dash' and f.get('acodec') != 'none' and f.get('vcodec') != 'none'), None)
    
    if not best_format:
        print("No suitable format found for download.")
        return

    ydl_opts = {
        'format': best_format['format_id'],
        'outtmpl': '%(title)s-%(id)s.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(last_live_url, download=True)
            upload_date = datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%d_%m_%Y')
            filename = f"PaszaTV-{upload_date}.{best_format['ext']}"
            os.rename(ydl.prepare_filename(info), filename)
            
            upload_result = upload_to_doodstream(filename)
            if upload_result:
                print(f"Upload successful. File ID: {upload_result.get('file_code')}")
            
        except Exception as e:
            print(f"Error during download or upload: {e}")
        finally:
            if 'filename' in locals() and os.path.exists(filename):
                os.remove(filename)
                print(f"Temporary file {filename} removed.")

if __name__ == "__main__":
    try:
        archive_last_live()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
