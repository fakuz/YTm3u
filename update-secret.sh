#!/bin/bash
# Script para actualizar el Secret YT_STORAGE_STATE en GitHub
# Uso: ./update-secret.sh

SECRET_NAME="YT_STORAGE_STATE"

echo "[INFO] Generando base64 del storage_state.json..."
if [ ! -f storage_state.json ]; then
    echo "[ERROR] No se encontró storage_state.json. Primero ejecuta:"
    echo "python youtube_hls_finder.py login --start https://www.youtube.com/"
    exit 1
fi

# Convertir a base64
ENCODED=$(base64 storage_state.json)

echo "[INFO] Actualizando Secret en GitHub: $SECRET_NAME ..."
gh secret set "$SECRET_NAME" <<< "$ENCODED"

if [ $? -eq 0 ]; then
    echo "[OK] Secret actualizado correctamente."
else
    echo "[ERROR] No se pudo actualizar el Secret. ¿Instalaste GitHub CLI y estás logueado?"
fi
