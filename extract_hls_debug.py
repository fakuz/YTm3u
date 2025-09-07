#!/usr/bin/env python3
import requests
import os

INPUT_FILE = "input.txt"
OUTPUT_FILE = "playlist.m3u"
START_TEXT = "https://manifest.googlevideo.com/api/manifest/hls_variant"
END_TEXT = "file/index.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

def extract_hls_variant(html):
    start = html.find(START_TEXT)
    if start == -1:
        return None
    end = html.find(END_TEXT, start)
    if end == -1:
        return None
    end += len(END_TEXT)
    return html[start:end]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] No se encontró el archivo {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("[ERROR] No hay URLs en input.txt")
        return

    session = requests.Session()
    session.headers.update(HEADERS)

    found_links = []

    for url in urls:
        print(f"[INFO] Descargando: {url}")
        video_id = url.split("v=")[-1]
        source_file = f"source_{video_id}.html"

        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()
            html = response.text

            with open(source_file, "w", encoding="utf-8") as src:
                src.write(html)
            print(f"[INFO] Código fuente guardado en {source_file}")

            link = extract_hls_variant(html)
            if link:
                print(f"[OK] Enlace encontrado: {link}")
                found_links.append(link)
            else:
                print(f"[WARN] No se encontró el fragmento en {url}")
        except Exception as e:
            print(f"[ERROR] Falló la descarga de {url}: {e}")

    if found_links:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u:
            m3u.write("#EXTM3U\n")
            for link in found_links:
                m3u.write("#EXTINF:-1, YouTube Stream\n")
                m3u.write(link + "\n")
        print(f"[INFO] Playlist guardada en {OUTPUT_FILE}")
    else:
        print("[INFO] No se encontraron enlaces en ninguna URL.")

if __name__ == "__main__":
    main()