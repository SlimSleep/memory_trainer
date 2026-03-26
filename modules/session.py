import json
import os

from config import DATA_DIR

SESSION_FILE = os.path.join(DATA_DIR, 'session.json')


def ensure_data_dir():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def save_session(username):
    ensure_data_dir()
    try:
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump({'username': username}, f, ensure_ascii=False)
    except Exception as e:
        print(f"⚠ Не удалось сохранить сессию: {e}")


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('username')
    except Exception as e:
        print(f"⚠ Не удалось загрузить сессию: {e}")
        return None


def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception as e:
        print(f"⚠ Не удалось удалить сессию: {e}")
