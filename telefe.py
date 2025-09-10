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
    r.raise_for_status()
    return r.text.strip()  # La API devuelve directamente la URL firmada

def guardar_m3u8(url):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
        f.write(url + "\n")

if __name__ == "__main__":
    try:
        url = obtener_m3u8()
        if url.startswith("http"):
            guardar_m3u8(url)
            print(f"✅ Archivo {OUTPUT_FILE} actualizado con éxito.")
        else:
            print("⚠️ La API no devolvió un link válido. No se actualizó el archivo.")
    except Exception as e:
        print(f"❌ Error al obtener el link: {e}")