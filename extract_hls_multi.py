#!/usr/bin/env python3
import subprocess
import os
import re

INPUT_FILE = "hls_input.txt"
OUTPUT_DIR = "output"

def sanitize_filename(url):
    """Genera un nombre seguro a partir del ID del video."""
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else "video"

def generate_hls(url):
    video_id = sanitize_filename(url)
    output_path = os.path.join(OUTPUT_DIR, f"{video_id}.m3u8")

    print(f"[INFO] Procesando {url}")
    
    # Obtener las mejores URLs de video y audio
    try:
        video_url = subprocess.check_output(
            ["yt-dlp", "-f", "bestvideo", "--get-url", url],
            text=True
        ).strip()
        
        audio_url = subprocess.check_output(
            ["yt-dlp", "-f", "bestaudio", "--get-url", url],
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo extraer {url}: {e}")
        return
    
    print(f"[INFO] Generando HLS para {video_id}...")
    
    # Crear carpeta si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ejecutar ffmpeg
    cmd = [
        "ffmpeg",
        "-y",  # Sobrescribir sin preguntar
        "-i", video_url,
        "-i", audio_url,
        "-c:v", "copy",
        "-c:a", "copy",
        "-f", "hls",
        "-hls_time", "6",
        "-hls_list_size", "0",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] Archivo HLS generado: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFMPEG falló en {video_id}: {e}")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] No existe {INPUT_FILE}")
        return
    
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        generate_hls(url)

if __name__ == "__main__":
    main()