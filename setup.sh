#!/bin/bash

# Setup-Skript für CreatorOS
echo "🚀 CreatorOS Setup wird gestartet..."

# Erstelle virtuelles Environment
echo "📦 Erstelle virtuelles Environment (.venv)..."
python3 -m venv .venv

# Aktiviere virtuelles Environment
echo "✅ Aktiviere virtuelles Environment..."
source .venv/bin/activate

# Installiere Requirements
echo "📥 Installiere Abhängigkeiten..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✨ Setup erfolgreich abgeschlossen!"
echo ""
echo "Um die App zu starten:"
echo "  1. Aktiviere das Environment: source .venv/bin/activate"
echo "  2. Starte Streamlit: streamlit run app.py"
echo ""

