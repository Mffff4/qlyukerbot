FROM python:3.10.11-alpine3.18

RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev openssl-dev

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p sessions

ENV PYTHONIOENCODING=utf-8
ENV TERM=xterm-256color

CMD ["python", "main.py", "-a", "3"]
