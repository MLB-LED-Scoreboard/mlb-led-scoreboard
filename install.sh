#!/bin/bash
echo "Installing python 3..."
sudo apt-get update && sudo apt-get install python3-dev python3-pip python3-pillow libxml2-dev libxslt-dev  -y
sudo pip3 install tzlocal feedparser "pyowm>3" "mlb-statsapi>=1.5"

echo "Running rgbmatrix installation..."
mkdir submodules
cd submodules
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git matrix
cd matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

cd ../..

if [ -n "$1" ]; then
    echo -e "\nSkipping config.json file creation"
else
    echo -e "\nYou'll need a config.json file to customize your settings. If you are updating"
    echo "from an older version and you were required to run this install script again or"
    echo "this is a fresh install, it's recommended we make a fresh one right now."
    echo "This will create a brand new 'config.json' file with default values so edit this"
    echo -e "file with your own settings.\n"
    read -p "Would you like to do this now? [Y/n] " answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        rm config.json
        cp config.json.example config.json
        chmod 777 config.json
        echo -e "\nYou should now have a fresh config.json file you can customize with your own settings.\n"
    else
        echo -e "\nIf you do not have a config.json, you can manually copy the config.json.example to config.json to customize settings.\n"
    fi
fi
