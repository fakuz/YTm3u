import requests
import re

def obtener_url():
    api_url = "https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8"

    try:
        r = requests.get(api_url, timeout=10)
        # No usamos raise_for_status(), para no cortar si da 403
        texto = r.text

        # Regex flexible: captura cualquier URL con .m3u8
        match = re.search(r"https?://[^\s'\"]+\.m3u8[^\s'\"]*", texto)
        if match:
            return match.group(0)
        else:
            print("⚠️ No se encontró ningún link .m3u8 en la respuesta.")
            return None

    except Exception as e:
        print(f"❌ Error al consultar la API: {e}")
        return None

if __name__ == "__main__":
    url = obtener_url()
    if url:
        with open("telefe.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
            f.write(url + "\n")
        print(f"✅ Playlist generada con link: {url}")
    else:
        print("⚠️ No se generó el archivo M3U porque no hubo link válido.")