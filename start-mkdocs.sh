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

mkdocs serve -a localhost:$PORT
