import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://47.96.133.238:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://47.96.133.238:8000',
        changeOrigin: true,
      },
    },
  },
})
