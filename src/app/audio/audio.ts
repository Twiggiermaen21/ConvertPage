import { Component, signal } from '@angular/core';
import { environment } from '../../environments/environment';

@Component({
    selector: 'app-audio',
    standalone: true,
    templateUrl: './audio.html',
    styleUrl: './audio.css'
})
export class AudioComponent {
    selectedFile = signal<File | null>(null);
    targetFormat = signal<'mp3' | 'wav' | 'm4a'>('mp3');
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
            this.selectedFile.set(files[0]);
        }
    }

    removeFile(event: Event) {
        event.stopPropagation();
        this.selectedFile.set(null);
    }

    setFormat(fmt: 'mp3' | 'wav' | 'm4a') {
        this.targetFormat.set(fmt);
    }

    async convert() {
        const file = this.selectedFile();
        if (!file) return;

        this.isProcessing.set(true);
        this.elapsedSeconds.set(0);
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds.update(s => s + 1);
        }, 1000);

        const formData = new FormData();
        formData.append('file', file, file.name);
        formData.append('target_format', this.targetFormat());

        try {
            const response = await fetch(`${environment.apiUrl}/audio/convert`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Konwersja audio nie powiodła się');

            // Default filename handling
            let filename = `converted_${file.name.split('.')[0]}.${this.targetFormat()}`;
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
            console.error('Audio conversion error:', error);
        } finally {
            clearInterval(this.timerInterval);
            this.isProcessing.set(false);
        }
    }
}
