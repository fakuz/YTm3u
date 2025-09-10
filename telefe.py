import requests

VIDEO_ID = "694564"
API_URL = f"https://telefe.com/Api/Videos/GetSourceUrl/{VIDEO_ID}/0/HLS?.m3u8"
OUTPUT_FILE = "telefe.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://telefe.com/"
}

def obtener_url():
    r = requests.get(API_URL, headers=HEADERS)
    r.raise_for_status()
    return r.text.strip()   # La API devuelve el link firmado de Akamai

def guardar_m3u(url):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
        f.write(url + "\n")

if __name__ == "__main__":
    url = obtener_url()
    if url.startswith("http"):
        guardar_m3u(url)
        print(f"✅ Link guardado en {OUTPUT_FILE}: {url}")
    else:
        print("⚠️ La API no devolvió una URL válida, no se actualizó el archivo.")