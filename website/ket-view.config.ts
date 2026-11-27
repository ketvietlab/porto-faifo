import { defineConfig } from '@ketvietlab/ketjs-view-tools'

export default defineConfig({
  base: './',
  styles: ['src/styles/site.css', 'src/styles/demos.css'],
  islands: {
    specimen: 'src/islands/specimen.ts',
    symbols: 'src/islands/symbols.ts',
    dashboard: 'src/islands/dashboard.ts',
    'mono-demo': 'src/islands/mono-demo.ts',
  },
})
