import { Component, signal } from '@angular/core';
import { PdfTool, ToolDef, PDF_TOOLS } from './pdf-shared';
import { MergeToolComponent } from './merge/merge';
import { SplitToolComponent } from './split/split';
import { GenericToolComponent } from './generic-tool/generic-tool';

@Component({
    selector: 'app-pdf',
    standalone: true,
    imports: [MergeToolComponent, SplitToolComponent, GenericToolComponent],
    templateUrl: './pdf.html',
    styleUrl: './pdf.css'
})
export class PdfComponent {
    selectedTool = signal<PdfTool | null>(null);
    tools = PDF_TOOLS;

    selectTool(tool: PdfTool) {
        this.selectedTool.set(tool);
    }

    goToMenu() {
        this.selectedTool.set(null);
    }
}
