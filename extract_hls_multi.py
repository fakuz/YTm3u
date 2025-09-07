import asyncio
from playwright.async_api import async_playwright

INPUT_FILE = "input.txt"
OUTPUT_FILE = "hls_links.txt"
M3U_FILE = "playlist.m3u"

async def process_url(playwright, url, video_id):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    print(f"[INFO] Procesando URL: {url}")
    links = []

    def handle_response(response):
        u = response.url
        if "manifest.googlevideo.com/api/manifest/hls_variant" in u:
            links.append(u)

    page.on("response", handle_response)

    await page.goto(url, wait_until="domcontentloaded")

    # Esperar hasta que aparezca el enlace o máximo 15s
    for _ in range(30):
        if links:
            break
        await asyncio.sleep(0.5)

    # Guardar HTML para debug
    html = await page.content()
    with open(f"source_{video_id}.html", "w", encoding="utf-8") as f:
        f.write(html)

    await browser.close()
    return links

async def main():
    with open(INPUT_FILE, "r") as f:
        urls = [u.strip() for u in f if u.strip()]

    all_links = []
    async with async_playwright() as p:
        for url in urls:
            video_id = url.split("v=")[-1]
            links = await process_url(p, url, video_id)
            if links:
                print(f"[INFO] Encontrados {len(links)} enlaces en {url}")
                all_links.extend(links)
            else:
                print(f"[WARN] No se encontraron enlaces en {url}")

    if all_links:
        # Guardar links
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(all_links))
        print(f"[INFO] Guardado {len(all_links)} enlaces en {OUTPUT_FILE}")

        # Generar playlist M3U
        with open(M3U_FILE, "w") as f:
            f.write("#EXTM3U\n")
            for i, link in enumerate(all_links, start=1):
                f.write(f"#EXTINF:-1, Canal {i}\n{link}\n")
        print(f"[INFO] Playlist IPTV generada en {M3U_FILE}")
    else:
        print("[INFO] No se encontraron enlaces")

if __name__ == "__main__":
    asyncio.run(main())