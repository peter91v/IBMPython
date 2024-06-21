#!/bin/bash

# Erstellen Sie das Verzeichnis octoplug
mkdir octoplug

# Überprüfen Sie, ob Python global installiert ist
if ! command -v python &> /dev/null
then
    echo "Python not found. Installing Python..."
    # Installieren Sie Python und die erforderlichen Pakete
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip gcc make python3-dev openssl libssl-dev libbz2-dev libreadline-dev libffi-dev
else
    echo "Python found. Installing required packages..."
    # Installieren Sie die erforderlichen Python-Pakete
    sudo apt-get update
    sudo apt-get install -y gcc make python3-dev openssl libssl-dev libbz2-dev libreadline-dev libffi-dev
fi

# Erstellen Sie eine virtuelle Umgebung im Verzeichnis octoplug
python3 -m venv octoplug

# Aktivieren Sie die virtuelle Umgebung
source octoplug/bin/activate

# Installieren Sie Flask und grpc-tools
pip install flask grpcio-tools

# Klonen Sie das OctoPyPlug-Repository und installieren Sie es
git clone git@github.com:peter91v/OctoPyPlug.git
pip install -e OctoPyPlug

# Deaktivieren Sie die virtuelle Umgebung
deactivate