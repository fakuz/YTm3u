#!/usr/bin/env python3
import subprocess

CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u"

def get_hls_url(youtube_url):
    try:
        cmd = [
            "yt-dlp",
            "-g",
            "-f", "best",
            "--hls-prefer-ffmpeg",
            youtube_url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"[ERROR] yt-dlp fallo para {youtube_url}: {result.stderr}")
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
            else:
                print(f"[WARN] No se pudo extraer stream para {name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist)

    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
