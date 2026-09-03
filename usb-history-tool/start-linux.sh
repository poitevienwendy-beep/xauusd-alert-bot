#!/usr/bin/env bash
# ============================================================
#   Historique Nomade - lanceur Linux
#   Rendez-le executable une fois :  chmod +x start-linux.sh
#   Puis :  ./start-linux.sh
# ============================================================
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    exec python3 history_tool.py "$@"
elif command -v python >/dev/null 2>&1; then
    exec python history_tool.py "$@"
fi

echo ""
echo "  Python 3 est introuvable."
echo "  Installez-le, par exemple :  sudo apt install python3"
echo ""
exit 1
