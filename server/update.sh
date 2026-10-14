#!/bin/bash
# Holt die neueste Version der Website. Kein Neustart nötig.
# Danach werden geänderte Seiten per IndexNow gemeldet (Bing, Yandex, Naver, Seznam).
DIR=/var/www/finvallo
ALT=$(git -C "$DIR" rev-parse HEAD)
git -C "$DIR" pull --ff-only -q || exit 1
NEU=$(git -C "$DIR" rev-parse HEAD)
if [ ! -f "$DIR/.indexnow-alle" ]; then
  python3 "$DIR/server/indexnow.py" --alle && touch "$DIR/.indexnow-alle"
elif [ "$ALT" != "$NEU" ]; then
  echo "Website aktualisiert."
  # Weiterleitungen geändert: nginx neu laden (nur wenn die Konfiguration gültig ist)
  if git -C "$DIR" diff --name-only "$ALT" "$NEU" | grep -q '^server/redirects.conf$'; then
    nginx -t 2>/dev/null && systemctl reload nginx && echo "nginx neu geladen."
  fi
  git -C "$DIR" diff --name-only "$ALT" "$NEU" -- public | python3 "$DIR/server/indexnow.py"
fi
