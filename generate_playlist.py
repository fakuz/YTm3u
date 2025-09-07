from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

INPUT_FILE = "links.txt"
OUTPUT_FILE = "playlist.m3u"
PAGE_URL = "https://mobi.jawaltv.com/extras/youtube/"
MAX_RETRIES = 5
WAIT_TIME = 20  # segundos máximos para esperar el link después del clic

def get_m3u8_link(youtube_url):
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[INFO] Intento {attempt} para {youtube_url}...")
        try:
            options = Options()
            options.binary_location = "/usr/bin/chromium-browser"
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=options)
            driver.get(PAGE_URL)

            time.sleep(3)  # Espera inicial para cargar la página

            try:
                input_box = driver.find_element(By.NAME, "url")
            except:
                print("[ERROR] No se encontró el campo de búsqueda")
                driver.quit()
                continue

            input_box.clear()
            input_box.send_keys(youtube_url)
            input_box.send_keys(Keys.RETURN)

            start_time = time.time()
            m3u8_link = None
            while time.time() - start_time < WAIT_TIME:
                page_text = driver.page_source
                start = page_text.find("https://manifest.googlevideo.com")
                if start != -1:
                    end = page_text.find(".m3u8", start) + 5
                    m3u8_link = page_text[start:end]
                    break
                time.sleep(1)

            driver.quit()

            if m3u8_link:
                return m3u8_link
            else:
                print(f"[WARN] No se encontró el link en el intento {attempt}")
                time.sleep(2)

        except Exception as e:
            print(f"[ERROR] {e} en intento {attempt}")
            time.sleep(2)

    print(f"[INFO] El canal {youtube_url} puede no estar transmitiendo en vivo.")
    return None

def generate_playlist():
    print("[INFO] Generando playlist...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    playlist_lines = ['#EXTM3U']
    converted = 0
    failed = 0

    for line in lines:
        if "|" not in line:
            print(f"[WARN] Formato inválido en línea: {line}")
            continue

        nombre, youtube_url = line.split("|", 1)
        print(f"[INFO] Procesando: {nombre} ({youtube_url})")

        m3u8_link = get_m3u8_link(youtube_url)
        if m3u8_link:
            playlist_lines.append(f'#EXTINF:-1,{nombre}')
            playlist_lines.append(m3u8_link)
            converted += 1
            print(f"[OK] Link generado para {nombre}")
        else:
            failed += 1
            print(f"[INFO] {nombre} no está en vivo o no se pudo generar link.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))

    print(f"[INFO] Playlist generada: {OUTPUT_FILE}")
    print(f"[INFO] Canales convertidos: {converted} | Fallidos: {failed}")

if __name__ == "__main__":
    generate_playlist()
