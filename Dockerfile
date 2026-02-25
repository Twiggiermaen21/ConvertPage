# Wybieramy oficjalny, lekki obraz Pythona
FROM python:3.10-slim

# Instalujemy narzędzia systemowe (przydadzą się do obsługi plików i PDF-ów)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    poppler-utils \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /backend

# Kopiujemy plik z wymaganymi bibliotekami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy całą resztę Twojego kodu do kontenera
COPY . .