from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

INPUT_FILE = "links.txt"
OUTPUT_FILE = "playlist.m3u"
PAGE_URL = "https://mobi.jawaltv.com/extras/youtube/"

def get_m3u8_link(youtube_url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.get(PAGE_URL)

        # Esperar a que cargue el input
        time.sleep(3)

        # Buscar el campo de texto e ingresar el link
        input_box = driver.find_element(By.NAME, "url")  # El name del input debería ser "url"
        input_box.clear()
        input_box.send_keys(youtube_url)

        # Simular presionar Enter o hacer clic en Search
        input_box.send_keys(Keys.RETURN)

        # Esperar que cargue el resultado
        time.sleep(5)

        # Buscar el link .m3u8 en la página
        page_text = driver.page_source
        driver.quit()

        # Buscar el link en el HTML
        start = page_text.find("https://manifest.googlevideo.com")
        if start != -1:
            end = page_text.find(".m3u8", start) + 5
            return page_text[start:end]

    except Exception as e:
        print(f"[ERROR] {e}")
    return None

def generate_playlist():
    print("[INFO] Generando playlist...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    playlist_lines = ['#EXTM3U']
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
        else:
            print(f"[ERROR] No se pudo generar el link para {nombre}")

        time.sleep(2)  # Pausa para no saturar el sitio

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))

    print(f"[INFO] Playlist generada: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
