import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  // **AÑADE ESTA LÍNEA:** // Esto le dice a Vite que la aplicación está alojada en la raíz del servidor.
  base: '/',
  
  plugins: [react()],
})