import yt_dlp
from datetime import datetime
import os
import sys
import dropbox

DROPBOX_ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

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
                for entry in info['entries']:
                    if entry.get('ie_key') == 'Youtube' and entry.get('live_status') == 'was_live':
                        return f"https://www.youtube.com/watch?v={entry['id']}"
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
    last_live_url = get_last_completed_live_stream(CHANNEL_URL)
    if not last_live_url:
        print("Brak dostępnej zakończonej transmisji na żywo.")
        return

    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s-%(id)s.%(ext)s',
        'noplaylist': True,
        'no_warnings': True,
        'quiet': True,
        'force_generic_extractor': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(last_live_url, download=True)
            upload_date = datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%d_%m_%Y')
            filename = f"PaszaTV-{upload_date}.{info['ext']}"
            os.rename(ydl.prepare_filename(info), filename)

            dropbox_path = f"/{filename}"
            upload_to_dropbox(filename, dropbox_path)
        except yt_dlp.utils.DownloadError as e:
            print(f"Error during download: {e}")
        except Exception as e:
            print(f"Error during upload: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == "__main__":
    try:
        archive_last_live()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
