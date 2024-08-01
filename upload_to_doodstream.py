import requests
import os
import sys

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

def upload_to_doodstream(file_path):
    if not DOODSTREAM_API_KEY:
        print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
        return False

    upload_url = 'https://doodapi.com/api/upload/server'
    headers = {
        'Authorization': f'Bearer {DOODSTREAM_API_KEY}',
    }

    # Pobierz URL do przesyłania
    response = requests.get(upload_url, headers=headers)
    if response.status_code != 200:
        print(f"Błąd podczas pobierania URL do przesyłania: {response.status_code}")
        return False

    upload_server = response.json()['result']

    # Prześlij plik
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(upload_server, files=files)

    if response.status_code == 200 and response.json()['status'] == 200:
        print(f"Plik przesłany pomyślnie. URL pliku: {response.json()['result']['download_url']}")
        return True
    else:
        print(f"Błąd podczas przesyłania pliku: {response.status_code}, {response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python upload_to_doodstream.py <ścieżka_do_pliku>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        sys.exit(1)
    
    success = upload_to_doodstream(file_path)
    if not success:
        sys.exit(1)
