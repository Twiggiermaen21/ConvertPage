export type PdfTool = 'merge' | 'split' | 'compress' | 'to-word' | 'to-html' | 'to-jpg' | 'ocr' | 'translate';

export interface PdfPage {
    thumbnail: string;
    pageNum: number;
    sourceFile: string;
    fileIndex: number;
}

export interface ToolDef {
    id: PdfTool;
    icon: string;
    label: string;
    desc: string;
}

export const PDF_TOOLS: ToolDef[] = [
    { id: 'merge', icon: '🔗', label: 'Połącz PDF', desc: 'Scal wiele plików w jeden' },
    { id: 'split', icon: '✂️', label: 'Rozdziel PDF', desc: 'Podziel plik na części' },
    { id: 'compress', icon: '📦', label: 'Kompresuj PDF', desc: 'Zmniejsz rozmiar pliku' },
    { id: 'to-word', icon: '📝', label: 'PDF do Word', desc: 'Konwertuj na dokument .docx' },
    { id: 'to-html', icon: '🌐', label: 'PDF do HTML', desc: 'Konwertuj na stronę HTML' },
    { id: 'to-jpg', icon: '🖼️', label: 'PDF do JPG', desc: 'Eksportuj strony jako obrazy' },
    { id: 'ocr', icon: '🔍', label: 'OCR PDF', desc: 'Rozpoznaj tekst z obrazów' },
    { id: 'translate', icon: '🌍', label: 'Przetłumacz PDF', desc: 'Przetłumacz treść dokumentu' },
];

export function formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
