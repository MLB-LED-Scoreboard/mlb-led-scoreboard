#!/bin/bash
git submodule update
cd matrix
echo "Running rgbmatrix installation..."
sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
make build-python
sudo make install-python
cd bindings
sudo pip install -e python/
cd ../../
echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
git reset --hard
git checkout master
git fetch origin --prune
git pull
sudo apt-get install libxml2-dev libxslt-dev
sudo pip install pytz tzlocal "feedparser<6.0.0" pyowm
sudo pip uninstall -y mlbgame
sudo pip install git+git://github.com/ajbowler/mlbgame.git@#egg=mlbgame
make
echo "If you didn't see any errors above, everything should be installed!"
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
        echo -e "\nYou should now have a fresh config.json file you can customize with your own settings.\n"
    else
        echo -e "\nIf you do not have a config.json, you can manually copy the config.json.example to config.json to customize settings.\n"
    fi
fi
chown pi:pi config.json
echo "Installation complete! Play around with the examples in matrix/bindings/python/samples to make sure your matrix is working."
