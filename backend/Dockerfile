# Wybieramy oficjalny, lekki obraz Pythona
FROM python:3.10-slim

# Instalujemy narzędzia systemowe (PDF-y, Ghostscript, FFmpeg, oraz biblioteki dla AI/grafiki)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    poppler-utils \
    ghostscript \
    ffmpeg \
    libgl1 \
    libgomp1 \ 
    && rm -rf /var/lib/apt/lists/*

# Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /backend

# Kopiujemy pliki
COPY requirements.txt .

# NAJPIERW aktualizujemy instalatora pip
RUN pip install --upgrade pip

# Dopiero potem instalujemy Twoje pakiety
RUN pip install --no-cache-dir -r requirements.txt

# --- NOWA SEKCJA: PRE-POBIERANIE MODELU AI ---
# Tworzymy folder na cache modeli rembg (domyślnie ~/.u2net)
RUN mkdir -p /root/.u2net

# Pobieramy model u2net bezpośrednio z GitHuba, aby był dostępny offline
RUN apt-get update && apt-get install -y wget && \
    wget -qO /root/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

# Kopiujemy całą resztę Twojego kodu do kontenera
COPY . .