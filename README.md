# GigSurance

GigSurance is a full-stack insurance risk and payments platform.

## Repository structure

- `backend/` – FastAPI backend with risk engine, fraud detection, premium scheduling, and payment integrations.
- `Frontend/` – Vite + React + TypeScript frontend UI.

## Setup

### Backend

1. Create a Python virtual environment:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Run the backend server:
   ```powershell
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. Install dependencies:
   ```powershell
   cd Frontend
   npm install
   ```
2. Run the frontend app:
   ```powershell
   npm run dev
   ```

## Testing

- Backend tests:
  ```powershell
  cd backend
  pytest
  ```
- Frontend tests:
  ```powershell
  cd Frontend
  npm test
  ```

## GitHub readiness

This repository includes a root `.gitignore` for Python and frontend artifacts, and a GitHub Actions workflow for CI.

## Notes

- Keep `backend/venv/` and `Frontend/node_modules/` out of source control.
- Use `.env` files locally when needed, but do not commit them.
