import asyncio
from playwright.async_api import async_playwright

CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u"

async def get_stream_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        stream_url = None

        async def handle_response(response):
            nonlocal stream_url
            if "googlevideo.com/videoplayback" in response.url and "live=1" in response.url:
                stream_url = response.url

        page.on("response", handle_response)

        await page.goto(url)
        # Intentar hacer click en el botón de play
        try:
            await page.click("button.ytp-large-play-button", timeout=5000)
        except:
            pass  # Si no hay botón, no pasa nada

        # Esperar hasta 40s o hasta que encontremos el enlace
        for _ in range(40):
            if stream_url:
                break
            await asyncio.sleep(1)

        await browser.close()
        return stream_url

def load_channels():
    channels = {}
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                name, url = line.strip().split("|", 1)
                channels[name] = url
    return channels

async def main():
    channels = load_channels()
    content = "#EXTM3U\n"
    for name, url in channels.items():
        print(f"🔍 Buscando stream para {name}...")
        link = await get_stream_url(url)
        if link:
            print(f"✅ {name}: {link}")
            content += f'#EXTINF:-1 tvg-name="{name}" group-title="YouTube",{name}\n{link}\n'
        else:
            print(f"❌ No se encontró stream para {name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    asyncio.run(main())
