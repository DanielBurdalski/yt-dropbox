import os
import sys
import json
from doodstream import DoodStream

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')
if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def split_file(file_path, chunk_size):
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    chunk_size = chunk_size * 1024 * 1024  # Convert MB to bytes
    
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunk_num += 1
            chunk_name = f"{file_name}.part{chunk_num:03d}"
            chunk_path = os.path.join(file_dir, chunk_name)
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
            yield chunk_path

def upload_to_doodstream(file_path):
    file_size = os.path.getsize(file_path)
    max_size = 2 * 1024 * 1024 * 1024  # 2 GB in bytes
    
    if file_size > max_size:
        print(f"Plik jest większy niż 2 GB. Dzielenie na części...")
        chunk_size = 1950  # 1950 MB to zapewnić, że każda część będzie mniejsza niż 2 GB
        uploaded_urls = []
        
        for chunk_path in split_file(file_path, chunk_size):
            print(f"Przesyłanie części: {chunk_path}")
            success, url = upload_single_file(chunk_path)
            if success:
                uploaded_urls.append(url)
            else:
                print(f"Błąd podczas przesyłania części {chunk_path}")
                return False
            
            # Usuń część po przesłaniu
            os.remove(chunk_path)
        
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
