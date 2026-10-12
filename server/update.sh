#!/bin/bash
# Holt die neueste Version der Website. Kein Neustart nötig.
git -C /var/www/finvallo pull --ff-only && echo "Website aktualisiert."
