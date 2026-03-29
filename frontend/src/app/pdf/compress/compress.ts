import { Component, signal, output } from '@angular/core';
import { environment } from '../../../environments/environment';
import { formatFileSize } from '../pdf-shared';

@Component({
    selector: 'app-compress-tool',
    standalone: true,
    templateUrl: './compress.html',
    styleUrl: './compress.css'
})
export class CompressToolComponent {
    back = output<void>();

    file = signal<File | null>(null);
    isProcessing = signal(false);
    elapsedSeconds = signal(0);
    private timerInterval: any;
    dpi = signal(150);
    originalDpi = signal(300);
    isDetectingDpi = signal(false);

    onDpiChange(event: Event) {
        const val = +(event.target as HTMLInputElement).value;
        this.dpi.set(val);
    }

    get dpiLabel(): string {
        const d = this.dpi();
        const orig = this.originalDpi();
        if (d >= orig) return 'Oryginalna jakość';
        if (d <= 72) return 'Minimalna jakość';
        if (d <= 100) return 'Niska jakość';
        if (d <= 150) return 'Średnia jakość';
        if (d <= 200) return 'Dobra jakość';
        return 'Wysoka jakość';
    }

    onFileSelected(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files?.length) {
            this.file.set(input.files[0]);
            input.value = '';
            this.detectOriginalDpi();
        }
    }

    removeFile(event: Event) {
        event.stopPropagation();
        this.file.set(null);
        this.originalDpi.set(300);
        this.dpi.set(150);
    }

    onDragOver(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
    }

    onDrop(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        const files = event.dataTransfer?.files;
        if (files?.length) {
            const pdf = Array.from(files).find(f => f.type === 'application/pdf');
            if (pdf) {
                this.file.set(pdf);
                this.detectOriginalDpi();
            }
        }
    }

    async detectOriginalDpi() {
        const f = this.file();
        if (!f) return;

        this.isDetectingDpi.set(true);
        try {
            const pdfjsLib = await import('pdfjs-dist');
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'assets/pdf.worker.min.mjs';

            const data = new Uint8Array(await f.arrayBuffer());
            const pdf = await pdfjsLib.getDocument({ data }).promise;
            const page = await pdf.getPage(1);
            const viewport = page.getViewport({ scale: 1.0 });

            const pageWidthInches = viewport.width / 72;
            const pageHeightInches = viewport.height / 72;

            const ops = await page.getOperatorList();
            let maxDpi = 72;

            for (let i = 0; i < ops.fnArray.length; i++) {
                if (ops.fnArray[i] === pdfjsLib.OPS.paintImageXObject ||
                    ops.fnArray[i] === pdfjsLib.OPS.paintInlineImageXObject) {
                    try {
                        const imgName = ops.argsArray[i][0];
                        const imgData: any = await new Promise((resolve, reject) => {
                            const timeout = setTimeout(() => reject('timeout'), 2000);
                            page.objs.get(imgName, (obj: any) => {
                                clearTimeout(timeout);
                                resolve(obj);
                            });
                        });
                        if (imgData?.width && imgData?.height) {
                            const dpiW = Math.round(imgData.width / pageWidthInches);
                            const dpiH = Math.round(imgData.height / pageHeightInches);
                            maxDpi = Math.max(maxDpi, dpiW, dpiH);
                        }
                    } catch { /* skip unresolvable images */ }
                }
            }

            pdf.destroy();

            const detectedDpi = Math.min(maxDpi, 600);
            this.originalDpi.set(detectedDpi);
            this.dpi.set(Math.min(150, detectedDpi));
        } catch (err) {
            console.error('DPI detection error:', err);
            this.originalDpi.set(300);
            this.dpi.set(150);
        } finally {
            this.isDetectingDpi.set(false);
        }
    }

    async compress() {
        const file = this.file();
        if (!file) return;

        this.isProcessing.set(true);
        this.elapsedSeconds.set(0);
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds.update(s => s + 1);
        }, 1000);

        const formData = new FormData();
        formData.append('file', file, file.name);
        formData.append('dpi', this.dpi().toString());

        try {
            const response = await fetch(`${environment.apiUrl}/pdf/compress`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error('Compress failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${file.name.replace('.pdf', '')}_compressed.pdf`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF compress error:', error);
        } finally {
            clearInterval(this.timerInterval);
            this.isProcessing.set(false);
        }
    }

    formatSize(bytes: number): string {
        return formatFileSize(bytes);
    }
}
