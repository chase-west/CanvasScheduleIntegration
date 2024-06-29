import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    https: {
      key: '../../backend/certs/key.pem',
      cert: '../../backend/certs/cert.pem',
    },
  },
  plugins: [react()],
});