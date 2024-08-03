import os
import sys
import requests

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

DOODSTREAM_API_URL = "https://doodapi.com/api"

def create_folder(channel_name):
    url = f"{DOODSTREAM_API_URL}/folder/create"
    params = {
        'key': DOODSTREAM_API_KEY,
        'name': channel_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 200:
            print(f"Folder '{channel_name}' stworzony. Odpowiedź API: {result}")
            return result['result']['fld_id']
        else:
            print(f"Błąd podczas tworzenia folderu '{channel_name}': {result.get('msg')}")
    else:
        print(f"Błąd HTTP: {response.status_code}")
    return None

def get_or_create_folder_id(channel_name):
    url = f"{DOODSTREAM_API_URL}/folders"
    params = {'key': DOODSTREAM_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 200:
            for folder in result['result']:
                if folder['name'] == channel_name:
                    print(f"Folder '{channel_name}' już istnieje. ID folderu: {folder['fld_id']}")
                    return folder['fld_id']
            return create_folder(channel_name)
        else:
            print(f"Błąd podczas pobierania listy folderów: {result.get('msg')}")
    else:
        print(f"Błąd HTTP: {response.status_code}")
    return None

def upload_to_doodstream(file_path, max_retries=3):
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        return False

    # Wyodrębnianie nazwy kanału z nazwy pliku
    file_name = os.path.basename(file_path)
    channel_name = file_name.split('-')[0]

    folder_id = get_or_create_folder_id(channel_name)
    if not folder_id:
        print(f"Nie udało się uzyskać ID folderu dla '{channel_name}'.")
        return False

    attempt = 0
    while attempt < max_retries:
        try:
            url = f"{DOODSTREAM_API_URL}/upload/url"
            params = {
                'key': DOODSTREAM_API_KEY,
                'url': file_path,
                'fld_id': folder_id,
                'new_title': file_name
            }
            response = requests.get(url, params=params)
            print(f"Odpowiedź API (próba {attempt + 1}): {response.json()}")

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 200:
                    if 'result' in result and len(result['result']) > 0:
                        upload_result = result['result'][0]
                        if 'download_url' in upload_result:
                            print(f"Plik przesłany pomyślnie. URL pliku: {upload_result['download_url']}")
                            return True
                        else:
                            print("Odpowiedź nie zawiera 'download_url' w 'result'.")
                    else:
                        print("Odpowiedź nie zawiera poprawnego 'result'.")
                else:
                    print(f"Błąd podczas przesyłania pliku: {result.get('msg', 'Nieznany błąd')}")
            else:
                print(f"Błąd HTTP: {response.status_code}")
        except Exception as e:
            print(f"Błąd podczas przesyłania pliku (próba {attempt + 1}): {e}")

        attempt += 1
        print(f"Ponawianie próby... ({attempt}/{max_retries})")

    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python upload_to_doodstream.py <ścieżka_do_pliku1> <ścieżka_do_pliku2> ...")
        sys.exit(1)

    file_paths = sys.argv[1:]

    for file_path in file_paths:
        print(f"Przesyłanie pliku: {file_path}")
        success = upload_to_doodstream(file_path)
        if not success:
            print(f"Błąd podczas przesyłania pliku: {file_path}")
            sys.exit(1)
