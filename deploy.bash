#!/bin/bash

rm -rf dist
NAME=WakeOnLanProxy
mkdir -p compiledist
cp *.py compiledist

#con deploy en PYZ, usamos boot para que instale las dependencias
python3 -m zipapp compiledist -o $NAME.pyz -m "boot:boot" --compress

#en caso del pyinstaller, no es necesario ejecutar boot
wine pyinstaller --noconfirm --onefile --name $NAME --clean wakeonlan.py
wine pyinstaller --noconfirm --onedir --name $NAME --clean wakeonlan.py

makensis installer.nsi

rm -r build
rm -r compiledist
