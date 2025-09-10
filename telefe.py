name: Actualizar Telefe M3U

on:
  schedule:
    - cron: "0 */4 * * *"  # cada 4 horas
  workflow_dispatch:

jobs:
  update-m3u:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Instalar dependencias
        run: pip install requests

      - name: Ejecutar script Telefe
        run: python telefe.py

      - name: Commit y push de cambios
        run: |
          git config --global user.name "fakuz"
          git config --global user.email "fakuz@users.noreply.github.com"
          git add telefe.m3u
          git commit -m "Actualizar telefe.m3u"
          git push