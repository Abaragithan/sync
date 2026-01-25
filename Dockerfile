FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    sshpass \
    openssh-client \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install -r requirements-docker.txt

# Install Ansible collections you need
RUN for i in 1 2 3 4 5; do \
      ansible-galaxy collection install ansible.windows && break; \
      echo "Retry $i failed, sleeping..."; \
      sleep 10; \
    done

# Default to shell so GUI can run any ansible command easily
WORKDIR /app/ansible
CMD ["bash"]