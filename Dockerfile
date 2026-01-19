# Switching from slim to the full image
FROM python:3.12

# Install only the essentials for Ansible and specific XCB support
RUN apt-get update && apt-get install -y \
    sshpass \
    openssh-client \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy project files
COPY . .

# Environment for GUI
ENV QT_X11_NO_MITSHM=1

CMD ["python", "app.py"]