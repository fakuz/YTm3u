import sys
import asyncio
import argparse
from playwright.async_api import async_playwright

async def login(start_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        print(f"[INFO] Abriendo {start_url} para login...")
        await page.goto(start_url)
        print("[INFO] Inicia sesión en YouTube y presiona Enter aquí cuando termines...")
        input("Presiona Enter cuando hayas iniciado sesión...")
        await context.storage_state(path="storage_state.json")
        print("[OK] Sesión guardada en storage_state.json")
        await browser.close()

async def scrape(urls_file, output):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="storage_state.json")
        page = await context.new_page()

        hls_links = []
        with open(urls_file, "r") as f:
            urls = [u.strip() for u in f if u.strip()]

        for url in urls:
            print(f"[INFO] Abriendo {url}")
            await page.goto(url)

            # ✅ Detector de sesión expirada
            if "accounts.google.com" in page.url:
                print("⚠️ Sesión expirada. Debes regenerar storage_state.json y actualizar el Secret.")
                await context.close()
                await browser.close()
                sys.exit(1)

            html = await page.content()
            # Buscar links HLS
            for line in html.split('"'):
                if line.startswith("https://manifest.googlevideo") and line.endswith(".m3u8"):
                    hls_links.append(line)
                    print(f"[OK] Encontrado: {line}")

        if hls_links:
            with open(output, "w") as out:
                out.write("#EXTM3U\n")
                for link in hls_links:
                    out.write(f"#EXTINF:-1, YouTube Stream\n{link}\n")
            print(f"[OK] Playlist generada: {output}")
        else:
            print("[WARN] No se encontraron enlaces HLS")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube HLS Finder")
    subparsers = parser.add_subparsers(dest="command")

    login_cmd = subparsers.add_parser("login")
    login_cmd.add_argument("--start", required=True, help="URL de inicio para login")

    scrape_cmd = subparsers.add_parser("scrape")
    scrape_cmd.add_argument("urls", help="Archivo con URLs de YouTube")
    scrape_cmd.add_argument("-o", "--output", default="streams.m3u", help="Archivo M3U de salida")

    args = parser.parse_args()

    if args.command == "login":
        asyncio.run(login(args.start))
    elif args.command == "scrape":
        asyncio.run(scrape(args.urls, args.output))
    else:
        parser.print_help()