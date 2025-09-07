#!/usr/bin/env python3
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# CONFIG
INPUT_FILE = "links.txt"
OUTPUT_FILE = "playlist.m3u"
URL_CONVERT = "https://mobi.jawaltv.com/extras/youtube/"
MAX_RETRIES = 5
WAIT_TIME = 20  # Tiempo máximo de espera para cargar el link generado

def get_driver():
    options = Options()
    options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def generar_playlist():
    print("[INFO] Generando playlist...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            canales = [line.strip().split("|") for line in f if "|" in line]
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo {INPUT_FILE}")
        sys.exit(1)

    driver = get_driver()
    playlist = "#EXTM3U\n"
    exitos = 0
    fallidos = 0

    for nombre, url in canales:
        print(f"[INFO] Procesando: {nombre} ({url})")
        link_m3u8 = None

        for intento in range(1, MAX_RETRIES + 1):
            print(f"[INFO] Intento {intento} para {url}...")
            try:
                driver.get(URL_CONVERT)
                time.sleep(2)

                input_box = driver.find_element(By.NAME, "link")
                input_box.clear()
                input_box.send_keys(url)

                search_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
                search_btn.click()

                time.sleep(WAIT_TIME)

                page_text = driver.find_element(By.TAG_NAME, "body").text
                for line in page_text.splitlines():
                    if line.startswith("https://manifest.googlevideo.com/"):
                        link_m3u8 = line.strip()
                        break

                if link_m3u8:
                    print(f"[OK] Link generado para {nombre}")
                    break
                else:
                    print(f"[WARN] No se encontró el link en el intento {intento}")

            except Exception as e:
                print(f"Error: {e} en intento {intento}")

        if link_m3u8:
            playlist += f'#EXTINF:-1,{nombre}\n{link_m3u8}\n'
            exitos += 1
        else:
            print(f"[INFO] {nombre} no está en vivo o no se pudo generar link.")
            fallidos += 1

    driver.quit()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist)

    print(f"[INFO] Playlist generada: {OUTPUT_FILE}")
    print(f"[INFO] Canales convertidos: {exitos} | Fallidos: {fallidos}")

if __name__ == "__main__":
    generar_playlist()
