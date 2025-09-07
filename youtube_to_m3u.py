import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u"

def get_hls_url_with_chrome(url: str) -> str:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Mantener headless para GitHub Actions
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)  # Espera extra para que cargue todo el HTML

        src = driver.page_source
        src = src.replace("\\/", "/")

        # Regex para encontrar el link HLS
        match = re.findall(r"https://manifest\.googlevideo\.com/api/manifest/hls_variant/[^\"']+", src)
        if match:
            # Si hay varios, elegir el de mayor resolución (maxh más alto)
            best = sorted(match, key=lambda x: int(re.search(r"maxh/(\d+)", x).group(1)) if re.search(r"maxh/(\d+)", x) else 0, reverse=True)[0]
            return best
        else:
            return None
    finally:
        driver.quit()

def generate_playlist():
    with open(INPUT_FILE, "r") as f:
        channels = [line.strip().split("|") for line in f if "|" in line]

    playlist = "#EXTM3U\n"
    for name, url in channels:
        print(f"[INFO] Procesando {name}...")
        hls_url = get_hls_url_with_chrome(url)
        if hls_url:
            print(f"[OK] {name} -> {hls_url}")
            playlist += f'#EXTINF:-1,{name}\n{hls_url}\n'
        else:
            print(f"[ERROR] No se encontró stream para {name}")

    with open(OUTPUT_FILE, "w") as f:
        f.write(playlist)
    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
