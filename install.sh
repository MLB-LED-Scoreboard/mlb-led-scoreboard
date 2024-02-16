#!/bin/bash

usage() {
    cat <<USAGE

    Usage: $0 [-a] [-c] [-m] [-p]

    Options:
        -c, --skip-config:  Skip updating JSON configuration files.
        -m, --skip-matrix:  Skip building matrix driver dependency. Video display will default to emulator mode.
        -p, --skip-python:  Skip Python 3 installation. Requires manual Python 3 setup if not already installed.

        -a, --skip-all:     Skip all dependencies and config installation (equivalent to -c -p -m).
        --no-venv           Do not create a virtual environment for the dependencies.
        --emulator-only:    Do not install dependencies under sudo. Skips building matrix dependencies (equivalent to -m)

USAGE
    exit 1
}

SKIP_PYTHON=false
SKIP_CONFIG=false
SKIP_MATRIX=false
NO_SUDO=false
SKIP_VENV=false

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
        SKIP_VENV=true
        shift # Remove -a / --skip-all from `$@`
        ;;
    --emulator-only)
        SKIP_MATRIX=true
        NO_SUDO=true
        shift # remove --emulator-only from `$@`
        ;;
    --no-venv)
        SKIP_VENV=true
        shift # remove --no-venv from `$@`
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
    echo
    echo "------------------------------------"
    echo "  Installing python 3..."
    echo "------------------------------------"
    echo

    sudo apt-get update && sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-pillow \
        python3-tk \
        python3-venv \
        libxml2-dev \
        libxslt-dev \
        libsdl2-mixer-2.0-0 \
        libsdl2-image-2.0-0 \
        libsdl2-2.0-0 \
        libsdl2-ttf-2.0-0 \
        libopenjp2-7
fi

echo
echo "------------------------------------"
echo "  Installing dependencies..."
echo "------------------------------------"
echo

if [ "$SKIP_VENV" = false ]; then
    echo "Creating virtual environment..."
    if [ "$NO_SUDO" = false ]; then
        sudo python3 -m venv ./venv
    else
        python3 -m venv ./venv
    fi
    source ./venv/bin/activate


    if ! grep -q "#\!/" main.py; then
        if [ "$NO_SUDO" = false ]; then
            sed  -i "1i #\!/usr/bin/sudo $(which python3)" main.py
        else
            sed  -i "1i #\!$(which python3)" main.py
        fi
        chmod +x main.py
    fi
fi
PYTHON=$(which python3)

if [ "$NO_SUDO" = false ]; then
    sudo "$PYTHON" -m pip install -r requirements.txt
else
    "$PYTHON" -m pip install -r requirements.txt
fi

if [ "$SKIP_MATRIX" = false ]; then
    echo "Running rgbmatrix installation..."
    mkdir submodules
    cd submodules
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git matrix
    cd matrix
    git pull
    make build-python PYTHON="$PYTHON"
    sudo make install-python PYTHON="$PYTHON"

    cd ../..
fi

if [ "$SKIP_CONFIG" = true ]; then
    echo
    echo "------------------------------------"
    echo "  Skipping configuration updates"
    echo "------------------------------------"
    echo
else
    if [ ! -f "./config.json" ]; then
        cp config.json.example config.json
        chmod 777 config.json
    fi

    # Yellow
    printf "\e[33m"
    echo
    echo "==================================================================================="
    echo "  If you have custom configurations, colors, or coordinates, it's recommended to"
    echo "  update them with the latest options at this time."
    echo
    echo "  This operation is automatic and will ensure you have up-to-date configuration."
    echo
    echo "  This action will NOT override any custom configuration you already have unless"
    echo "  the option has been obsoleted and is no longer in use."
    echo "==================================================================================="
    echo
    printf "\e[0m"
    # End yellow

    read -p "Would you like to do this now? [Y/n] " answer

    echo
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        python3 validate_config.py
    fi
    echo
fi

echo "Installation finished!"
