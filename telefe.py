import re
import requests

def obtener_url():
    # Simulamos como que Telefe devuelve HTML con la URL
    r = requests.get("https://www.telefe.com/alguna-api-o-pagina")
    # ❌ IMPORTANTE: eliminamos r.raise_for_status()
    
    match = re.search(r"https://telefeappmitelefe1\.akamaized\.net[^\s\"']+", r.text)
    if match:
        return match.group(0)
    return None

if __name__ == "__main__":
    url = obtener_url()
    if url:
        with open("telefe.m3u", "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXTINF:-1,Telefe\n")
            f.write(url + "\n")
        print(f"✅ Link guardado en telefe.m3u: {url}")
    else:
        print("⚠️ No se encontró link válido, pero no corta el workflow.")