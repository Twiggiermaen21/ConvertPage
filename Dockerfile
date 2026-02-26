# Wybieramy oficjalny, lekki obraz Pythona
FROM python:3.10-slim

# Instalujemy narzędzia systemowe
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    poppler-utils \
    ghostscript \
    ffmpeg \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /backend

# Kopiujemy pliki
COPY requirements.txt .

# NAJPIERW aktualizujemy instalatora pip (to rozwiązuje 90% problemów z budowaniem bibliotek!)
RUN pip install --upgrade pip

# Dopiero potem instalujemy Twoje pakiety
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy całą resztę Twojego kodu do kontenera
COPY . .