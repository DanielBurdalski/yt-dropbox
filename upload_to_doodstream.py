import os
import sys
import json
import subprocess
import requests
from doodstream import DoodStream

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')
if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def split_video(input_file, target_size_gb=1.5):
    file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_template = f"{file_name}_part_%03d.mp4"
    target_size_bytes = int(target_size_gb * 1024 * 1024 * 1024)  # Convert GB to bytes
    
    # Get video bitrate
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-count_packets",
        "-show_entries", "stream=bit_rate",
        "-of", "csv=p=0",
        input_file
    ]
    bitrate = int(subprocess.check_output(cmd).decode().strip())
    
    # Calculate segment duration based on target size and bitrate
    segment_duration = (target_size_bytes * 8) / bitrate
    
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",
        "-map", "0",
        "-segment_time", str(int(segment_duration)),
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

def upload_to_doodstream(file_path):
    max_size = 1.9 * 1024 * 1024 * 1024  # 1.9 GB w bajtach
    file_size = os.path.getsize(file_path)
    
    if file_size > max_size:
        print(f"Plik jest większy niż 1.9 GB. Dzielenie na części...")
        split_files = split_video(file_path)
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
        # Użyj bezpośrednio requests zamiast DoodStream API wrapper
        url = "https://doodapi.com/api/upload/server"
        params = {'api_key': DOODSTREAM_API_KEY}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Błąd podczas pobierania serwera uploadowego: {response.text}")
            return False, None
        
        upload_url = response.json().get('result')
        if not upload_url:
            print("Nie udało się uzyskać URL do przesyłania.")
            return False, None
        
        files = {'file': open(file_path, 'rb')}
        upload_response = requests.post(upload_url, files=files)
        
        if upload_response.status_code != 200:
            print(f"Błąd podczas przesyłania pliku: {upload_response.text}")
            return False, None
        
        result = upload_response.json()
        
        # Zapisz pełną odpowiedź do pliku
        with open(f'response_{os.path.basename(file_path)}.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Pełna odpowiedź API została zapisana w pliku 'response_{os.path.basename(file_path)}.json'")
        
        if result.get('status') == 200:
            file_code = result.get('file_code')
            if file_code:
                download_url = f"https://dood.so/{file_code}"
                print(f"Plik przesłany pomyślnie. URL pliku: {download_url}")
                return True, download_url
            else:
                print("Odpowiedź nie zawiera 'file_code'.")
        else:
            print(f"Błąd podczas przesyłania pliku: {result.get('msg', 'Nieznany błąd')}")
        
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
