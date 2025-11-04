#!/usr/bin/env bash

VENV_NAME=.venv-mkdocs

echo -n "Start creating Python virtual env..."
python3 -m venv $VENV_NAME
echo "OK"

echo "Activate by executing the following line"
echo "source $VENV_NAME/bin/activate"