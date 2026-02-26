export type PdfTool = 'merge' | 'split' | 'compress' | 'to-jpg' | 'ocr' | 'translate';

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
    disabled?: boolean;
    disabledReason?: string;
}

export const PDF_TOOLS: ToolDef[] = [
    { id: 'merge', icon: '🔗', label: 'Połącz PDF', desc: 'Scal wiele plików w jeden' },
    { id: 'split', icon: '✂️', label: 'Rozdziel PDF', desc: 'Podziel plik na części' },
    { id: 'compress', icon: '📦', label: 'Kompresuj PDF', desc: 'Zmniejsz rozmiar pliku' },
    { id: 'to-jpg', icon: '🖼️', label: 'PDF do JPG', desc: 'Eksportuj strony jako obrazy' },
    { id: 'ocr', icon: '🔍', label: 'OCR PDF', desc: 'Rozpoznaj tekst z obrazów', disabled: true, disabledReason: 'Wkrótce' },
    { id: 'translate', icon: '🌍', label: 'Przetłumacz PDF', desc: 'Przetłumacz treść dokumentu', disabled: true, disabledReason: 'Wkrótce' },
];

export function formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
