#!/bin/bash
set -e

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERR] Python3 не установлен."
  exit 1
fi

if ! command -v pip3 >/dev/null 2>&1; then
  echo "[INFO] pip3 не установлен. Устанавливаю..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y python3-pip
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3-pip
  else
    echo "[ERR] Не удалось установить pip3. Попробуйте позже или установите вручную."
    exit 1
  fi
fi

if ! command -v pipx >/dev/null 2>&1; then
  echo "[INFO] pipx не установлен. Устанавливаю..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y pipx
    export PATH="$PATH:$HOME/.local/bin"
  elif command -v brew >/dev/null 2>&1; then
    brew install pipx
    pipx ensurepath
  else
    python3 -m pip install --user pipx
    export PATH="$PATH:$HOME/.local/bin"
  fi
fi

if ! command -v pipx >/dev/null 2>&1; then
  export PATH="$PATH:$HOME/.local/bin"
fi

echo "[INFO] Установка nginx-lens через pipx..."
pipx install --force .

echo "[SUCCESS] nginx-lens установлен. Используйте команду: nginx-lens --help"