import requests
import re

def obtener_url():
    api_url = "https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8"

    try:
        r = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"})
        texto = r.text

        # Buscar cualquier link que termine en .m3u8 (con token o sin)
        match = re.search(r"https?://[^\s'\"]+\.m3u8[^\s'\"]*", texto)
        if match:
            return match.group(0)
        else:
            print("⚠️ No se encontró ningún link .m3u8 en la respuesta.")
            return None

    except Exception as e:
        print(f"❌ Error al obtener desde la API de Telefe: {e}")
        return None


def generar_m3u(url):
    if not url:
        print("⚠️ No se generó el archivo M3U porque no hubo link válido.")
        return

    contenido = f"""#EXTM3U
#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe
{url}
"""
    with open("telefe.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    print("✅ Archivo telefe.m3u actualizado correctamente.")


if __name__ == "__main__":
    url = obtener_url()
    generar_m3u(url)