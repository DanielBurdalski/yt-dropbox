import requests
import os
import sys
import json

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

def upload_to_doodstream(file_path):
    if not DOODSTREAM_API_KEY:
        print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
        return False

    upload_url = 'https://doodapi.com/api/upload/server'
    headers = {
        'api_key': DOODSTREAM_API_KEY,
    }

    # Pobierz URL do przesyłania
    try:
        response = requests.get(upload_url, headers=headers)
        response.raise_for_status()  # Zgłosi wyjątek dla kodów błędów HTTP
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania URL do przesyłania: {e}")
        print(f"Pełna odpowiedź: {response.text}")
        return False

    try:
        result = response.json()
    except json.JSONDecodeError:
        print(f"Nie udało się zdekodować odpowiedzi JSON. Odpowiedź serwera: {response.text}")
        return False

    upload_server = result.get('result')
    if not upload_server:
        print(f"Nie udało się pobrać URL serwera do przesyłania. Pełna odpowiedź: {result}")
        return False

    # Prześlij plik
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'api_key': DOODSTREAM_API_KEY}
            response = requests.post(upload_server, files=files, data=data)
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas przesyłania pliku: {e}")
        print(f"Pełna odpowiedź: {response.text}")
        return False

    try:
        result = response.json()
    except json.JSONDecodeError:
        print(f"Nie udało się zdekodować odpowiedzi JSON po przesłaniu. Odpowiedź serwera: {response.text}")
        return False

    if result.get('status') == 200:
        print(f"Plik przesłany pomyślnie. URL pliku: {result['result']['download_url']}")
        return True
    else:
        print(f"Błąd podczas przesyłania pliku: {result.get('msg')}")
        print(f"Pełna odpowiedź: {result}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python upload_to_doodstream.py <ścieżka_do_pliku>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        sys.exit(1)
    
    print(f"Używany klucz API: {DOODSTREAM_API_KEY[:5]}...{DOODSTREAM_API_KEY[-5:]} (pierwsze i ostatnie 5 znaków)")
    success = upload_to_doodstream(file_path)
    if not success:
        sys.exit(1)
