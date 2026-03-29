#!/bin/bash
# =============================================================
# OpenFisca Montréal — Script de démarrage
# =============================================================
#
# Usage:
#   ./start.sh          → Lance le frontend seul (rapide, sans Python)
#   ./start.sh --full   → Lance le backend OpenFisca API + frontend
#
# Prérequis:
#   - Python 3.9+
#   - pip
#   - Un navigateur web
# =============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
FRONTEND_PORT=8080
API_PORT=5000

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  OpenFisca Montréal — Simulateur de taxes 2026   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# -----------------------------------------------------------
# Option 1: Frontend seul (pas besoin de Python/OpenFisca)
# -----------------------------------------------------------
if [ "$1" != "--full" ]; then
    echo -e "${GREEN}▸ Mode frontend seul${NC}"
    echo "  Le simulateur fonctionne entièrement côté client."
    echo "  (Pour lancer aussi l'API OpenFisca: ./start.sh --full)"
    echo ""

    # Essayer python3, sinon python, sinon npx
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}▸ Démarrage du serveur HTTP sur http://localhost:${FRONTEND_PORT}${NC}"
        echo ""
        cd "$FRONTEND_DIR"
        python3 -m http.server "$FRONTEND_PORT"
    elif command -v python &> /dev/null; then
        echo -e "${GREEN}▸ Démarrage du serveur HTTP sur http://localhost:${FRONTEND_PORT}${NC}"
        echo ""
        cd "$FRONTEND_DIR"
        python -m http.server "$FRONTEND_PORT"
    elif command -v npx &> /dev/null; then
        echo -e "${GREEN}▸ Démarrage avec npx serve sur http://localhost:${FRONTEND_PORT}${NC}"
        echo ""
        npx -y serve "$FRONTEND_DIR" -p "$FRONTEND_PORT"
    else
        echo -e "${YELLOW}⚠ Aucun serveur HTTP trouvé.${NC}"
        echo "  Ouvrez directement le fichier dans votre navigateur :"
        echo "  file://$FRONTEND_DIR/index.html"
        echo ""
        # Sur macOS, ouvrir automatiquement
        if command -v open &> /dev/null; then
            open "$FRONTEND_DIR/index.html"
        # Sur Linux
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$FRONTEND_DIR/index.html"
        fi
    fi
    exit 0
fi

# -----------------------------------------------------------
# Option 2: Stack complète (API OpenFisca + Frontend)
# -----------------------------------------------------------
echo -e "${GREEN}▸ Mode complet : API OpenFisca + Frontend${NC}"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python 3.9+ requis. Installez-le via:"
    echo "  brew install python3   (macOS)"
    echo "  sudo apt install python3 python3-pip python3-venv  (Ubuntu/Debian)"
    exit 1
fi

# Créer et activer le venv si nécessaire
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${BLUE}▸ Création de l'environnement virtuel...${NC}"
    python3 -m venv "$SCRIPT_DIR/.venv"
fi
source "$SCRIPT_DIR/.venv/bin/activate"

# Installer les dépendances
echo -e "${BLUE}▸ Installation des dépendances...${NC}"
pip install --quiet --upgrade pip
pip install --quiet openfisca-country-template
pip install --quiet -e "$SCRIPT_DIR"

# Lancer l'API OpenFisca en arrière-plan
echo -e "${GREEN}▸ Démarrage de l'API OpenFisca sur http://localhost:${API_PORT}${NC}"
openfisca serve \
    --port "$API_PORT" \
    --country-package openfisca_country_template \
    --extensions openfisca_montreal &
API_PID=$!

# Attendre que l'API soit prête
echo -n "  Attente de l'API"
for i in $(seq 1 30); do
    if curl -s "http://localhost:${API_PORT}/spec" > /dev/null 2>&1; then
        echo -e " ${GREEN}OK${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Lancer le frontend
echo -e "${GREEN}▸ Démarrage du frontend sur http://localhost:${FRONTEND_PORT}${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "  Frontend : ${BLUE}http://localhost:${FRONTEND_PORT}${NC}"
echo -e "  API spec : ${BLUE}http://localhost:${API_PORT}/spec${NC}"
echo -e "  API calc : ${BLUE}http://localhost:${API_PORT}/calculate${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "  Appuyez sur Ctrl+C pour tout arrêter."
echo ""

# Gérer l'arrêt propre
cleanup() {
    echo ""
    echo -e "${YELLOW}▸ Arrêt des serveurs...${NC}"
    kill "$API_PID" 2>/dev/null
    wait "$API_PID" 2>/dev/null
    echo -e "${GREEN}▸ Terminé.${NC}"
}
trap cleanup EXIT INT TERM

cd "$FRONTEND_DIR"
python3 -m http.server "$FRONTEND_PORT"
