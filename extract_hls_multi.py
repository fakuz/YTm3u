import subprocess
import json

INPUT_FILE = "hls_input.txt"
OUTPUT_FILE = "hls_links.txt"
M3U_FILE = "playlist.m3u"

def extract_hls_with_ytdlp(url):
    print(f"[INFO] Procesando con yt-dlp: {url}")
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--no-config",
                "--no-cache-dir",
                "--add-header", "User-Agent: Mozilla/5.0",
                "--add-header", "Accept-Language: en-US,en;q=0.9",
                "--geo-bypass",
                "--dump-json",
                url
            ],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"[ERROR] yt-dlp falló en {url}")
            return None

        data = json.loads(result.stdout)
        hls_url = data.get("hlsManifestUrl")
        return hls_url if hls_url else None

    except Exception as e:
        print(f"[ERROR] Excepción en {url}: {e}")
        return None

def main():
    with open(INPUT_FILE, "r") as f:
        urls = [u.strip() for u in f if u.strip()]

    all_links = []
    for url in urls:
        link = extract_hls_with_ytdlp(url)
        if link:
            all_links.append(link)
            print(f"[INFO] HLS encontrado: {link}")
        else:
            print(f"[WARN] No se encontró HLS para {url}")

    if all_links:
        # Guardar en TXT
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(all_links))
        print(f"[INFO] Guardado {len(all_links)} enlaces en {OUTPUT_FILE}")

        # Generar playlist.m3u
        with open(M3U_FILE, "w") as f:
            f.write("#EXTM3U\n")
            for i, link in enumerate(all_links, start=1):
                f.write(f"#EXTINF:-1, Canal {i}\n{link}\n")
        print(f"[INFO] Playlist generada en {M3U_FILE}")
    else:
        print("[INFO] No se encontraron enlaces")

if __name__ == "__main__":
    main()