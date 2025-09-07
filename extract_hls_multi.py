import asyncio
import subprocess
import json
from playwright.async_api import async_playwright

INPUT_FILE = "hls_input.txt"
OUTPUT_FILE = "hls_links.txt"
M3U_FILE = "playlist.m3u"

def extract_with_ytdlp(url):
    print(f"[INFO] Intentando con yt-dlp: {url}")
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--no-config",
                "--no-cache-dir",
                "--add-header", "User-Agent: Mozilla/5.0",
                "--add-header", "Accept-Language: en-US,en;q=0.9",
                "--geo-bypass",
                "--dump-json",
                url
            ],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"[ERROR] yt-dlp falló en {url}")
            return None

        data = json.loads(result.stdout)

        # 1) Intentar con hlsManifestUrl
        if "hlsManifestUrl" in data:
            return data["hlsManifestUrl"]

        # 2) Buscar en formats los que tengan protocolo m3u8
        for fmt in data.get("formats", []):
            if fmt.get("protocol") == "m3u8_native" and "url" in fmt:
                return fmt["url"]

        return None
    except Exception as e:
        print(f"[ERROR] Excepción yt-dlp en {url}: {e}")
        return None

async def extract_with_playwright(url, video_id):
    print(f"[INFO] Intentando con Playwright: {url}")
    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        def handle_response(response):
            if "manifest.googlevideo.com/api/manifest/hls_variant" in response.url:
                links.append(response.url)

        page.on("response", handle_response)

        await page.goto(url, wait_until="domcontentloaded")

        # Aceptar cookies si aparecen
        try:
            await page.click('button:has-text("Aceptar")', timeout=5000)
        except:
            pass

        # Intentar hacer clic en Play
        try:
            await page.click('button.ytp-large-play-button', timeout=5000)
        except:
            pass

        # Esperar hasta 30s que aparezca el enlace
        for _ in range(60):
            if links:
                break
            await asyncio.sleep(0.5)

        # Guardar HTML para debug
        html = await page.content()
        with open(f"source_{video_id}.html", "w", encoding="utf-8") as f:
            f.write(html)

        await browser.close()

    return links[0] if links else None

async def main():
    with open(INPUT_FILE, "r") as f:
        urls = [u.strip() for u in f if u.strip()]

    all_links = []
    for url in urls:
        video_id = url.split("v=")[-1]

        # Método 1 y 2: yt-dlp
        link = extract_with_ytdlp(url)

        # Método 3: Playwright
        if not link:
            print(f"[WARN] yt-dlp no encontró nada. Probando con Playwright...")
            link = await extract_with_playwright(url, video_id)

        if link:
            all_links.append(link)
            print(f"[INFO] Enlace HLS encontrado: {link}")
        else:
            print(f"[ERROR] No se pudo extraer HLS para {url}")

    if all_links:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(all_links))

        with open(M3U_FILE, "w") as f:
            f.write("#EXTM3U\n")
            for i, link in enumerate(all_links, start=1):
                f.write(f"#EXTINF:-1, Canal {i}\n{link}\n")

        print(f"[INFO] Guardado {len(all_links)} enlaces en {OUTPUT_FILE} y playlist.m3u")
    else:
        print("[INFO] No se encontraron enlaces.")

if __name__ == "__main__":
    asyncio.run(main())