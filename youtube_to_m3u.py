import subprocess

CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u"

def load_channels():
    channels = {}
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                name, url = line.strip().split("|", 1)
                channels[name] = url
    return channels

def get_hls_link(url):
    cmd = ["yt-dlp", "-g", "-f", "best", url]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def generate_m3u(channels):
    content = "#EXTM3U\n"
    for name, url in channels.items():
        print(f"Obteniendo link para {name}...")
        link = get_hls_link(url)
        if link:
            content += f'#EXTINF:-1 tvg-name="{name}" group-title="YouTube",{name}\n{link}\n'
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    channels = load_channels()
    generate_m3u(channels)
    print("✅ Playlist actualizada.")
