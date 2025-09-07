#!/usr/bin/env python3
import subprocess

INPUT_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u8"

def get_streamlink_url(url):
    try:
        result = subprocess.run(
            ["streamlink", "--stream-url", url, "best"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except Exception:
        return None

def get_ytdlp_url(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "-g", "-f", "best", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
        return None
    except Exception:
        return None

def get_hls_url(youtube_url):
    # Primero Streamlink, si falla, yt-dlp
    hls = get_streamlink_url(youtube_url)
    if not hls:
        print(f"[WARN] Streamlink falló para {youtube_url}, intentando yt-dlp...")
        hls = get_ytdlp_url(youtube_url)
    return hls

def generate_m3u8():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for line in lines:
            if line.strip():
                parts = line.strip().split("|")
                if len(parts) < 2:
                    continue
                name = parts[0]
                url = parts[1]
                logo = parts[2] if len(parts) >= 3 else ""

                print(f"[INFO] Procesando {name}...")
                hls_url = get_hls_url(url)
                if hls_url:
                    if logo:
                        out.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{hls_url}\n')
                    else:
                        out.write(f'#EXTINF:-1,{name}\n{hls_url}\n')
                else:
                    print(f"[ERROR] No se pudo obtener stream para {name}")

if __name__ == "__main__":
    generate_m3u8()
    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")
