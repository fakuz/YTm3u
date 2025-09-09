import subprocess

# Lista de canales
CHANNELS = {
    # "TN": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
    # "C5N": "https://www.youtube.com/watch?v=XXXXXXXXXXX"
}

OUTPUT_FILE = "playlist.m3u"

def get_hls_link(url):
    cmd = ["yt-dlp", "-g", "-f", "best", url]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def generate_m3u():
    content = "#EXTM3U\n"
    for name, url in CHANNELS.items():
        print(f"Obteniendo link para {name}...")
        link = get_hls_link(url)
        if link:
            content += f'#EXTINF:-1 tvg-name="{name}" group-title="YouTube",{name}\n{link}\n'
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    generate_m3u()
    print("✅ Playlist actualizada.")
