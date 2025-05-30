FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color
ENV FORCE_COLOR=1

RUN apt-get update && apt-get install -y \
    build-essential \
    qtbase5-dev \
    qt5-qmake \
    qtchooser \
    bash

WORKDIR /app/

COPY requirements.txt .
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
RUN uv pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "-a", "1"]
