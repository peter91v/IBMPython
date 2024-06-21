#!/bin/bash

# Setze die Ausführungsrechte für das Skript
# chmod +x start_server.sh

# Starte den gRPC-Server
./OctoVenv/Scripts/activate
python.exe ./src/octoplug/classes/datalistener.py

