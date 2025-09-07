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
# Acepta versión con barras escapadas (\/) y sin escapar.
REGEX_ESCAPED = re.compile(
    r'(https:\\/\\/manifest\.googlevideo\.com\\/api\\/manifest\\/hls_variant\\/expire[^"]*?\\/file\\/index\.m3u8)'
)
REGEX_PLAIN = re.compile(
    r'(https://manifest\.googlevideo\.com/api/manifest/hls_variant/expire[^"]*?/file/index\.m3u8)'
)

def _append_params(url: str) -> str:
    # Ayuda a evitar pantallas de consentimiento/edad
    extra = "bpctr=9999999999&has_verified=1&hl=es&persist_hl=1"
    if "?" in url:
        return url + "&" + extra
    return url + "?" + extra

def _init_driver():
    chrome_path = os.environ.get("CHROME_PATH")  # lo inyecta setup-chrome@v1 en Actions
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
    # Intenta setear cookie de consentimiento para evitar redirecciones a consent.youtube.com
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
    # Abre el código fuente (equivalente a clic derecho → Ver código fuente)
    vs_url = "view-source:" + url
    driver.get(vs_url)
    # En view-source, el HTML real aparece dentro de <pre>
    pre = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "pre"))
    )
    return pre.text  # texto plano del origen de la página

def extract_hls_from_source(text: str) -> str | None:
    # 1) Buscar escapado
    m = REGEX_ESCAPED.search(text)
    if m:
        return m.group(1).replace("\\/", "/")
    # 2) Buscar sin escapar
    m = REGEX_PLAIN.search(text)
    if m:
        return m.group(1)
    return None

def normalize_youtube_url(url: str) -> str:
    # Asegura esquema/host correctos y agrega params anti-consent
    try:
        u = urlparse(url)
        if not u.scheme:
            u = u._replace(scheme="https")
