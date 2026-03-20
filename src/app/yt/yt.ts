import { Component, signal } from '@angular/core';
import { environment } from '../../environments/environment';

@Component({
    selector: 'app-yt',
    standalone: true,
    templateUrl: './yt.html',
    styleUrl: './yt.css'
})
export class YtComponent {
    url = signal('');
    isProcessing = signal(false);
    elapsedSeconds = signal(0);
    private timerInterval: any;

    onUrlChange(event: Event) {
        const val = (event.target as HTMLInputElement).value;
        this.url.set(val);
    }

    async download() {
        const link = this.url();
        if (!link) return;

        this.isProcessing.set(true);
        this.elapsedSeconds.set(0);
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds.update(s => s + 1);
        }, 1000);

        try {
            const response = await fetch(`${environment.apiUrl}/yt/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: link })
            });

            if (!response.ok) throw new Error('Download failed');

            // Try to extract filename from Content-Disposition header if possible
            let filename = 'youtube_download.mp4';
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

            // Clear input after successful download
            this.url.set('');
        } catch (error) {
            console.error('YouTube download error:', error);
            // Optionally, we could add an errorMessage signal here
        } finally {
            clearInterval(this.timerInterval);
            this.isProcessing.set(false);
        }
    }
}
