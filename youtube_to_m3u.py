import asyncio
from playwright.async_api import async_playwright
import re
import time

# Lista de canales con su URL de YouTube
channels = {
    "TN": "https://www.youtube.com/watch?v=Uo-ziJhrTvI",
    "C5N": "https://www.youtube.com/watch?v=ArKbAx1K-2U",
    "A24": "https://www.youtube.com/watch?v=avly0uwZzOE",
    "Cronica": "https://www.youtube.com/watch?v=OLMiTr2OUeU",
    "Canal 26": "https://www.youtube.com/watch?v=5f__Ls4_VYQ"
}

async def get_stream_url(channel_name, youtube_url):
    print(f"Obteniendo URL para {channel_name}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(youtube_url)
        
        stream_url = None
        start_time = time.time()
        timeout = 30  # segundos
        
        # Escuchar las peticiones de red
        async def on_request(request):
            nonlocal stream_url
            url = request.url
            if "videoplayback?" in url and "mime=video" in url:
                stream_url = url
                print(f"✅ Encontrado para {channel_name}: {stream_url}")

        page.on("request", on_request)

        # Esperar hasta encontrar el enlace o agotar el tiempo
        while stream_url is None and (time.time() - start_time) < timeout:
            await asyncio.sleep(1)
        
        await browser.close()
        return stream_url

async def generate_playlist():
    playlist_lines = ["#EXTM3U"]
    for name, url in channels.items():
        stream_url = await get_stream_url(name, url)
        if stream_url:
            playlist_lines.append(f"#EXTINF:-1,{name}")
            playlist_lines.append(stream_url)
        else:
            print(f"❌ No se encontró stream para {name}")

    # Guardar en archivo
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))
    print("✅ Playlist actualizada correctamente (playlist.m3u)")

if __name__ == "__main__":
    asyncio.run(generate_playlist())
