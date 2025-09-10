import requests

VIDEO_ID = "694564"
API_URL = f"https://telefe.com/Api/Videos/GetSourceUrl/{VIDEO_ID}/0/HLS?.m3u8"
OUTPUT_FILE = "telefe.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0 Safari/537.36"
}

def obtener_url():
    # 🚨 Solo pedimos la API, no validamos el link final
    r = requests.get(API_URL, headers=HEADERS)
    r.raise_for_status()  # solo valida la API de Telefe
    return r.text.strip()  # el cuerpo es la URL firmada

def guardar_m3u(url):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
        f.write(url + "\n")

if __name__ == "__main__":
    try:
        url = obtener_url()
        guardar_m3u(url)
        print("✅ M3U generado con éxito")
    except Exception as e:
        # ⚡️ Nunca debe mostrar un 403, solo errores reales de la API
        print(f"❌ Error al obtener desde la API de Telefe: {e}")