"""
User Storage System - v1.3.0
Zarządzanie ulubionych, historii i statystyk użytkownika
"""

import json
import os
from datetime import datetime
import logging

logger = logging.getLogger('MusicBot')

STORAGE_DIR = "config/user_data"
USERS_FILE = f"{STORAGE_DIR}/users.json"

def ensure_storage_dir():
    """Utworz folder jeśli nie istnieje"""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
        logger.info(f"✅ Utworzono folder: {STORAGE_DIR}")

def load_users():
    """Załaduj dane użytkowników z JSON"""
    ensure_storage_dir()
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Błąd ładowania users.json: {e}")
            return {}
    return {}

def save_users(users):
    """Zapisz dane użytkowników do JSON"""
    ensure_storage_dir()
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Błąd zapisywania users.json: {e}")

def get_user_data(user_id):
    """Pobierz dane użytkownika (lub utwórz nowego)"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            "id": user_id,
            "favorites": [],
            "history": [],
            "stats": {
                "total_played": 0,
                "skip_count": 0,
                "favorite_count": 0,
                "created_at": datetime.now().isoformat()
            }
        }
        save_users(users)
    
    return users[user_id_str], users

def add_favorite(user_id, track_url, track_title):
    """Dodaj utwór do ulubionych"""
    user_data, users = get_user_data(user_id)
    
    # Sprawdzić czy już w ulubionych
    for fav in user_data["favorites"]:
        if fav["url"] == track_url:
            return False  # Już tam jest
    
    user_data["favorites"].append({
        "url": track_url,
        "title": track_title,
        "added_at": datetime.now().isoformat()
    })
    
    user_data["stats"]["favorite_count"] = len(user_data["favorites"])
    save_users(users)
    logger.info(f"⭐ Dodano do ulubionych: {track_title} (user: {user_id})")
    return True

def remove_favorite(user_id, track_url):
    """Usuń utwór z ulubionych"""
    user_data, users = get_user_data(user_id)
    
    original_count = len(user_data["favorites"])
    user_data["favorites"] = [f for f in user_data["favorites"] if f["url"] != track_url]
    
    if len(user_data["favorites"]) < original_count:
        user_data["stats"]["favorite_count"] = len(user_data["favorites"])
        save_users(users)
        return True
    
    return False

def get_favorites(user_id):
    """Pobierz ulubione użytkownika"""
    user_data, _ = get_user_data(user_id)
    return user_data["favorites"]

def add_to_history(user_id, track_url, track_title):
    """Dodaj utwór do historii"""
    user_data, users = get_user_data(user_id)
    
    user_data["history"].insert(0, {
        "url": track_url,
        "title": track_title,
        "played_at": datetime.now().isoformat()
    })
    
    # Trzymaj tylko ostatnie 50 utworów w historii
    if len(user_data["history"]) > 50:
        user_data["history"] = user_data["history"][:50]
    
    user_data["stats"]["total_played"] += 1
    save_users(users)
    return True

def get_history(user_id, limit=20):
    """Pobierz historię użytkownika"""
    user_data, _ = get_user_data(user_id)
    return user_data["history"][:limit]

def get_user_stats(user_id):
    """Pobierz statystyki użytkownika"""
    user_data, _ = get_user_data(user_id)
    return user_data["stats"]

def increment_skip_count(user_id):
    """Zwiększ licznik skipów"""
    user_data, users = get_user_data(user_id)
    user_data["stats"]["skip_count"] += 1
    save_users(users)

# Inicjacja przy importie
ensure_storage_dir()
