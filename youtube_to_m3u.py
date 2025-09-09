import subprocess

# URL del canal o transmisión en vivo
YOUTUBE_URL = "https://www.youtube.com/watch?v=XXXXXXXXXXX"

# Nombre del archivo de salida
OUTPUT_FILE = "playlist.m3u"

def get_hls_url():
    # Ejecutar yt-dlp para obtener el enlace HLS
    cmd = ["yt-dlp", "-g", "-f", "b", YOUTUBE_URL]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def generate_m3u(hls_url):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1 tvg-id=\"ytlive\" tvg-name=\"YouTube Live\", YouTube Live\n")
        f.write(hls_url + "\n")

if __name__ == "__main__":
    hls_url = get_hls_url()
    if hls_url:
        generate_m3u(hls_url)
        print("Archivo playlist.m3u generado con éxito.")
    else:
        print("Error: no se pudo obtener el enlace HLS.")
