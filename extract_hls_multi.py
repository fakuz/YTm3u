#!/usr/bin/env python3
import requests
import os
import re
import html as html_lib
import traceback
from urllib.parse import urlparse, parse_qs

INPUT_FILE = "input.txt"
OUTPUT_FILE = "playlist.m3u"
START_TEXT = "https://manifest.googlevideo.com/api/manifest/hls_variant"
END_TEXT = "file/index.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

def video_id_from_url(url):
    try:
        q = parse_qs(urlparse(url).query)
        if "v" in q and q["v"]:
            return q["v"][0]
        path = urlparse(url).path.strip("/")
        return path.split("/")[-1] or "unknown"
    except Exception:
        return "unknown"

def normalize_variants(text):
    variants = []
    original = text
    variants.append(("original", original))

    unescaped_html = html_lib.unescape(original)
    if unescaped_html != original:
        variants.append(("unescaped_html", unescaped_html))

    slash_fixed = original.replace("\\/", "/")
    if slash_fixed != original:
        variants.append(("slash_fixed", slash_fixed))

    unescaped_slash = unescaped_html.replace("\\/", "/")
    if unescaped_slash not in [original, unescaped_html, slash_fixed]:
        variants.append(("unescaped_html_slash_fixed", unescaped_slash))

    collapsed = re.sub(r"\s+", " ", original)
    if collapsed != original:
        variants.append(("collapsed", collapsed))

    collapsed_unescaped = re.sub(r"\s+", " ", unescaped_slash)
    if collapsed_unescaped not in [collapsed, unescaped_slash]:
        variants.append(("collapsed_unescaped_slash_fixed", collapsed_unescaped))

    concat_removed = re.sub(r'(["\'])\s*\+\s*(["\'])', r'\1\2', original)
    if concat_removed != original:
        variants.append(("concat_removed", concat_removed))

    concat_removed_unescaped = re.sub(r'(["\'])\s*\+\s*(["\'])', r'\1\2', unescaped_slash)
    if concat_removed_unescaped not in [concat_removed, unescaped_slash]:
        variants.append(("concat_removed_unescaped_slash_fixed", concat_removed_unescaped))

    return variants

def find_fragment_in_texts(variants, start, end, max_span=5000):
    start_esc = re.escape(start)
    end_esc = re.escape(end)
    pattern = re.compile(start_esc + r".{0," + str(max_span) + r"}?" + end_esc, re.DOTALL)

    for name, txt in variants:
        m = pattern.search(txt)
        if m:
            return name, m.group(0)
    return None, None

def main():
    try:
        if not os.path.exists(INPUT_FILE):
            print(f"[ERROR] No se encontró {INPUT_FILE}.")
            return

        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        if not urls:
            print("[ERROR] input.txt está vacío.")
            return

        session = requests.Session()
        session.headers.update(HEADERS)
        found_links = []

        for url in urls:
            print(f"\n[INFO] Procesando URL: {url}")
            vid = video_id_from_url(url)
            source_file = f"source_{vid}.html"

            try:
                resp = session.get(url, timeout=30, allow_redirects=True)
                print(f"[INFO] Status: {resp.status_code}")
                with open(source_file, "wb") as bf:
                    bf.write(resp.content)
                print(f"[INFO] Guardado en {source_file}")

                try:
                    text = resp.text
                except Exception:
                    enc = resp.encoding or "utf-8"
                    text = resp.content.decode(enc, errors="replace")

                variants = normalize_variants(text)
                variant_name, match = find_fragment_in_texts(variants, START_TEXT, END_TEXT)

                if match:
                    cleaned = match
                    cleaned = html_lib.unescape(cleaned)
                    cleaned = cleaned.replace("\\/", "/")
                    cleaned = cleaned.strip(' \'"')
                    print(f"[OK] Fragmento encontrado en variante '{variant_name}': {cleaned}")
                    found_links.append(cleaned)
                else:
                    print("[WARN] No se encontró el fragmento.")
                    if "manifest.googlevideo.com" in text:
                        idx = text.find("manifest.googlevideo.com")
                        snippet = text[max(0, idx-200): idx+400].replace("\n", "\\n")
                        print(f"[DEBUG] Hay 'manifest.googlevideo.com' cerca de: {snippet}")
                    else:
                        print("[DEBUG] No aparece 'manifest.googlevideo.com' en el HTML.")

            except Exception as e:
                print(f"[ERROR] Excepción descargando {url}: {e}")
                traceback.print_exc()

        if found_links:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u:
                m3u.write("#EXTM3U\n")
                for l in found_links:
                    m3u.write("#EXTINF:-1, YouTube Stream\n")
                    m3u.write(l + "\n")
            print(f"\n[INFO] Playlist guardada en {OUTPUT_FILE} con {len(found_links)} enlaces.")
        else:
            print("\n[INFO] No se encontraron enlaces.")

    except Exception:
        print("[ERROR] Excepción general:")
        traceback.print_exc()

if __name__ == "__main__":
    main()