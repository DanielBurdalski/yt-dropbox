import os
import sys
import json
import subprocess
from doodstream import DoodStream

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')
if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def split_video(input_file, segment_time):
    file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_template = f"{file_name}_part_%03d.mp4"
    
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",
        "-map", "0",
        "-segment_time", str(segment_time),
        "-f", "segment",
        "-reset_timestamps", "1",
        output_template
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return [f for f in os.listdir() if f.startswith(f"{file_name}_part_") and f.endswith(".mp4")]
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas dzielenia wideo: {e}")
        return []

def get_video_duration(file_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas pobierania czasu trwania wideo: {e}")
        return 0

def upload_to_doodstream(file_path):
    max_size = 2 * 1024 * 1024 * 1024  # 2 GB w bajtach
    file_size = os.path.getsize(file_path)
    
    if file_size > max_size:
        print(f"Plik jest większy niż 2 GB. Dzielenie na części...")
        duration = get_video_duration(file_path)
        if duration == 0:
            print("Nie udało się określić czasu trwania wideo.")
            return False
        
        # Oblicz czas trwania segmentu, aby każda część miała około 1.9 GB
        segment_time = int((1.9 * 1024 * 1024 * 1024 / file_size) * duration)
        
        split_files = split_video(file_path, segment_time)
        if not split_files:
            print("Nie udało się podzielić pliku wideo.")
            return False
        
        uploaded_urls = []
        for split_file in split_files:
            print(f"Przesyłanie części: {split_file}")
            success, url = upload_single_file(split_file)
            if success:
                uploaded_urls.append(url)
            else:
                print(f"Błąd podczas przesyłania części {split_file}")
                return False
            
            # Usuń część po przesłaniu
            os.remove(split_file)
        
        print("Wszystkie części zostały przesłane.")
        print("URL-e przesłanych części:")
        for url in uploaded_urls:
            print(url)
        return True
    else:
        return upload_single_file(file_path)[0]

def upload_single_file(file_path):
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        return False, None
    
    try:
        response = d.local_upload(file_path)
        
        # Zapisz pełną odpowiedź do pliku
        with open(f'response_{os.path.basename(file_path)}.json', 'w') as f:
            json.dump(response, f, indent=2)
        print(f"Pełna odpowiedź API została zapisana w pliku 'response_{os.path.basename(file_path)}.json'")
        
        if 'status' in response and response['status'] == 200:
            if 'result' in response and isinstance(response['result'], list) and len(response['result']) > 0:
                upload_result = response['result'][0]
                if 'download_url' in upload_result:
                    print(f"Plik przesłany pomyślnie. URL pliku: {upload_result['download_url']}")
                    return True, upload_result['download_url']
                else:
                    print("Odpowiedź nie zawiera 'download_url' w 'result'.")
            else:
                print("Odpowiedź nie zawiera poprawnego 'result'.")
        else:
            print(f"Błąd podczas przesyłania pliku: {response.get('msg', 'Nieznany błąd')}")
        
        return False, None
    except Exception as e:
        print(f"Błąd podczas przesyłania pliku: {str(e)}")
        return False, None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python upload_to_doodstream.py <ścieżka_do_pliku>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = upload_to_doodstream(file_path)
    if not success:
        sys.exit(1)
