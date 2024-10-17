#!/usr/bin/env bash

set -e

error() {
    echo "ERROR: $1" >&2
    exit 1
}

install_dependencies() {
    if command -v apt-get &> /dev/null; then
        export DEBIAN_FRONTEND=noninteractive
        sudo ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime
        sudo apt-get update || true
        sudo apt-get install -y tzdata
        sudo dpkg-reconfigure --frontend noninteractive tzdata
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update || true
        sudo apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip git
    elif command -v yum &> /dev/null; then
        sudo yum install -y https://repo.ius.io/ius-release-el7.rpm
        sudo yum install -y python310 python310-devel python310-pip git
    elif command -v brew &> /dev/null; then
        brew install python@3.10 git
    else
        error "Unable to detect package manager. Please install Python 3.10, pip, and git manually."
    fi
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || error "Failed to change directory to script location."

if [ -d "venv" ] && [ -f "venv/bin/python3" ] && [ -f "venv/installed" ] && [ -f ".env" ]; then
    echo "Environment is already set up. Activating and running the bot..."
    source venv/bin/activate
    python3 main.py
    exit 0
fi

echo "Full setup required. Starting installation process..."

if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 not found. Installing dependencies..."
    install_dependencies
fi

PYTHON_CMD=$(command -v python3.10)
if [ -z "$PYTHON_CMD" ]; then
    error "Python 3.10 is not installed or not in PATH. Please install Python 3.10."
fi

python_version=$("$PYTHON_CMD" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$python_version" != "3.10" ]]; then
    error "Python 3.10 is required. Current version: $python_version. Please install Python 3.10."
fi

echo "Current directory: $(pwd)"
echo "Python command: $PYTHON_CMD"

if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

echo "Creating new virtual environment..."
"$PYTHON_CMD" -m venv venv
if [ $? -ne 0 ]; then
    error "Failed to create virtual environment. Error code: $?"
fi
echo "Virtual environment created successfully."

VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
VENV_PIP="$SCRIPT_DIR/venv/bin/pip"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Contents of venv/bin:"
    ls -l venv/bin
    error "Virtual environment Python not found at $VENV_PYTHON"
fi

echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    error "Failed to activate virtual environment. Error code: $?"
fi
echo "Virtual environment activated successfully."

if [ ! -f "$VENV_PIP" ]; then
    error "Virtual environment pip not found at $VENV_PIP"
fi

if [ ! -f "venv/installed" ]; then
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies..."
        "$VENV_PYTHON" -m pip install --upgrade pip || error "Failed to upgrade pip."
        "$VENV_PIP" install wheel || error "Failed to install wheel."
        "$VENV_PIP" install -r requirements.txt || error "Failed to install dependencies."
        touch venv/installed
    else
        error "requirements.txt not found. Cannot install dependencies."
    fi
else
    echo "Dependencies already installed, skipping installation."
fi

if [ ! -f ".env" ]; then
    if [ -f ".env-example" ]; then
        echo "Copying configuration file..."
        cp .env-example .env || error "Failed to copy .env-example to .env"
        echo "Please edit the .env file with your configuration."
    else
        error ".env-example not found. Cannot create .env file."
    fi
else
    echo "Configuration file .env already exists, skipping."
fi

echo "Updating repository..."
git stash || error "Failed to stash changes."
git pull || error "Failed to pull latest changes."
git stash pop || { echo "No local changes to reapply."; true; }

echo "Starting the bot..."
"$VENV_PYTHON" main.py || error "Failed to start the bot."

echo "Bot execution completed."
