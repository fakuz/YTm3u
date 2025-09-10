import re
from pathlib import Path

# Simulación: acá iría el contenido real de la API de Telefe
respuesta_api = """
https://telefeappmitelefe1.akamaized.net/hls/live/2037985/appmitelefe/TOK/master.m3u8?hdnea=st=1757469189~exp=1757476389~acl=/hls/live/2037985/appmitelefe/TOK/*~hmac=fae55fd45c45757f6fca4238e8598f0d9ff5cf0efadde6b572374d08ccc9674d
"""

# Buscar cualquier URL que termine en .m3u8 (aunque tenga token después)
match = re.search(r"https://[^\s]+\.m3u8[^\s]*", respuesta_api)

if match:
    link = match.group(0).strip()
    contenido_m3u = f"""#EXTM3U
#EXTINF:-1 tvg-id="telefe" tvg-name="Telefe" group-title="Argentina",Telefe
{link}
"""
    Path("telefe.m3u").write_text(contenido_m3u, encoding="utf-8")
    print("✅ Archivo telefe.m3u generado con link válido")
else:
    print("⚠️ No se encontró ningún link .m3u8 en la respuesta.")