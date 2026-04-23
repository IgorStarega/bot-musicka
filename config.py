import os
import requests
from dotenv import load_dotenv

# Załaduj zmienne z pliku .env
load_dotenv()

def get_radio_stations():
    """Pobiera stacje radiowe z API i usuwa te bez URL."""
    try:
        url_api = "https://radyjko.mordorek.dev/api/stations"
        response = requests.get(url_api, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        stations = {}
        for item in data:
            # Pomiń stacje OpenFM bez bezpośredniego URL (wymagałyby dodatkowej logiki)
            # Jeśli URL jest None, próbujemy zbudować go dla OpenFM
            url = item.get("url")
            if not url and item.get("isOpenFM") == 1:
                url = f"https://stream-cdn-1.open.fm/OFM{item['openFmId']}/ngrp:standard/playlist.m3u8"
            
            if url:
                stations[item["id"]] = {
                    "name": item["name"],
                    "url": url.strip()
                }
        return stations
    except Exception as e:
        print(f"Błąd API Radiowego: {e}")
        return {
            130: {"name": "RMF FM", "url": "https://rs6-krk2.rmfstream.pl/rmf_fm"},
            170: {"name": "Radio ZET", "url": "https://27943.live.streamtheworld.com/RADIO_ZETAAC.aac?dist=zet"}
        }

# Lista stacji radiowych pobierana dynamicznie
RADIO_STATIONS = get_radio_stations()

# Konfiguracja bota pobierana z .env
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
