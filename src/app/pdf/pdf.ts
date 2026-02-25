import { Component, signal } from '@angular/core';

@Component({
    selector: 'app-pdf',
    standalone: true,
    templateUrl: './pdf.html',
    styleUrl: './pdf.css'
})

export class PdfComponent {
    selectedFile = signal<File | null>(null);

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
}
