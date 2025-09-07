import requests
import time

INPUT_FILE = "links.txt"
OUTPUT_FILE = "playlist.m3u"
BASE_URL = "https://mobi.jawaltv.com/extras/youtube/"

def get_m3u8_link(youtube_url):
    try:
        response = requests.get(BASE_URL, params={"url": youtube_url}, timeout=15)
        if response.status_code == 200:
            link = response.text.strip()
            if link.startswith("https://manifest.googlevideo.com") and ".m3u8" in link:
                return link
            else:
                print(f"[WARN] Respuesta inesperada para {youtube_url}: {link}")
        else:
            print(f"[ERROR] Status {response.status_code} para {youtube_url}")
    except Exception as e:
        print(f"[ERROR] {e}")
    return None

def generate_playlist():
    print("[INFO] Generando playlist...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    playlist_lines = ['#EXTM3U']
    for line in lines:
        if "|" not in line:
            print(f"[WARN] Formato inválido en línea: {line}")
            continue

        nombre, youtube_url = line.split("|", 1)
        print(f"[INFO] Procesando: {nombre} ({youtube_url})")

        m3u8_link = get_m3u8_link(youtube_url)
        if m3u8_link:
            playlist_lines.append(f'#EXTINF:-1,{nombre}')
            playlist_lines.append(m3u8_link)
        else:
            print(f"[ERROR] No se pudo generar el link para {nombre}")

        time.sleep(2)  # Pausa para no saturar el servidor

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))

    print(f"[INFO] Playlist generada: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
