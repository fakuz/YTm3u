#!/usr/bin/env python3
import os
import re
import time
from urllib.parse import urlparse, urlunparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "playlist.m3u"

# Patrón exacto: empieza en .../hls_variant/expire... y termina en /file/index.m3u8
REGEX_ESCAPED = re.compile(
    r'(https:\\/\\/manifest\.googlevideo\.com\\/api\\/manifest\\/hls_variant\\/expire[^"]*?\\/file\\/index\.m3u8)'
)
REGEX_PLAIN = re.compile(
    r'(https://manifest\.googlevideo\.com/api/manifest/hls_variant/expire[^"]*?/file/index\.m3u8)'
)

def _append_params(url: str) -> str:
    extra = "bpctr=9999999999&has_verified=1&hl=es&persist_hl=1"
    if "?" in url:
        return url + "&" + extra
    return url + "?" + extra

def _init_driver():
    chrome_path = os.environ.get("CHROME_PATH")
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=es-ES")
    opts.add_argument("--window-size=1280,800")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0")
    if chrome_path:
        opts.binary_location = chrome_path
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    return driver

def _set_consent_cookie(driver):
    try:
        driver.get("https://www.youtube.com/")
        time.sleep(1)
        driver.add_cookie({
            "name": "CONSENT",
            "value": "YES+cb.20210328-17-p0.es+FX+123",
            "domain": ".youtube.com",
            "path": "/",
            "secure": True,
            "httpOnly": False,
        })
    except Exception:
        pass

def _open_view_source(driver, url: str):
    vs_url = "view-source:" + url
    driver.get(vs_url)
    pre = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "pre"))
    )
    return pre.text

def extract_hls_from_source(text: str) -> str | None:
    m = REGEX_ESCAPED.search(text)
    if m:
        return m.group(1).replace("\\/", "/")
    m = REGEX_PLAIN.search(text)
    if m:
        return m.group(1)
    return None

def normalize_youtube_url(url: str) -> str:
    try:
        u = urlparse(url)
        if not u.scheme:
            u = u._replace(scheme="https")
        if "youtube.com" not in u.netloc:
            if "youtu.be" in u.netloc:
                video_id = u.path.strip("/")
                u = urlparse(f"https://www.youtube.com/watch?v={video_id}")
        return _append_params(urlunparse(u))
    except Exception:
        return _append_params(url)

def get_hls_url_with_chrome(youtube_url: str) -> str | None:
    driver = _init_driver()
    try:
        _set_consent_cookie(driver)
        url = normalize_youtube_url(youtube_url)
        try:
            driver.get(url)
        except Exception:
            pass
        src = _open_view_source(driver, url)
        return extract_hls_from_source(src)
    finally:
        driver.quit()

def generate_playlist():
    lines = ["#EXTM3U"]
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or "|" not in raw:
                continue
            name, yt = raw.split("|", 1)
            print(f"[INFO] Procesando {name}...")
            hls = get_hls_url_with_chrome(yt.strip())
            if hls:
                print(f"[OK] Stream encontrado para {name}")
                lines.append(f'#EXTINF:-1,{name}')
                lines.append(hls)
            else:
                print(f"[WARN] No se encontró stream para {name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))
    print(f"[INFO] Playlist generada en {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
