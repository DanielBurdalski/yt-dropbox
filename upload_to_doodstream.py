import os
import sys
from doodstream import DoodStream

# Klucz API DOODSTREAM (ustaw jako zmienną środowiskową)
DOODSTREAM_API_KEY = os.getenv('DOODSTREAM_API_KEY')

if not DOODSTREAM_API_KEY:
    print("Brak klucza API DOODSTREAM. Ustaw zmienną środowiskową DOODSTREAM_API_KEY.")
    sys.exit(1)

d = DoodStream(DOODSTREAM_API_KEY)

def upload_to_doodstream(file_path):
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje.")
        return False

    try:
        response = d.local_upload(file_path)
        if response['status'] == 200:
            print(f"Plik przesłany pomyślnie. URL pliku: {response['result']['download_url']}")
            return True
        else:
            print(f"Błąd podczas przesyłania pliku: {response.get('msg')}")
            return False
    except Exception as e:
        print(f"Błąd podczas przesyłania pliku: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python upload_to_doodstream.py <ścieżka_do_pliku>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = upload_to_doodstream(file_path)
    if not success:
        sys.exit(1)
