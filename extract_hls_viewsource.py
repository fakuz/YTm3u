#!/usr/bin/env python3
import requests
import os

INPUT_FILE = "input.txt"
OUTPUT_FILE = "playlist.m3u"
SOURCE_FILE = "source.html"

START_TEXT = "https://manifest.googlevideo.com/api/manifest/hls_variant"
END_TEXT = "file/index.m3u"

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
        url = f.read().strip()

    if not url:
        print("[ERROR] El archivo input.txt está vacío.")
        return

    print(f"[INFO] Descargando código fuente: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        html = response.text

        # Guardar el código fuente completo
        with open(SOURCE_FILE, "w", encoding="utf-8") as src:
            src.write(html)
        print(f"[INFO] Código fuente guardado en {SOURCE_FILE}")

        # Buscar el enlace
        link = extract_hls_variant(html)

        if link:
            print(f"[OK] Enlace encontrado: {link}")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u:
                m3u.write("#EXTM3U\n")
                m3u.write("#EXTINF:-1, YouTube Stream\n")
                m3u.write(link + "\n")
            print(f"[INFO] Playlist guardada en {OUTPUT_FILE}")
        else:
            print("[INFO] No se encontró ningún enlace en el código fuente.")

    except requests.RequestException as e:
        print(f"[ERROR] No se pudo acceder a la URL: {e}")

if __name__ == "__main__":
    main()
