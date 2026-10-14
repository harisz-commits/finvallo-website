#!/bin/bash
# Kompletter Neuaufbau aller generierten Seiten in der richtigen Reihenfolge.
set -e; cd "$(dirname "$0")/.."
python3 tools/karten.py
python3 tools/lohnt.py
python3 tools/ratgeber.py
python3 tools/rechner.py
python3 tools/header.py >/dev/null
python3 tools/landing.py
python3 tools/cleanup.py
python3 tools/listui.py
python3 tools/rechnen.py
V=$(sha256sum public/assets/site.css | cut -c1-8)
find public -name '*.html' -exec sed -i -E "s#(assets/site\.css)\?v=[a-z0-9]+\"#\1?v=$V\"#g" {} +
rm -rf tools/__pycache__
echo "fertig, css v=$V"
