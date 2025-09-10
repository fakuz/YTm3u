import requests
import re
import os

def obtener_url():
    api_url = "https://telefe.com/Api/Videos/GetSourceUrl/694564/0/HLS?.m3u8"

    try:
        r = requests.get(api_url, timeout=10)
        texto = r.text

        # Buscar cualquier URL que termine en .m3u8
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
    ultimo_file = "ultimo.txt"

    # Leer último link válido si existe
    ultimo_url = None
    if os.path.exists(ultimo_file):
        with open(ultimo_file, "r", encoding="utf-8") as f:
            ultimo_url = f.read().strip()

    if url:
        # Si hay nuevo link válido → actualizar archivo
        with open(ultimo_file, "w", encoding="utf-8") as f:
            f.write(url)
        print(f"✅ Nuevo link obtenido: {url}")
    else:
        # Si no hay → usar el último guardado
        url = ultimo_url
        if url:
            print(f"♻️ Usando último link válido: {url}")
        else:
            print("⚠️ No se encontró link y no hay histórico.")

    # Generar siempre el M3U
    with open("telefe.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write('#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe\n')
        if url:
            f.write(url + "\n")
        else:
            f.write("# No se pudo obtener ni recuperar un link válido\n")