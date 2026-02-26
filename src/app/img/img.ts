import { Component, signal } from '@angular/core';

@Component({
    selector: 'app-img',
    standalone: true,
    templateUrl: './img.html',
    styleUrl: './img.css'
})
export class ImgComponent {
    selectedFile = signal<File | null>(null);
    isProcessing = signal(false);
    elapsedSeconds = signal(0);
    private timerInterval: any;

    onFileSelected(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files?.length) {
            this.selectedFile.set(input.files[0]);
        }
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
            const img = Array.from(files).find(f => f.type.startsWith('image/'));
            if (img) {
                this.selectedFile.set(img);
            }
        }
    }

    removeFile(event: Event) {
        event.stopPropagation();
        this.selectedFile.set(null);
    }

    async removeBackground() {
        const file = this.selectedFile();
        if (!file) return;

        this.isProcessing.set(true);
        this.elapsedSeconds.set(0);
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds.update(s => s + 1);
        }, 1000);

        const formData = new FormData();
        formData.append('file', file, file.name);

        try {
            const response = await fetch('http://localhost:8000/api/image/remove-background', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Usuwanie tła nie powiodło się');

            // Default filename handling
            let filename = `nobg_${file.name.split('.')[0]}.png`;
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            const blob = await response.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(blobUrl);

        } catch (error) {
            console.error('Image processing error:', error);
        } finally {
            clearInterval(this.timerInterval);
            this.isProcessing.set(false);
        }
    }
}
