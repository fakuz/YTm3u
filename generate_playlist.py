#!/usr/bin/env python3
import requests
import os

INPUT_FILE = "links.txt"
OUTPUT_FILE = "playlist.m3u"
BASE_URL = "https://mobi.jawaltv.com/extras/youtube/"

def get_m3u8_link(youtube_url):
    try:
        params = {"url": youtube_url}
        response = requests.get(BASE_URL, params=params, timeout=15)

        if response.status_code == 200:
            if "googlevideo.com" in response.text and ".m3u8" in response.text:
                start = response.text.find("https://manifest.googlevideo.com")
                end = response.text.find(".m3u8", start) + 5
                return response.text[start:end]
            else:
                print(f"[WARN] No se encontró link .m3u8 para {youtube_url}")
        else:
            print(f"[ERROR] Status {response.status_code} para {youtube_url}")
    except Exception as e:
        print(f"[ERROR] {e}")
    return None

def generate_playlist():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] No se encontró {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    playlist_lines = ["#EXTM3U"]

    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            name, logo, url = parts
        elif len(parts) == 2:
            name, url = parts
            logo = ""
        else:
            name = "Canal"
            logo = ""
            url = line.strip()

        m3u8 = get_m3u8_link(url)
        if m3u8:
            if logo:
                playlist_lines.append(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{m3u8}')
            else:
                playlist_lines.append(f'#EXTINF:-1,{name}\n{m3u8}')
        else:
            print(f"[ERROR] No se pudo generar el link para {name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))

    print(f"[INFO] Playlist actualizada con {len(lines)} canales.")

if __name__ == "__main__":
    generate_playlist()
