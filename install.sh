#!/bin/bash
echo "Installing python 3..."
sudo apt-get update && sudo apt-get install python3-dev python3-pip python3-pillow libxml2-dev libxslt-dev  -y
sudo pip3 install tzlocal feedparser "pyowm>3" mlb-statsapi

echo "Running rgbmatrix installation..."
mkdir submodules
cd submodules
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git matrix
cd matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

cd ../..
cp config.json.example config.json
