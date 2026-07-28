import { defineConfig } from 'vite';

export default defineConfig({
  // Keep production assets relative so the build also works when opened from disk.
  base: './',
  build: {
    rollupOptions: {
      input: 'app.html',
    },
  },
});
