#!/bin/bash
# ============================================================
#   Historique Nomade - lanceur macOS
#   Double-cliquez sur ce fichier (ou clic droit > Ouvrir la
#   premiere fois si macOS le bloque).
# ============================================================
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    exec python3 history_tool.py "$@"
fi

echo ""
echo "  Python 3 est introuvable."
echo "  Installez-le depuis https://python.org puis relancez ce fichier."
echo ""
read -n 1 -s -r -p "Appuyez sur une touche pour fermer..."
echo ""
