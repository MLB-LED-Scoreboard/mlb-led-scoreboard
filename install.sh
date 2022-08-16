#!/bin/bash

function usage() {
    cat <<USAGE

    Usage: $0 [-a] [-c] [-m] [-p]

    Options:
        -c, --skip-config:  Skip creating a new JSON config.
        -m, --skip-matrix:  Skip building matrix driver dependency. Video display will default to emulator mode.
        -p, --skip-python:  Skip Python 3 installation. Requires manual Python 3 setup if not already installed.

        -a, --skip-all:     Skip all dependencies and config installation (equivalent to -c -p -m).

USAGE
    exit 1
}

SKIP_PYTHON=false
SKIP_CONFIG=false
SKIP_MATRIX=false

for arg in "$@"; do
    case $arg in
    -p | --skip-python)
        SKIP_PYTHON=true
        shift # Remove -p / --skip-python from `$@`
        ;;
    -c | --skip-config)
        SKIP_CONFIG=true
        shift # Remove -c / --skip-config from `$@`
        ;;
    -m | --skip-matrix)
        SKIP_MATRIX=true
        shift # Remove -m / --skip-matrix from `$@`
        ;;
    -a | --skip-all)
        SKIP_CONFIG=true
        SKIP_MATRIX=true
        SKIP_PYTHON=true
        shift # Remove -a / --skip-all from `$@`
        ;;
    -h | --help)
        usage # run usage function on help
        ;;
    *)
        usage # run usage function if wrong argument provided
        ;;
    esac
done

if [ "$SKIP_PYTHON" = false ]; then
    echo "Installing python 3..."
    sudo apt-get update && sudo apt-get install python3-dev python3-pip python3-pillow libxml2-dev libxslt-dev -y
fi

echo "Installing dependencies..."
sudo pip3 install -r requirements.txt

if [ "$SKIP_MATRIX" = false ]; then
    echo "Running rgbmatrix installation..."
    mkdir submodules
    cd submodules
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git matrix
    cd matrix
    git pull
    make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)

    cd ../..
fi

if [ "$SKIP_CONFIG" = true ]; then
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
