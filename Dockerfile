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

# Tworzymy malutki skrypt Pythona, który odpala rembg.remove na pustych bajtach.
# To wymusi na bibliotece pobranie domyślnego modelu i zapisanie go w cache.
RUN python3 -c 'import rembg; rembg.remove(bytes())'

# Kopiujemy całą resztę Twojego kodu do kontenera
COPY . .