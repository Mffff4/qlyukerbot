FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color
ENV FORCE_COLOR=1
ENV UV_SYSTEM_PYTHON=1
ENV UV_NETWORK_TIMEOUT=60
ENV UV_RETRY_ATTEMPTS=5

ENV HOSTALIASES=/etc/host.aliases
ENV UV_CUSTOM_PYPI_URL=https://pypi.org/simple/

RUN apt-get update && apt-get install -y \
    build-essential \
    qtbase5-dev \
    qt5-qmake \
    qtchooser \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY . .

CMD ["uv", "run", "main.py", "-a", "1"]
