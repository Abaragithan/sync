# run.ps1
$ErrorActionPreference = "Stop"

$IMAGE_NAME = "sync-ansible:latest"

Write-Host "Starting Sync Deployer GUI..."
Write-Host "Checking Docker image: $IMAGE_NAME"

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed. Install Docker Desktop first."
    exit 1
}

# Check if Docker daemon is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker daemon is not running. Start Docker Desktop and try again."
    exit 1
}

# Build image if not found
$imageId = docker images -q $IMAGE_NAME 2>$null
if ([string]::IsNullOrWhiteSpace($imageId)) {
    Write-Host "Docker image not found. Building now..."
    docker build -t $IMAGE_NAME .
} else {
    Write-Host "Docker image found."
}

# Check python (prefer py launcher)
$pythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    Write-Host "Python not found. Install Python 3 first."
    exit 1
}

# Create venv if not exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    & $pythonCmd -m venv .venv
}

Write-Host "Activating venv..."
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing GUI requirements..."
python -m pip install --upgrade pip
pip install -r requirements-gui.txt

Write-Host "Running the GUI..."
python app\main.py
