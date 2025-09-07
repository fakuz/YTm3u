#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

INPUT_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u8"

async def get_hls_url(playwright, youtube_url):
    browser = await playwright.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    context = await browser.new_context()
    page = await context.new_page()

    hls_url = None

    async def handle_request(request):
        nonlocal hls_url
        if "manifest.googlevideo.com/api/manifest/hls_variant" in request.url:
            # Asegurar que sea la versión con todas las calidades
            if "playlist_type=LIVE" in request.url or "playlist_type=DVR" in request.url:
                hls_url = request.url

    context.on("request", handle_request)

    print(f"[INFO] Abriendo {youtube_url}")
    await page.goto(youtube_url)
    
    # Iniciar reproducción forzada
    try:
        await page.click('button[aria-label="Reproducir"]', timeout=5000)
    except:
        pass  # Si ya está reproduciendo, ignoramos

    await page.evaluate("""
        () => {
            const video = document.querySelector('video');
            if (video) {
                video.muted = true;
                video.play();
            }
        }
    """)

    # Esperar hasta 30s o hasta que aparezca el HLS
    for _ in range(30):
        if hls_url:
            break
        await asyncio.sleep(1)

    await browser.close()
    return hls_url

async def generate_m3u8():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    async with async_playwright() as p:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")
            for line in lines:
                if line.strip():
                    parts = line.strip().split("|")
                    if len(parts) < 2:
                        continue
                    name = parts[0]
                    url = parts[1]
                    logo = parts[2] if len(parts) >= 3 else ""

                    print(f"[INFO] Procesando {name}...")
                    hls_url = await get_hls_url(p, url)
                    if hls_url:
                        print(f"[OK] {name} -> {hls_url}")
                        if logo:
                            out.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{hls_url}\n')
                        else:
                            out.write(f'#EXTINF:-1,{name}\n{hls_url}\n')
                    else:
                        print(f"[ERROR] No se encontró stream para {name}")

    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(generate_m3u8())
