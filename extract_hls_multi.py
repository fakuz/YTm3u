import asyncio
import re
import os
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError

INPUT_FILE = "input.txt"
OUTPUT_FILE = "playlist.m3u"
PATTERN = r"https://manifest\.googlevideo\.com/api/manifest/hls_variant.*?file/index\.m3u"

MAX_TIMEOUT = 30000  # 30 segundos por URL
WAIT_TIME = 5000     # Espera inicial en ms
RETRIES = 2          # Reintentos por URL

def get_filename_from_url(url):
    parsed = urlparse(url)
    video_id = parsed.query.split("v=")[-1] if "v=" in parsed.query else parsed.path.split("/")[-1]
    return f"source_{video_id}.html"

async def process_url(playwright, url):
    for attempt in range(1, RETRIES + 1):
        print(f"[INFO] ({attempt}/{RETRIES}) Procesando: {url}")
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=MAX_TIMEOUT)
            # Espera dinámica: verifica si aparece el patrón cada segundo
            for _ in range(WAIT_TIME // 1000):
                html = await page.content()
                if re.search(PATTERN, html):
                    print("[INFO] Fragmento encontrado antes de la espera completa.")
                    break
                await asyncio.sleep(1)

            html = await page.content()
            filename = get_filename_from_url(url)
            abs_path = os.path.abspath(filename)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[INFO] HTML guardado en: {abs_path} ({len(html)} caracteres)")

            matches = re.findall(PATTERN, html)
            if matches:
                print(f"[OK] Fragmento encontrado en {url}")
                await browser.close()
                return matches
            else:
                print(f"[WARN] No se encontró fragmento en {url}")
        except TimeoutError:
            print(f"[ERROR] Timeout en {url}")
        except Exception as e:
            print(f"[ERROR] Error en {url}: {e}")
        finally:
            await browser.close()

    return []  # Si falla después de todos los intentos

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] No existe {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("[ERROR] input.txt está vacío.")
        return

    all_links = []

    async with async_playwright() as p:
        for url in urls:
            links = await process_url(p, url)
            all_links.extend(links)

    if all_links:
        abs_path = os.path.abspath(OUTPUT_FILE)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for link in all_links:
                f.write(f"{link}\n")
        print(f"[INFO] Playlist guardada en: {abs_path}")
    else:
        print("[INFO] No se encontraron enlaces en ninguna URL.")

if __name__ == "__main__":
    asyncio.run(main())