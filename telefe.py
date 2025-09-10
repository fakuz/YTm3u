import requests

VIDEO_ID = "694564"
API_URL = f"https://telefe.com/Api/Videos/GetSourceUrl/{VIDEO_ID}/0/HLS?.m3u8"
OUTPUT_FILE = "telefe.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://telefe.com/"
}

def obtener_m3u8():
    r = requests.get(API_URL, headers=HEADERS)
    real_url = r.text.strip()  # respuesta cruda (el m3u8 con token)

    if not real_url.startswith("http"):
        raise ValueError(f"Respuesta inesperada: {real_url}")

    return real_url

def guardar_m3u8(url):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
        f.write(url + "\n")

if __name__ == "__main__":
    url = obtener_m3u8()
    guardar_m3u8(url)
    print(f"Archivo {OUTPUT_FILE} generado con éxito.")
