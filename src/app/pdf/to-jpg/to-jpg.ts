import { Component, signal, output } from '@angular/core';
import { formatFileSize } from '../pdf-shared';

@Component({
    selector: 'app-to-jpg-tool',
    standalone: true,
    templateUrl: './to-jpg.html',
    styleUrl: './to-jpg.css'
})
export class ToJpgToolComponent {
    back = output<void>();

    file = signal<File | null>(null);
    isProcessing = signal(false);
    elapsedSeconds = signal(0);
    private timerInterval: any;

    onFileSelected(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files?.length) {
            this.file.set(input.files[0]);
            input.value = '';
        }
    }

    removeFile(event: Event) {
        event.stopPropagation();
        this.file.set(null);
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
            }
        }
    }

    async convert() {
        const file = this.file();
        if (!file) return;

        this.isProcessing.set(true);
        this.elapsedSeconds.set(0);
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds.update(s => s + 1);
        }, 1000);

        const formData = new FormData();
        formData.append('file', file, file.name);

        try {
            const response = await fetch('http://localhost:8000/api/pdf/to-jpg', {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error('Conversion failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // Endpoint returns a ZIP with images
            a.download = `${file.name.replace('.pdf', '')}_images.zip`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('PDF to JPG error:', error);
        } finally {
            clearInterval(this.timerInterval);
            this.isProcessing.set(false);
        }
    }

    formatSize(bytes: number): string {
        return formatFileSize(bytes);
    }
}
