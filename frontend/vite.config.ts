import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: [
      '@univerjs/core',
      '@univerjs/design',
      '@univerjs/engine-formula',
      '@univerjs/engine-render',
      '@univerjs/sheets',
      '@univerjs/sheets-formula',
      '@univerjs/sheets-ui',
      '@univerjs/ui',
      '@univerjs/docs',
      '@univerjs/docs-ui',
    ],
  },
});
