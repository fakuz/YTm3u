import requests
import re

API_URL = "https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8"

def obtener_url():
    try:
        r = requests.get(API_URL, timeout=10)
        texto = r.text.strip()

        # Captura cualquier URL https:// que aparezca en la respuesta
        match = re.search(r"https://[^\s\"']+", texto)
        if match:
            return match.group(0)
        else:
            print("⚠️ No se encontró ningún link en la respuesta.")
            return None

    except Exception as e:
        print(f"❌ Error al obtener desde la API de Telefe: {e}")
        return None

def guardar_m3u(url):
    contenido = f"""#EXTM3U
#EXTINF:-1 tvg-id="Telefe" tvg-name="Telefe" group-title="Argentina" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Telefe_logo_2018.svg/1200px-Telefe_logo_2018.svg.png",Telefe
{url}
"""
    with open("telefe.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    print("✅ Archivo telefe.m3u actualizado.")

if __name__ == "__main__":
    url = obtener_url()
    if url:
        guardar_m3u(url)
    else:
        print("⚠️ No se generó el archivo M3U porque no hubo link válido.")