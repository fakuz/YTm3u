#!/usr/bin/env python3
import re
import requests

CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u"

def extract_hls_url(html):
    # Busca con slashes escapados (YouTube suele usar \/)
    match = re.search(r'(https:\\/\\/manifest\.googlevideo\.com\\/[^"]+m3u8)', html)
    if match:
        return match.group(1).replace("\\/", "/")
    
    # Si no encuentra escapado, busca normal
    match = re.search(r'(https://manifest\.googlevideo\.com/[^"]+m3u8)', html)
    if match:
        return match.group(1)
    
    return None

def get_hls_url(youtube_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.youtube.com/"
        }
        response = requests.get(youtube_url, headers=headers, timeout=15)
        if response.status_code == 200:
            return extract_hls_url(response.text)
        else:
            print(f"[ERROR] HTTP {response.status_code} para {youtube_url}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def generate_playlist():
    playlist = "#EXTM3U\n"
    
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "|" not in line:
                continue
            name, url = line.split("|", 1)
            print(f"[INFO] Procesando {name}...")
            hls_url = get_hls_url(url)
            if hls_url:
                playlist += f'#EXTINF:-1,{name}\n{hls_url}\n'
                print(f"[OK] Stream encontrado para {name}")
            else:
                print(f"[WARN] No se encontró stream para {name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist)

    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
