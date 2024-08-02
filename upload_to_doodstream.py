import os
import sys
from doodstream import DoodStream

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def upload_to_doodstream(file_path, max_retries=3):
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        return False

    attempt = 0
    while attempt < max_retries:
        try:
            response = d.local_upload(file_path)
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
