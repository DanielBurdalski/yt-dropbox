import yt_dlp
from datetime import datetime
import os
import sys
import dropbox
import subprocess

DROPBOX_ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

CHANNEL_URL = 'https://www.youtube.com/@PaszaTV/streams'

def get_second_completed_live_stream(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            completed_streams = []
            if 'entries' in info:
                for entry in info['entries']:
                    if entry.get('ie_key') == 'Youtube' and entry.get('live_status') == 'was_live':
                        completed_streams.append(entry)
            if len(completed_streams) >= 2:
                return f"https://www.youtube.com/watch?v={completed_streams[1]['id']}"
            else:
                print("Nie znaleziono wystarczającej liczby zakończonych transmisji na żywo.")
                return None
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None
    return None

def upload_to_dropbox(file_path, dropbox_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path)
    print(f"File uploaded to Dropbox: {dropbox_path}")

def archive_last_live():
    second_live_url = get_second_completed_live_stream(CHANNEL_URL)
    if not second_live_url:
        print("Brak dostępnej drugiej zakończonej transmisji na żywo.")
        return

    ydl_opts = {
        'format': 'best/bestvideo+bestaudio/best',
        'outtmpl': '%(title)s-%(id)s.%(ext)s',
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(second_live_url, download=True)
        upload_date = datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%d_%m_%Y')
        filename = f"PaszaTV-{upload_date}.{info['ext']}"
        os.rename(ydl.prepare_filename(info), filename)

    try:
        dropbox_path = f"/{filename}"
        upload_to_dropbox(filename, dropbox_path)
    except Exception as e:
        print(f"Error during upload: {e}")
    finally:
        os.remove(filename)

if __name__ == "__main__":
    try:
        # Update yt-dlp to the latest version
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'])
        
        # Install ffmpeg
        subprocess.run(['apt-get', 'update'])
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'])
        
        archive_last_live()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
