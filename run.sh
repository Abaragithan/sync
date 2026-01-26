#!/bin/bash
set -e

IMAGE_NAME="sync-ansible:latest"

echo "Starting Sync Deployer GUI..."
echo "Checking Docker image: $IMAGE_NAME"

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
  echo "Docker is not installed. Install Docker first."
  exit 1
fi

# Check if Docker daemon is running
if ! docker info &>/dev/null; then
  echo "Docker daemon is not running. Start Docker and try again."
  exit 1
fi

# Build image if not found
if [[ -z "$(docker images -q $IMAGE_NAME 2>/dev/null)" ]]; then
  echo "Docker image not found. Building now..."
  docker build -t $IMAGE_NAME .
else
  echo "Docker image found."
fi

# Check python
if ! command -v python3 &>/dev/null; then
  echo "python3 not found. Install Python 3 and try again."
  exit 1
fi

# Create venv if not exists
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Activating venv..."
source .venv/bin/activate

echo "Installing GUI requirements..."
pip install -r requirements-gui.txt

echo "Running the GUI..."
python app/main.py
#python app/app.py
