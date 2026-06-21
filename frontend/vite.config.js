import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Note: in production deployment (Vercel/Netlify), HTTPS is provided
// automatically by the host — no manual cert setup needed. The basicSsl
// plugin was only used for local network testing on your phone before
// deployment; it's not needed here anymore.
export default defineConfig({
  plugins: [react()],
})
