import requests
import re
import os
from urllib.parse import urlparse

# ========================= CONFIG =========================
INPUT_FILE = "input.txt"
OUTPUT_FILE = "playlist.m3u"
PATTERN = r"https://manifest\.googlevideo\.com/api/manifest/hls_variant.*?file/index\.m3u"

# =========================================================

def get_filename_from_url(url):
    """Genera un nombre de archivo seguro a partir del ID de YouTube."""
    parsed = urlparse(url)
    video_id = parsed.query.split("v=")[-1] if "v=" in parsed.query else parsed.path.split("/")[-1]
    return f"source_{video_id}.html"

def save_html(content, filename):
    abs_path = os.path.abspath(filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] Código fuente guardado en: {abs_path}")

def save_playlist(links):
    abs_path = os.path.abspath(OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for link in links:
            f.write(f"{link}\n")
    print(f"[INFO] Playlist guardada en: {abs_path}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] No existe {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("[ERROR] input.txt está vacío.")
        return

    print(f"[INFO] Encontradas {len(urls)} URLs en {INPUT_FILE}")

    all_links = []

    for url in urls:
        print(f"[INFO] Descargando código fuente: {url}")
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            response.raise_for_status()
            html = response.text

            filename = get_filename_from_url(url)
            save_html(html, filename)

            matches = re.findall(PATTERN, html)
            if matches:
                print(f"[OK] Fragmento encontrado en {url}")
                all_links.extend(matches)
            else:
                print(f"[WARN] No se encontró el fragmento en {url}")

        except requests.RequestException as e:
            print(f"[ERROR] No se pudo obtener {url}: {e}")

    if all_links:
        save_playlist(all_links)
    else:
        print("[INFO] No se encontraron enlaces en ninguna URL.")

if __name__ == "__main__":
    main()