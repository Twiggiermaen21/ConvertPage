import { Component, signal, computed, output } from '@angular/core';
import { CdkDrag, CdkDragDrop, CdkDropList, moveItemInArray } from '@angular/cdk/drag-drop';
import { PdfPage, formatFileSize } from '../pdf-shared';
import { environment } from '../../../environments/environment';

type MergeStep = 'upload' | 'reorder';

@Component({
    selector: 'app-merge-tool',
    standalone: true,
    imports: [CdkDropList, CdkDrag],
    templateUrl: './merge.html',
    styleUrl: './merge.css'
})
export class MergeToolComponent {
    back = output<void>();

    files = signal<File[]>([]);
    pages = signal<PdfPage[]>([]);
    step = signal<MergeStep>('upload');
    isProcessing = signal(false);
    elapsedSeconds = signal(0);
    private timerInterval: any;
    isLoadingPages = signal(false);

    totalSize = computed(() => {
        const bytes = this.files().reduce((sum, f) => sum + f.size, 0);
        return formatFileSize(bytes);
    });

    onFilesSelected(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files?.length) {
            const pdfFiles = Array.from(input.files).filter(f => f.type === 'application/pdf');
            this.files.update(c => [...c, ...pdfFiles]);
            input.value = '';
        }
    }

    onDragOver(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
    }

    onDropFiles(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        const dropped = event.dataTransfer?.files;
        if (dropped?.length) {
            const pdfFiles = Array.from(dropped).filter(f => f.type === 'application/pdf');
            this.files.update(c => [...c, ...pdfFiles]);
        }
    }

    removeFile(index: number, event: Event) {
        event.stopPropagation();
        this.files.update(c => c.filter((_, i) => i !== index));
    }

    async goToReorder() {
        if (this.files().length === 0) return;
        this.step.set('reorder');
        this.isLoadingPages.set(true);

        try {
            const pdfjsLib = await import('pdfjs-dist');
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'assets/pdf.worker.min.mjs';

            const allPages: PdfPage[] = [];
            const files = this.files();

            for (let fi = 0; fi < files.length; fi++) {
                const file = files[fi];
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise;

                for (let pi = 1; pi <= pdf.numPages; pi++) {
                    const page = await pdf.getPage(pi);
                    const viewport = page.getViewport({ scale: 0.4 });
                    const canvas = document.createElement('canvas');
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;
                    const ctx = canvas.getContext('2d')!;

                    await page.render({ canvasContext: ctx, viewport, canvas } as any).promise;

                    allPages.push({ thumbnail: canvas.toDataURL('image/jpeg', 0.7), pageNum: pi, sourceFile: file.name, fileIndex: fi });
                }
            }
            this.pages.set(allPages);
        } catch (err) {
            console.error('Error extracting pages:', err);
        } finally {
            this.isLoadingPages.set(false);
        }
    }

    onPageReorder(event: CdkDragDrop<PdfPage[]>) {
        const updated = [...this.pages()];
        moveItemInArray(updated, event.previousIndex, event.currentIndex);
        this.pages.set(updated);
    }

    goBack() {
        this.step.set('upload');
    }

    async merge() {
        this.isProcessing.set(true);
        this.elapsedSeconds.set(0);
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds.update(s => s + 1);
        }, 1000);

        const formData = new FormData();
        const allFiles = this.files();
        const orderedPages = this.pages();

        // Build a new file order based on the sequence pages appear in the reordered list
        const oldToNewIndex = new Map<number, number>();
        const orderedFiles: File[] = [];
        for (const page of orderedPages) {
            if (!oldToNewIndex.has(page.fileIndex)) {
                oldToNewIndex.set(page.fileIndex, orderedFiles.length);
                orderedFiles.push(allFiles[page.fileIndex]);
            }
        }

        // Append files in the reordered sequence
        orderedFiles.forEach(f => formData.append('files', f, f.name));

        // Remap fileIndex in page_order to match the new file order
        const pageOrder = orderedPages.map(p => ({
            fileIndex: oldToNewIndex.get(p.fileIndex)!,
            pageNum: p.pageNum
        }));
        formData.append('page_order', JSON.stringify(pageOrder));

        try {
            const response = await fetch(`${environment.apiUrl}/pdf/merge`, { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Merge failed');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'merged.pdf';
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF merge error:', error);
        } finally {
            clearInterval(this.timerInterval);
            this.isProcessing.set(false);
        }
    }

    formatSize(bytes: number): string {
        return formatFileSize(bytes);
    }
}
