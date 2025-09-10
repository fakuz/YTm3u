import requests
import re

URL_API = "https://edge-mitelefe.akamaized.net/live/telefehd/index.m3u8"

def obtener_m3u8():
    try:
        r = requests.get(URL_API, timeout=10)
        texto = r.text
        # Buscar cualquier URL que tenga .m3u8 (aunque tenga ?...)
        match = re.search(r"https://[^\s\"']+\.m3u8[^\s\"']*", texto)
        if match:
            return match.group(0)
    except Exception as e:
        print(f"⚠️ Error al obtener desde la API: {e}")
    return None

if __name__ == "__main__":
    url = obtener_m3u8()
    if url:
        with open("telefe.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("#EXTINF:-1,Telefe\n")
            f.write(url + "\n")
        print(f"✅ Guardado link válido: {url}")
    else:
        print("⚠️ No se encontró ningún link válido.")