#!/bin/bash

# Setze die Ausführungsrechte für das Skript
# chmod +x start_server.sh

# Starte den OctoPlugRESTService
./OctoVenv/Scripts/activate
python ./src/octoplug/rest_service/octoplugrestapi.py