import yt_dlp
from datetime import datetime
import os
import sys
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.
    return GoogleDrive(gauth)

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

def archive_last_live():
    drive = authenticate_google_drive()

    last_live_url = get_last_completed_live_stream(CHANNEL_URL)
    if not last_live_url:
        print("Brak dostępnej zakończonej transmisji na żywo.")
        return

    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s-%(id)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(last_live_url, download=True)
        upload_date = datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%d_%m_%Y')
        filename = f"PaszaTV-{upload_date}.{info['ext']}"
        os.rename(ydl.prepare_filename(info), filename)

    try:
        file_drive = drive.CreateFile({'title': filename})
        file_drive.SetContentFile(filename)
        file_drive.Upload()
        print(f"File uploaded to Google Drive: {file_drive['title']}")
    except Exception as e:
        print(f"Error during upload: {e}")
    finally:
        os.remove(filename)

if __name__ == "__main__":
    try:
        archive_last_live()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
