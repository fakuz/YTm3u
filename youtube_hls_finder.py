#!/usr/bin/env python3
"""
YouTube HLS Finder (Playwright, filtrando manifest.googlevideo)

- Abre navegador real con Playwright.
- Permite login manual 1 sola vez (guarda cookies en storage_state.json).
- Rastrea URLs en el código fuente que empiecen con https://manifest.googlevideo y terminen en .m3u8.

USO:
  1) Instalar:
       pip install playwright
       playwright install

  2) Guardar sesión:
       python youtube_hls_finder.py login --start https://www.youtube.com/

  3) Rastrear:
       python youtube_hls_finder.py scrape https://www.youtube.com/watch?v=<ID> -o salida.m3u
"""
import argparse
import re
import time
from pathlib import Path
from typing import List, Set, Tuple
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

STORAGE_STATE = Path("storage_state.json")
REGEX_MANIFEST = re.compile(r"https://manifest\\.googlevideo[^'\"<>\\s]+?\\.m3u8", re.IGNORECASE)

def _read_urls(values: List[str]) -> List[str]:
    urls = []
    for v in values:
        p = Path(v)
        if p.exists():
            urls += [line.strip() for line in p.read_text().splitlines() if line.strip()]
        else:
            urls.append(v)
    return list(dict.fromkeys(urls))

def _open_browser(pw, headed: bool) -> Browser:
    return pw.chromium.launch(headless=not headed)

def _new_context(browser: Browser, use_storage: bool) -> BrowserContext:
    return browser.new_context(storage_state=str(STORAGE_STATE) if use_storage and STORAGE_STATE.exists() else None)

def action_login(start_url: str, headed: bool):
    with sync_playwright() as pw:
        browser = _open_browser(pw, headed)
        context = _new_context(browser, use_storage=False)
        page = context.new_page()
        page.goto(start_url)
        print("[INFO] Inicia sesión manualmente y cierra la pestaña o Ctrl+C para continuar...")
        try:
            while True:
                time.sleep(1)
                if page.is_closed():
                    break
        except KeyboardInterrupt:
            pass
        context.storage_state(path=str(STORAGE_STATE))
        print(f"[OK] Sesión guardada en {STORAGE_STATE}")
        context.close()
        browser.close()

def _extract_manifest(page: Page) -> Set[str]:
    html = page.content()
    return set(REGEX_MANIFEST.findall(html))

def _emit_m3u(results: List[Tuple[str, List[str]]], out_path: Path):
    lines = ["#EXTM3U"]
    for url, streams in results:
        for s in streams:
            lines.append(f"#EXTINF:-1,HLS from {url}")
            lines.append(s)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] M3U guardado en {out_path}")

def action_scrape(urls: List[str], headed: bool, out_m3u: str | None):
    with sync_playwright() as pw:
        browser = _open_browser(pw, headed)
        context = _new_context(browser, use_storage=True)
        page = context.new_page()
        results = []
        for url in urls:
            print(f"[INFO] Cargando {url}...")
            page.goto(url)
            page.wait_for_timeout(5000)
            found = list(_extract_manifest(page))
            print(f"[OK] {len(found)} streams encontrados en {url}")
            for f in found:
                print("   ", f)
            results.append((url, found))
        if out_m3u:
            _emit_m3u(results, Path(out_m3u))
        context.close()
        browser.close()

def parse_args():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    login_p = sub.add_parser("login")
    login_p.add_argument("--start", default="https://www.youtube.com/")
    login_p.add_argument("--headless", action="store_true")

    scrape_p = sub.add_parser("scrape")
    scrape_p.add_argument("targets", nargs="+")
    scrape_p.add_argument("-o", "--out", dest="out_m3u")
    scrape_p.add_argument("--headless", action="store_true")

    return p.parse_args()

def main():
    args = parse_args()
    if args.cmd == "login":
        action_login(args.start, headed=not args.headless)
    elif args.cmd == "scrape":
        urls = _read_urls(args.targets)
        action_scrape(urls, headed=not args.headless, out_m3u=args.out_m3u)

if __name__ == "__main__":
    main()