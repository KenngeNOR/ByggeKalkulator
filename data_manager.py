import json
import os

DB_FILE = 'materialer.json'

def last_materialer():
    """Laster materialer fra JSON. Hvis filen ikke finnes, returnerer vi en tom dict."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def lagre_materialer(data):
    """Lagrer oppdatert material-dict til JSON-filen."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)