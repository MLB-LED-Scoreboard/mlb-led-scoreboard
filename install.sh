#!/bin/bash

# Redirect output to a logfile
exec > >(tee -a logs/mlbled.log) 2>&1

SKIP_PYTHON=false
SKIP_CONFIG=false
SKIP_MATRIX=false
NO_SUDO=false
SKIP_VENV=false
DRIVER_SHA=d8778b5 # until https://github.com/hzeller/rpi-rgb-led-matrix/pull/1818 is merged
FORCE=false

usage() {
    cat <<USAGE
    Usage: ./install.sh [-a | --skip-all] [-c | --skip-config] [-m | --skip-matrix] 
                        [-p | --skip-python] [-v | --no-venv] [-e | --emulator-only] 
                        [-d <branch_or_commit> | --driver <branch_or_commit>] 
                        [-f | --force] [-h | --help]

    Options:
        -a, --skip-all          Skip all dependencies and config installation (equivalent to -c -p -m).
        -c, --skip-config       Skip updating JSON configuration files.
        -m, --skip-matrix       Skip building matrix driver dependency. Video display will default to emulator mode.
        -p, --skip-python       Skip Python 3 installation. Requires manual Python 3 setup if not already installed.

        -v, --no-venv           Do not create a virtual environment for the dependencies.
        -e, --emulator-only     Do not install dependencies under sudo. Skips building matrix dependencies (equivalent to -m)
        -d, --driver            Specify a branch name or commit SHA for the rpi-rgb-led-matrix library. (Defaults to "$DRIVER_SHA")

        -f, --force             Try to skip most errors and force install. May be able to recover from previous installer errors.

        -h, --help              Display this help message
USAGE
    exit 1
}

handle_error() {
    local exit_code="$?"
    local line_number="$LINENO"

    # Red
    printf "\e[31m"                                                                            >&2
    echo                                                                                       >&2
    echo "| WARNING |========================================================================" >&2
    echo "  mlb-led-scoreboard failed to install correctly!"                                   >&2
    echo                                                                                       >&2
    echo "  Ensure you are installing from the project directory with:"                        >&2
    echo                                                                                       >&2
    echo "      sudo ./install.sh"                                                             >&2
    echo                                                                                       >&2
    echo "  You may be able to bypass this error by reinstalling with the --force flag"        >&2
    echo                                                                                       >&2
    echo "      sudo ./install.sh --force"                                                     >&2
    echo                                                                                       >&2
    echo "  Debug information:"                                                                >&2
    echo "      | exit_code:   $exit_code"                                                     >&2
    echo "      | line_number: $line_number"                                                   >&2
    echo "===================================================================================" >&2
    echo                                                                                       >&2
    printf "\e[0m"                                                                             >&2
    # End red

    exit "$exit_code"
}

while [ $# -gt 0 ]; do
    case "$1" in
    -p | --skip-python)
        SKIP_PYTHON=true
        shift
        ;;
    -c | --skip-config)
        SKIP_CONFIG=true
        shift
        ;;
    -m | --skip-matrix)
        SKIP_MATRIX=true
        shift
        ;;
    -a | --skip-all)
        SKIP_CONFIG=true
        SKIP_MATRIX=true
        SKIP_PYTHON=true
        SKIP_VENV=true
        shift
        ;;
    -e | --emulator-only)
        SKIP_MATRIX=true
        NO_SUDO=true
        shift
        ;;
    -v | --no-venv)
        SKIP_VENV=true
        shift
        ;;
    -d | --driver)
        DRIVER_SHA="$2"
        shift 2
        ;;
    -f | --force)
        FORCE=true
        shift
        ;;
    -h | --help)
        usage # run usage function on help
        ;;
    *)
        usage # run usage function if wrong argument provided
        ;;
    esac
done

if [ "$FORCE" = false ]; then
    set -Eeuo pipefail

    trap handle_error ERR
fi

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
        cython3 \
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
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' '1i\'$'\n''#!'"$(which python3)"$'\n' main.py
        elif [ "$NO_SUDO" = false ]; then
            sed -i "1i #\!/usr/bin/sudo $(which python3)" main.py
        else
            sed -i "1i #\!$(which python3)" main.py
        fi
        chmod +x main.py

        # Add template to .git/config (if it doesn't already exist), and trigger the filter by adding the file.
        # After that, the shebang should be ignored.
        if ! grep -q "noshebang" ./.git/config; then
            cat .git-config-template >> .git/config
        fi

        git add main.py
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
    sudo apt-get install -y make gcc g++
    mkdir submodules -p
    cd submodules

    if [ -d matrix ]; then
        echo "'matrix' directory already exists. Assuming rpi-rgb-led-matrix is already installed."
    else
        git clone https://github.com/hzeller/rpi-rgb-led-matrix.git matrix
    fi

    cd matrix
    # Checkout the branch or commit specified for rpi-rgb-led-matrix
    git fetch
    git checkout $DRIVER_SHA

    # If we're on 'detached HEAD' state, git pull has a non-zero exit and fails
    # Current branch will be a zero-length string (-z) in this state, so test (-n) for non-empty string
    if [ -n "$(git branch --show-current)" ]; then
        git pull
    fi

    make build-python PYTHON="$PYTHON" CYTHON=cython3
    sudo make install-python PYTHON="$PYTHON"

    cd ../..

    echo "------------------------------------"
    echo "  Checking for snd_bcm2835"
    echo "------------------------------------"
    if [ ! -f /etc/modprobe.d/blacklist-rgbmatrix.conf ]; then
        echo "Sound Blacklist File not found, Creating."
        echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/blacklist-rgbmatrix.conf
        sudo modprobe -r snd_bcm2835
        sudo depmod -a
    else
        echo "Sound Blacklist File found, skipping creation."
    fi
    echo "------------------------------------"
    echo "  Checking for isolcpus=3"
    echo "------------------------------------"
    if grep -q isolcpus=3 "/boot/cmdline.txt" || grep -q isolcpus=3 "/boot/firmware/cmdline.txt" 2>/dev/null;  then
        echo "isolcpus=3 found in cmdline.txt"
    else
        read -d . VERSION < /etc/debian_version
        if [ "$VERSION" -lt "12" ]; then
            echo "adding isolcpus=3 to /boot/cmdline.txt"
            sudo sed -i '$ s/$/ isolcpus=3/' /boot/cmdline.txt
        else
            echo "adding isolcpus=3 to /boot/firmware/cmdline.txt"
            sudo sed -i '$ s/$/ isolcpus=3/' /boot/firmware/cmdline.txt
        fi
    fi
fi

if [ "$SKIP_CONFIG" = true ]; then
    echo
    echo "------------------------------------"
    echo "  Skipping configuration updates"
    echo "------------------------------------"
    echo
else
    if [ ! -f "./config.json" ]; then
        cp config.example.json config.json
        chmod 777 config.json
    fi

    # Yellow
    printf "\e[33m"
    echo
    echo "| NOTICE |========================================================================="
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
