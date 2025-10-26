import os
from dotenv import load_dotenv

# Versuche, die .env-Datei zu laden
load_dotenv()

# Hole den Schlüssel aus der Umgebung
api_key = os.getenv("GEMINI_API_KEY")

# Überprüfe, ob es geklappt hat
if api_key:
    print("\n✅ Juhu! Der Schlüssel wurde erfolgreich aus der .env-Datei geladen.")
    print("Die ersten 5 Zeichen sind:", api_key[:5] + "...")
else:
    print("\n❌ Fehler! Das Skript konnte die .env-Datei nicht finden oder lesen.")
    print("Bitte überprüfe, ob die Datei im richtigen Ordner liegt und '.env' heißt.")