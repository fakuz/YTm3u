import datetime

# 🎯 Poné acá tu link directo (con token si hace falta)
url = "https://edge-mitelefe.akamaized.net/live/telefehd/index.m3u8"

if url:
    contenido = f"""#EXTM3U
#EXTINF:-1 tvg-logo="https://telefe.com/logo.png" group-title="Argentina", Telefe
{url}
"""
    with open("telefe.m3u", "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✅ Archivo M3U generado correctamente a las {datetime.datetime.now()}")
else:
    print("⚠️ No se generó el archivo M3U porque no hubo link en la variable 'url'")