#!/usr/bin/env bash

python3 -m venv venv;
./venv/bin/pip3 install -r requirements.txt
echo PATH='$PATH':"${pwd}" >> $HOME/.profile