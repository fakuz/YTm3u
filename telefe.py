import datetime

def obtener_url():
    # 🎯 Acá iría la lógica de extracción (API, scraping, etc.)
    # Por ahora lo dejamos fijo como ejemplo:
    return "https://telefeappmitelefe1.akamaized.net/hls/live/2037985/appmitelefe/TOK/master.m3u8?hdnea=st=1757469189~exp=1757476389~acl=/hls/live/2037985/appmitelefe/TOK/*~hmac=fae55fd45c45757f6fca4238e8598f0d9ff5cf0efadde6b572374d08ccc9674d"

url = obtener_url()

if url and url.endswith(".m3u8"):
    contenido = f"""#EXTM3U
#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe
{url}
"""
    with open("telefe.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✅ Archivo M3U generado correctamente a las {datetime.datetime.now()}")
else:
    print("⚠️ No se generó el archivo M3U porque no hubo link válido.")