import requests
from bs4 import BeautifulSoup
import time
import json
import hashlib
import random

# Telegram ayarlarını buraya gir
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "CHAT_ID_HERE"

SEEN_HASHES_FILE = "seen_links.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram hatası:", e)

def hash_link(link):
    return hashlib.sha256(link.encode()).hexdigest()

def load_seen():
    try:
        with open(SEEN_HASHES_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(SEEN_HASHES_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_links():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "tr-TR,tr;q=0.9"
    }

    try:
        r = requests.get("https://www.tesla.com/tr_TR/inventory/new/my", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/tr_TR/inventory/new/view/"):
                full = "https://www.tesla.com" + href
                links.append(full)
        return links
    except Exception as e:
        print("İstek hatası:", e)
        return []

def check_tesla():
    print("Araç kontrolü başladı...")
    current = fetch_links()
    seen = load_seen()
    new = []

    for link in current:
        h = hash_link(link)
        if h not in seen:
            new.append(link)
            seen.add(h)

    if new:
        for l in new:
            print(f"Yeni araç bulundu: {l}")
            send_telegram(f"🚗 Yeni Tesla Aracı:\n{l}")
    else:
        print("Yeni araç bulunamadı.")

    save_seen(seen)

if __name__ == "__main__":
    import sys
    import random

    while True:
        try:
            check_tesla()
        except Exception as e:
            print("Genel hata:", e)
        wait = random.randint(48, 55)
        print(f"{wait} saniye sonra tekrar kontrol edilecek...")
        time.sleep(wait)