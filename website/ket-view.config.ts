import { defineConfig } from '@ketvietlab/ketjs-view-tools'

export default defineConfig({
  base: './',
  styles: ['src/styles/site.css'],
  islands: {
    specimen: 'src/islands/specimen.ts',
    symbols: 'src/islands/symbols.ts',
  },
})
