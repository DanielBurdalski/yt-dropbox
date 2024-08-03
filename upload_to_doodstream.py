import os
import sys
from datetime import datetime
from doodstream import DoodStream

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')
if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def create_folder(folder_name):
    response = d.create_folder(folder_name)
    if response['status'] == 200:
        return response['result']['fld_id']
    return None

def get_or_create_folder(channel_name):
    folders = d.list_folders()
    for folder in folders['result']['folders']:
        if folder['name'] == channel_name:
            return folder['fld_id']
    return create_folder(channel_name)

def upload_to_doodstream(file_path, channel_name, max_retries=3):
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        return False

    folder_id = get_or_create_folder(channel_name)
    if not folder_id:
        print(f"Nie można utworzyć lub znaleźć folderu dla kanału {channel_name}.")
        return False

    file_name = os.path.basename(file_path)
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_file_name = f"{channel_name}-{date_str}.mp4"

    attempt = 0
    while attempt < max_retries:
        try:
            response = d.local_upload(file_path, fld_id=folder_id, new_title=new_file_name)
            print(f"Odpowiedź API (próba {attempt + 1}): {response}")
            if 'status' in response and response['status'] == 200:
                if 'result' in response and isinstance(response['result'], list) and len(response['result']) > 0:
                    upload_result = response['result'][0]
                    if 'download_url' in upload_result:
                        print(f"Plik przesłany pomyślnie. URL pliku: {upload_result['download_url']}")
                        return True
                    else:
                        print("Odpowiedź nie zawiera 'download_url' w 'result'.")
                else:
                    print("Odpowiedź nie zawiera poprawnego 'result'.")
            else:
                print(f"Błąd podczas przesyłania pliku: {response.get('msg', 'Nieznany błąd')}")
        except Exception as e:
            print(f"Błąd podczas przesyłania pliku (próba {attempt + 1}): {e}")
        attempt += 1
        print(f"Ponawianie próby... ({attempt}/{max_retries})")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python upload_to_doodstream.py <nazwa_kanału> <ścieżka_do_pliku1> <ścieżka_do_pliku2> ...")
        sys.exit(1)

    channel_name = sys.argv[1]
    file_paths = sys.argv[2:]

    for file_path in file_paths:
        print(f"Przesyłanie pliku: {file_path}")
        success = upload_to_doodstream(file_path, channel_name)
        if not success:
            print(f"Błąd podczas przesyłania pliku: {file_path}")
            sys.exit(1)
