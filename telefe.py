import requests
import json

# Lista de proxies Piped / Invidious
PIPED_API = "https://pipedapi.kavin.rocks"
INVIDIOUS_API = "https://vid.puffyan.us"

# Leer canales desde channels.txt
with open("channels.txt", "r", encoding="utf-8") as f:
    channels = [line.strip().split(",") for line in f if line.strip()]

playlist = "#EXTM3U\n"

for name, url in channels:
    video_id = url.split("v=")[-1]
    print(f"🔍 Buscando HLS para {name}...")

    hls_url = None

    # Intentar con Piped
    try:
        r = requests.get(f"{PIPED_API}/streams/{video_id}", timeout=10)
        data = r.json()
        if "hls" in data and data["hls"]:
            hls_url = data["hls"]
            print(f"✅ {name}: {hls_url}")
    except:
        print(f"⚠️ Error con Piped para {name}")

    # Intentar con Invidious si Piped falla
    if not hls_url:
        try:
            r = requests.get(f"{INVIDIOUS_API}/api/v1/videos/{video_id}", timeout=10)
            data = r.json()
            if "adaptiveFormats" in data:
                for fmt in data["adaptiveFormats"]:
                    if fmt.get("type", "").startswith("application/x-mpegURL"):
                        hls_url = fmt["url"]
                        print(f"✅ {name} (Invidious): {hls_url}")
                        break
        except:
            print(f"❌ No se pudo obtener {name}")

    if hls_url:
        playlist += f"#EXTINF:-1,{name}\n{hls_url}\n"
    else:
        print(f"❌ No se encontró stream para {name}")

# Guardar playlist
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(playlist)

print("✅ Playlist generada: playlist.m3u")
