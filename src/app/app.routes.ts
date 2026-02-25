import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: '', redirectTo: 'pdf', pathMatch: 'full' },
    {
        path: 'pdf',
        loadComponent: () => import('./pdf/pdf').then(m => m.PdfComponent)
    },
    {
        path: 'audio',
        loadComponent: () => import('./audio/audio').then(m => m.AudioComponent)
    },
    {
        path: 'yt',
        loadComponent: () => import('./yt/yt').then(m => m.YtComponent)
    }
];
