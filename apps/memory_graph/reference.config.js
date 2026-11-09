import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
export default defineConfig({root:'reference',plugins:[viteSingleFile()],build:{outDir:'../.reference-host',emptyOutDir:true}});
