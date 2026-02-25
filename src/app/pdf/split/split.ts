import { Component, signal, computed, output } from '@angular/core';
import { CdkDrag, CdkDragDrop, CdkDropList, CdkDropListGroup, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { PdfPage, formatFileSize } from '../pdf-shared';

type SplitStep = 'upload' | 'arenas';

interface Arena {
    id: number;
    label: string;
    pages: PdfPage[];
}

@Component({
    selector: 'app-split-tool',
    standalone: true,
    imports: [CdkDropList, CdkDrag, CdkDropListGroup],
    templateUrl: './split.html',
    styleUrl: './split.css'
})
export class SplitToolComponent {
    back = output<void>();

    file = signal<File | null>(null);
    step = signal<SplitStep>('upload');
    isLoadingPages = signal(false);
    isProcessing = signal(false);
    arenas = signal<Arena[]>([]);
    private nextArenaId = 1;

    fileSize = computed(() => {
        const f = this.file();
        return f ? formatFileSize(f.size) : '';
    });

    onFileSelected(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files?.length) {
            const pdf = Array.from(input.files).find(f => f.type === 'application/pdf');
            if (pdf) this.file.set(pdf);
            input.value = '';
        }
    }

    onDragOver(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
    }

    onDropFile(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        const dropped = event.dataTransfer?.files;
        if (dropped?.length) {
            const pdf = Array.from(dropped).find(f => f.type === 'application/pdf');
            if (pdf) this.file.set(pdf);
        }
    }

    removeFile(event: Event) {
        event.stopPropagation();
        this.file.set(null);
    }

    async goToArenas() {
        const f = this.file();
        if (!f) return;
        this.step.set('arenas');
        this.isLoadingPages.set(true);

        try {
            const pdfjsLib = await import('pdfjs-dist');
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'assets/pdf.worker.min.mjs';

            const arrayBuffer = await f.arrayBuffer();
            const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise;

            const allPages: PdfPage[] = [];
            for (let pi = 1; pi <= pdf.numPages; pi++) {
                const page = await pdf.getPage(pi);
                const viewport = page.getViewport({ scale: 0.4 });
                const canvas = document.createElement('canvas');
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                const ctx = canvas.getContext('2d')!;
                await page.render({ canvasContext: ctx, viewport, canvas } as any).promise;
                allPages.push({
                    thumbnail: canvas.toDataURL('image/jpeg', 0.7),
                    pageNum: pi,
                    sourceFile: f.name,
                    fileIndex: 0
                });
            }

            this.nextArenaId = 1;
            this.arenas.set([
                { id: this.nextArenaId++, label: 'Dokument 1', pages: allPages },
                { id: this.nextArenaId++, label: 'Dokument 2', pages: [] }
            ]);
        } catch (err) {
            console.error('Error extracting pages:', err);
        } finally {
            this.isLoadingPages.set(false);
        }
    }

    getDropListIds(): string[] {
        return this.arenas().map(a => 'arena-' + a.id);
    }

    onPageDrop(event: CdkDragDrop<PdfPage[]>) {
        if (event.previousContainer === event.container) {
            moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
        } else {
            transferArrayItem(event.previousContainer.data, event.container.data, event.previousIndex, event.currentIndex);
        }
        // Trigger signal update
        this.arenas.update(a => [...a]);
    }

    addArena() {
        this.arenas.update(a => [
            ...a,
            { id: this.nextArenaId++, label: `Dokument ${a.length + 1}`, pages: [] }
        ]);
    }

    removeArena(arenaId: number) {
        this.arenas.update(arenas => {
            const target = arenas.find(a => a.id === arenaId);
            if (!target) return arenas;
            const remaining = arenas.filter(a => a.id !== arenaId);
            // Move pages back to the first arena
            if (remaining.length > 0 && target.pages.length > 0) {
                remaining[0] = {
                    ...remaining[0],
                    pages: [...remaining[0].pages, ...target.pages]
                };
            }
            return remaining;
        });
    }

    goBack() {
        this.step.set('upload');
    }

    hasNonEmptyArenas(): boolean {
        return this.arenas().filter(a => a.pages.length > 0).length >= 2;
    }

    async split() {
        this.isProcessing.set(true);
        const f = this.file();
        if (!f) return;

        const formData = new FormData();
        formData.append('file', f, f.name);

        const splitConfig = this.arenas()
            .filter(a => a.pages.length > 0)
            .map((a, i) => ({
                label: a.label,
                pages: a.pages.map(p => p.pageNum)
            }));
        formData.append('split_config', JSON.stringify(splitConfig));

        try {
            const response = await fetch('http://localhost:8000/api/pdf/split', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Split failed');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'split_output.zip';
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF split error:', error);
        } finally {
            this.isProcessing.set(false);
        }
    }

    formatSize(bytes: number): string {
        return formatFileSize(bytes);
    }
}
