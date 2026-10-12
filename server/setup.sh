#!/bin/bash
# Einmalige Einrichtung von finvallo.com auf diesem Server. Andere Seiten bleiben unberührt.
set -e
DIR=/var/www/finvallo
echo "1/4 Pakete prüfen ..."
apt-get install -y -qq git certbot python3-certbot-nginx >/dev/null
echo "2/4 Website holen ..."
if [ -d "$DIR/.git" ]; then git -C "$DIR" pull --ff-only -q; else git clone -q https://github.com/harisz-commits/finvallo-website.git "$DIR"; fi
echo "3/4 Nginx einrichten ..."
cp "$DIR/server/nginx-finvallo.conf" /etc/nginx/sites-available/finvallo
ln -sf /etc/nginx/sites-available/finvallo /etc/nginx/sites-enabled/finvallo
if nginx -t 2>/dev/null; then systemctl reload nginx; echo "   Nginx OK"; else rm -f /etc/nginx/sites-enabled/finvallo; nginx -t; echo "FEHLER: Konfiguration zurückgenommen, andere Seiten laufen weiter."; exit 1; fi
echo "4/4 HTTPS-Zertifikat ..."
IP=$(curl -s4 https://ifconfig.me || hostname -I | awk '{print $1}')
if getent ahostsv4 finvallo.com | grep -q "$IP"; then
  certbot --nginx -d finvallo.com -d www.finvallo.com --redirect --agree-tos --register-unsafely-without-email -n && echo "FERTIG: https://finvallo.com ist online."
else
  echo "DNS zeigt noch nicht auf diesen Server ($IP). Website ist eingerichtet. Später einfach nochmal ausführen: bash $DIR/server/setup.sh"
fi
