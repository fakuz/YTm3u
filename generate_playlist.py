#!/usr/bin/env python3
import subprocess

INPUT_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u8"

def get_hls_url(youtube_url):
    try:
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
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def generate_m3u8():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write('#EXTM3U\n')
        for line in lines:
            if line.strip():
                # Ahora solo aceptamos: Nombre|URL|Logo
                parts = line.strip().split("|")
                if len(parts) < 2:
                    continue
                name = parts[0]
                url = parts[1]
                logo = parts[2] if len(parts) >= 3 else ""

                print(f"[INFO] Procesando {name}...")
                hls_url = get_hls_url(url)
                if hls_url:
                    out.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{hls_url}\n')

if __name__ == "__main__":
    generate_m3u8()
    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")
