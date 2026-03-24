#!/usr/bin/env bash


export PATH="/opt/homebrew/opt/tcl-tk/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/tcl-tk/lib"
export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk/lib/pkgconfig"

set -euo pipefail

# Build a macOS app bundle using PyInstaller.
# Requires: Python 3, pip install pyinstaller

APP_NAME="SimpleBankingApp"
ENTRY=gui_app.py

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "pyinstaller not found. Install with: pip install pyinstaller"
  exit 1
fi

pyinstaller --noconfirm --windowed --name "$APP_NAME" "$ENTRY" --codesign-identity= 2>/dev/null || pyinstaller --noconfirm --windowed --name "$APP_NAME" "$ENTRY"

echo "Built. Find the app in dist/$APP_NAME.app — move it to your Desktop to 'export' it." 
