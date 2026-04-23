import os
from dotenv import load_dotenv

# Załaduj zmienne z pliku .env
load_dotenv()

# Lista stacji radiowych
RADIO_STATIONS = {
    1: {"name": "Radioparty - Kanał Główny", "url": "https://s2.radioparty.pl:7000/stream?nocache=5782"},
    2: {"name": "Radioparty - DJ Mixes", "url": "https://radioparty.pl:8888/djmixes"},
    3: {"name": "RMF MAXX", "url": "http://31.192.216.10:8000/rmf_maxxx"},
    4: {"name": "ESKA Siedlce", "url": "https://ic2.smcdn.pl/2060-1.mp3"},
    5: {"name": "Radio ZET", "url": "https://n-11-23.dcs.redcdn.pl/sc/o2/Eurozet/live/audio.livx?audio=5"},
    6: {"name": "Radio Zet Dance", "url": "https://zt05.cdn.eurozet.pl/ZETDAN.mp3?redirected=05/"},
    7: {"name": "Radio Zet Party", "url": "http://zt04.cdn.eurozet.pl/ZETPAR.mp3"},
    8: {"name": "Open FM - Vixa", "url": "https://stream-cdn-1.open.fm/OFM207/ngrp:standard/playlist.m3u8"},
    9: {"name": "Open FM - Dance", "url": "https://stream-cdn-1.open.fm/OFM160/ngrp:standard/playlist.m3u8"},
    10: {"name": "Open FM - Do Auta", "url": "https://stream-cdn-1.open.fm/OFM163/ngrp:standard/playlist.m3u8"},
    11: {"name": "Open FM - 500 Party Hits", "url": "https://stream-cdn-1.open.fm/OFM169/ngrp:standard/playlist.m3u8"},
}

# Konfiguracja bota pobierana z .env
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
