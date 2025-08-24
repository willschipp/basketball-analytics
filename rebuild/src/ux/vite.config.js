import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { mockDevServerPlugin } from 'vite-plugin-mock-dev-server'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(), 
    mockDevServerPlugin()
  ],
  resolve: {
    alias: {
      '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
    }
  },
  server: {
    proxy: {
      '^/api': 'http://example.com', // This proxy prefix enables `/api` mock interception
    },
  },  
})
