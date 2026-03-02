# Etap 1: Budowanie aplikacji Angular
FROM node:20-alpine AS build

WORKDIR /app

# Kopiowanie plików zależności
COPY package.json package-lock.json ./
RUN npm ci

# Kopiowanie reszty kodu źródłowego
COPY . .

# Zbudowanie aplikacji produkcyjnej
RUN npx ng build --configuration production

# Etap 2: Serwowanie za pomocą Nginx
FROM nginx:alpine

# Usunięcie domyślnej strony Nginx
RUN rm -rf /usr/share/nginx/html/*

# Skopiowanie zbudowanych plików z pierwszego etapu
# Uwaga: Ścieżka dist/pdf-yt-audio/browser zależy od nazwy projektu w angular.json
COPY --from=build /app/dist/pdf-yt-audio/browser /usr/share/nginx/html

# Kopiowanie niestandardowej konfiguracji Nginx (do obsługi routingu SPA i proxy do paska API)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Ekspozycja portu 80
EXPOSE 80

# Uruchomienie Nginx
CMD ["nginx", "-g", "daemon off;"]
