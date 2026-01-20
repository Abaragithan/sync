FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sshpass \
    openssh-client \
    libxkbcommon-x11-0 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install official Ansible Windows collection
RUN ansible-galaxy collection install ansible.windows

# Copy project files
COPY . .

# Environment for GUI
ENV QT_X11_NO_MITSHM=1

CMD ["python", "app.py"]
