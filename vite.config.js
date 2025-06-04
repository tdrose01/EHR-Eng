import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8081,
    proxy: {
      '/api/patients': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/api/dashboard': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Dashboard Request to Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Dashboard Response from Target:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/api/records': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
        }
      },
      '/api/vaccines': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
        }
      },
      '/api/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
}) 