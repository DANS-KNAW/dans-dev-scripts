#!/usr/bin/env bash

PORT=${1:-8080}

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Virtual environment for mkdocs not active. Activating..."
  start-virtual-env-mkdocs.sh
  source .venv-mkdocs/bin/activate
fi

echo -n "Upgrading pip3..."
python3 -m pip install --upgrade pip
echo "OK"

echo "Installing dependencies for doc site..."
pip3 install -r .github/workflows/mkdocs/requirements.txt
echo "...OK"

# Downgrade click to version 8.2.1 to work around https://github.com/mkdocs/mkdocs/issues/4032
pip3 install "click==8.2.1"

mkdocs serve -a localhost:$PORT
