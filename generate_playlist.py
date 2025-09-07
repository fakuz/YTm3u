#!/usr/bin/env python3
import subprocess
import sys
import os

# Lista de videos de YouTube que quieres extraer
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=XXXXXXX",
    "https://www.youtube.com/watch?v=YYYYYYY"
]

OUTPUT_FILE = "playlist.m3u8"

def get_hls_url(youtube_url):
    try:
        # Ejecutar streamlink para obtener la URL HLS en la mejor calidad
        result = subprocess.run(
            ["streamlink", "--stream-url", youtube_url, "best"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"[ERROR] No se pudo extraer stream de {youtube_url}")
            print(result.stderr)
            return None

    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def generate_m3u8(urls):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for idx, url in enumerate(urls):
            if url:
                f.write(f'#EXTINF:-1, Canal {idx+1}\n{url}\n')

if __name__ == "__main__":
    streams = []
    for yt in YOUTUBE_URLS:
        print(f"[INFO] Extrayendo stream de {yt}...")
        hls = get_hls_url(yt)
        streams.append(hls)

    generate_m3u8(streams)
    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")
