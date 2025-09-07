import asyncio
from playwright.async_api import async_playwright
import re

INPUT_FILE = "hls_input.txt"
OUTPUT_FILE = "hls_links.txt"

async def fetch_page(playwright, url, video_id):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    
    print(f"[INFO] Procesando URL: {url}")
    await page.goto(url, wait_until="networkidle")

    # Guardar HTML completo
    html = await page.content()
    source_file = f"source_{video_id}.html"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Guardado en {source_file}")

    # Buscar fragmento
    matches = re.findall(r"https://manifest\.googlevideo\.com[^\"']+", html)
    await browser.close()
    return matches

async def main():
    with open(INPUT_FILE, "r") as f:
        urls = [u.strip() for u in f if u.strip()]

    all_links = []
    async with async_playwright() as p:
        for url in urls:
            video_id = url.split("v=")[-1]
            links = await fetch_page(p, url, video_id)
            if links:
                print(f"[INFO] Encontrados {len(links)} enlaces en {url}")
                all_links.extend(links)
            else:
                print(f"[WARN] No se encontraron enlaces en {url}")

    if all_links:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(all_links))
        print(f"[INFO] Guardado {len(all_links)} enlaces en {OUTPUT_FILE}")
    else:
        print("[INFO] No se encontraron enlaces")

if __name__ == "__main__":
    asyncio.run(main())
