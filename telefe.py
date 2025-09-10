import requests

# ID del video de Telefe
VIDEO_ID = "694564"

# Endpoint de la API
API_URL = f"https://telefe.com/Api/Videos/GetSourceUrl/{VIDEO_ID}/0/HLS?.m3u8"

# Archivo de salida
OUTPUT_FILE = "telefe.m3u"

def obtener_m3u8():
    r = requests.get(API_URL)
    real_url = r.text.strip()  # La API devuelve directamente el link .m3u8

    if not real_url.startswith("http"):
        raise ValueError("No se encontró una URL válida en la respuesta.")

    return real_url

def guardar_m3u8(url):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
        f.write(url + "\n")

if __name__ == "__main__":
    url = obtener_m3u8()
    guardar_m3u8(url)
    print(f"Archivo {OUTPUT_FILE} generado con éxito: {url}")
