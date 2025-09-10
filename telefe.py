import requests
import re

API_URL = "https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8"

def obtener_url():
    try:
        r = requests.get(API_URL, timeout=10)
        texto = r.text.strip()

        match = re.search(r"https://[^\s\"']+\.m3u8[^\s\"']*", texto)
        if match:
            return match.group(0)
        else:
            print("⚠️ No se encontró ningún link .m3u8 en la respuesta.")
            return None

    except Exception as e:
        print(f"❌ Error al obtener desde la API de Telefe: {e}")
        return None

if __name__ == "__main__":
    url = obtener_url()
    if url:
        with open("telefe.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
            f.write(url + "\n")
        print("✅ Archivo telefe.m3u actualizado con éxito.")
    else:
        print("⚠️ No se generó el archivo M3U porque no hubo link válido.")