import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    proxy: {
      // In dev, forward /api/* requests to the Flask backend.
      // This avoids CORS issues while developing locally.
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
    },
  },

  build: {
    // Output goes to dist/ — Vercel will serve from here
    outDir: 'dist',
  },
})
