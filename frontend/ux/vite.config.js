import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { mockDevServerPlugin } from 'vite-plugin-mock-dev-server'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(), 
    mockDevServerPlugin()
  ],
  build: {
    outDir: resolve(__dirname, '../../server/src/ux/dist'),
    emptyOutDir: true // ensures old builds are cleared
  },
  resolve: {
    alias: {
      '~bootstrap': resolve(__dirname, 'node_modules/bootstrap'),
    }
  },
  server: {
    proxy: {
      '^/api': 'http://example.com',
    },
  },  
})
