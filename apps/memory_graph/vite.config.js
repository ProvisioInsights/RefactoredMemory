import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
export default defineConfig({
  plugins: [viteSingleFile()],
  build: { outDir: '../../refactoredmemory/ui', emptyOutDir: false,
    rollupOptions: { input: 'graph.html', output: { entryFileNames: 'graph.js' } } },
});
