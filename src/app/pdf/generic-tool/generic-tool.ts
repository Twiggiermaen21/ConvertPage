import { Component, signal, input, output } from '@angular/core';
import { PdfTool, ToolDef, PDF_TOOLS, formatFileSize } from '../pdf-shared';

@Component({
    selector: 'app-generic-tool',
    standalone: true,
    templateUrl: './generic-tool.html',
    styleUrl: './generic-tool.css'
})
export class GenericToolComponent {
    toolId = input.required<PdfTool>();
    back = output<void>();

    file = signal<File | null>(null);
    isProcessing = signal(false);

    get toolDef(): ToolDef {
        return PDF_TOOLS.find(t => t.id === this.toolId())!;
    }

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
            if (pdf) this.file.set(pdf);
        }
    }

    async process() {
        const tool = this.toolId();
        const file = this.file();
        if (!file) return;

        this.isProcessing.set(true);
        const formData = new FormData();
        formData.append('file', file, file.name);

        try {
            const response = await fetch(`http://localhost:8000/api/pdf/${tool}`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error(`${tool} failed`);

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${file.name.replace('.pdf', '')}_${tool}.pdf`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error(`PDF ${tool} error:`, error);
        } finally {
            this.isProcessing.set(false);
        }
    }

    formatSize(bytes: number): string {
        return formatFileSize(bytes);
    }
}
