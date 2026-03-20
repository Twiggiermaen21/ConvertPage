const fs = require('fs');
const path = require('path');

// Ścieżka do pliku wynikowego
const envDirectory = path.join(__dirname, 'src', 'environments');
const targetPath = path.join(envDirectory, 'environment.ts');

// Tworzenie folderu, jeśli nie istnieje
if (!fs.existsSync(envDirectory)) {
  fs.mkdirSync(envDirectory, { recursive: true });
}

// Pobieranie URL z environment (Vercel) lub lokalnego pliku .env w głównym folderze
let apiUrl = process.env.API_URL;

const rootEnvPath = path.join(__dirname, '..', '..', '.env');
if (!apiUrl && fs.existsSync(rootEnvPath)) {
  const envContent = fs.readFileSync(rootEnvPath, 'utf8');
  const match = envContent.match(/^API_URL=(.+)$/m);
  if (match) {
    apiUrl = match[1].trim().replace(/^['"]|['"]$/g, '');
  }
}

if (!apiUrl) {
  apiUrl = 'http://localhost:8000/api';
}

const envConfigFile = `
export const environment = {
  production: true,
  apiUrl: '${apiUrl}'
};
`;

console.log('Generowanie environment.ts...');
fs.writeFileSync(targetPath, envConfigFile);
console.log(`Plik wygenerowany w ${targetPath}`);
