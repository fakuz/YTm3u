import asyncio
from playwright.async_api import async_playwright
import time
import re
from datetime import datetime

def load_channels(filename="channels.txt"):
    channels = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                name, url = line.strip().split("|", 1)
                channels[name] = url
    return channels

async def get_stream_url(channel_name, youtube_url):
    print(f"🔍 Buscando stream para {channel_name}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(youtube_url)
        
        stream_url = None
        start_time = time.time()
        timeout = 30
        
        async def on_request(request):
            nonlocal stream_url
            url = request.url
            if ".m3u8" in url:
                stream_url = url
            elif "videoplayback?" in url and "mime=video" in url:
                if not stream_url:
                    stream_url = url

        page.on("request", on_request)

        while stream_url is None and (time.time() - start_time) < timeout:
            await asyncio.sleep(1)
        
        await browser.close()
        return stream_url

def extract_expire(url):
    match = re.search(r"expire=(\d+)", url)
    if match:
        timestamp = int(match.group(1))
        expire_time = datetime.utcfromtimestamp(timestamp)
        return expire_time
    return None

async def generate_playlist():
    channels = load_channels()
    playlist_lines = ["#EXTM3U"]
    log_lines = []
    
    for name, url in channels.items():
        stream_url = await get_stream_url(name, url)
        if stream_url:
            expire_time = extract_expire(stream_url)
            expire_info = f"Expira: {expire_time} UTC" if expire_time else "Expira: Desconocido"
            print(f"✅ {name}: {stream_url}")
            print(f"   {expire_info}")
            
            playlist_lines.append(f"#EXTINF:-1,{name}")
            playlist_lines.append(stream_url)
            
            log_lines.append(f"{name} -> {expire_info}")
        else:
            print(f"❌ No se encontró stream para {name}")
            log_lines.append(f"{name} -> No encontrado")
    
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))
    
    with open("last_update.txt", "w", encoding="utf-8") as f:
        f.write(f"Última actualización: {datetime.utcnow()} UTC\n")
        f.write("\n".join(log_lines))
    
    print("✅ Playlist actualizada correctamente (playlist.m3u)")
    print("📄 Log generado en last_update.txt")

if __name__ == "__main__":
    asyncio.run(generate_playlist())
