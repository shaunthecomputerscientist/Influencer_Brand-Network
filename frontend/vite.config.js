import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  server: {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'ssl-certificates/selfsigned.key')),
      cert: fs.readFileSync(path.resolve(__dirname, 'ssl-certificates/selfsigned.crt')),
    },
    host: '0.0.0.0',  // To make it accessible over the network       
    port: 5173 // Port number for Vite
  },
  optimizeDeps: {
    include: ["plotly.js-dist"], // Ensure Plotly is pre-bundled
  },
})
