import os
import csv
from datetime import datetime
import requests

def read_csv(file_path):
    """
    Reads a semicolon-separated CSV file (French format) and returns its content as a list of dictionaries.

    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            return list(reader)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return []
    

def download_file(url, save_dir="./"):
    """
    Downloads a file from a given URL and saves it with today's date in the filename.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(save_dir, f"fichier_{today_str}.csv")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Fichier téléchargé avec succès : {file_path}")
        return file_path
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier : {e}")
        return None
    
    