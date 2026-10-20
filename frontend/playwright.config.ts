import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './e2e', timeout: 90000, workers: 1,
  use: { baseURL: 'http://localhost:5173', channel: 'msedge', headless: true },
  webServer: [
    { command: '..\\.venv\\Scripts\\python.exe -m uvicorn api.main:app --app-dir .. --host 127.0.0.1 --port 8001', url: 'http://127.0.0.1:8001', reuseExistingServer: true, timeout: 90000 },
    { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: true },
  ],
})
