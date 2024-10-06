FROM python:3.10.11-alpine3.18

WORKDIR /app

# Устанавливаем необходимые пакеты для компиляции и сборки
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev openssl-dev

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py", "-a", "2"]