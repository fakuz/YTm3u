import asyncio
import subprocess
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
            if "googlevideo.com/videoplayback" in response.url:
                if "itag=" in response.url or "mime=" in response.url:
                    stream_url = response.url

        page.on("response", handle_response)

        await page.goto(url)
        # Intentar hacer click en el botón Play para forzar el inicio
        try:
            await page.click("button.ytp-large-play-button", timeout=5000)
        except:
            pass

        # Esperar hasta 40 segundos o hasta capturar la URL
        for _ in range(40):
            if stream_url:
                break
            await asyncio.sleep(1)

        await browser.close()
        return stream_url

def get_reproducible_url(original_url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-url", "-f", "best", original_url],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return original_url
    except Exception as e:
        print(f"Error ejecutando yt-dlp: {e}")
        return original_url

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
            print(f"✅ Capturado: {link}")
            reproducible = get_reproducible_url(link)
            print(f"🎯 URL final reproducible: {reproducible}")
            content += f'#EXTINF:-1 tvg-name="{name}" group-title="YouTube",{name}\n{reproducible}\n'
        else:
            print(f"❌ No se encontró stream para {name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    asyncio.run(main())
