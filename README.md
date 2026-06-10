# Reshot

A rephotography app for recreating old photos and memories.

## Project Structure

```text
reshot/
  frontend/          React + Vite app
  backend/           FastAPI app
  assets/            Fixed photos, frame templates, and dummy captures
  captures/          Per-session capture originals
  output/sessions/   Generated session outputs
  docs/              Camera setup and operations notes
```

## Prerequisites

- Node.js 22 or newer
- npm 10 or newer
- Python 3.13 or newer

## Environment

Copy the example file before running locally:

```powershell
Copy-Item .env.example .env
Copy-Item frontend\.env.example frontend\.env
```

The frontend reads `VITE_API_BASE_URL`. The backend reads `FRONTEND_ORIGINS`,
`PUBLIC_BASE_URL`, storage paths, and `CAMERA_MODE` from `.env`.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response includes:

```json
{
  "app": "reshot",
  "status": "ok"
}
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The page calls the backend health endpoint using
`VITE_API_BASE_URL` or `http://localhost:8000` by default.

## Phase 2 Image Composition

The default frame template is `assets/frames/default.json`.

- Final canvas: `1200 x 1854`
- Background: `#000000`
- Optional logo: `assets/frames/mpnu-logo.png`
- Optional overlay: `assets/frames/default_overlay.png`
- Old photos: `assets/old-photos/old_1.jpg`, `assets/old-photos/old_2.jpg`
- Current photos: `captures/{session_id}/current_1.jpg`, `captures/{session_id}/current_2.jpg`
- Output: `output/sessions/{session_id}/final.jpg`

Run the Phase 2 demo composition from the backend directory:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.scripts.compose_demo --create-samples
```

The demo command creates missing sample inputs for the `demo` session and writes:

```text
output/sessions/demo/final.jpg
```

Use `--overwrite-samples` to regenerate the demo inputs. Logo and overlay files are optional; if they are absent, composition continues without them.

## Phase 3 Session Lookup

Phase 3 stores session metadata next to the composed image:

```text
output/sessions/{session_id}/session.json
output/sessions/{session_id}/final.jpg
```

Each `session.json` includes `session_id`, `created_at`, `updated_at`, `status`,
`template_id`, `final_image_path`, `old_photos`, and `captures`.

Create or refresh the `demo` session from the backend directory:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.scripts.compose_demo --create-samples
```

Start the backend API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify session metadata:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/sessions/demo
```

Verify the final image response:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/sessions/demo/image -OutFile ..\output\sessions\demo\api-final.jpg
```

Expected files:

```text
output/sessions/demo/session.json
output/sessions/demo/final.jpg
```

Missing sessions and missing final images return `404`. Invalid session IDs are
rejected to prevent path traversal.

## Phase 4 QR Code Generation

Phase 4 stores a QR PNG next to the composed image:

```text
output/sessions/{session_id}/qr.png
```

The QR content is the public result-image URL:

```text
{PUBLIC_BASE_URL}/sessions/{session_id}/image
```

For local verification, set `PUBLIC_BASE_URL=http://127.0.0.1:8000` in `.env`
or rely on the default `http://localhost:8000`.

Create or refresh the `demo` session and install dependencies:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.scripts.compose_demo --create-samples
```

Start the backend API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Generate or regenerate the demo QR:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/sessions/demo/qr
```

Expected metadata includes:

```json
{
  "session_id": "demo",
  "qr_image_path": "output/sessions/demo/qr.png"
}
```

Download the QR image through the API:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/sessions/demo/qr -OutFile ..\output\sessions\demo\api-qr.png
```

Expected files:

```text
output/sessions/demo/session.json
output/sessions/demo/final.jpg
output/sessions/demo/qr.png
```

`POST /sessions/{session_id}/compose` also generates QR after a successful
composition. Missing sessions, missing final images, and missing QR images
return `404`. Invalid session IDs are rejected to prevent path traversal.

## Phase 5 MVP Shooting UI

Phase 5 adds the operator-facing shooting flow. It uses `CAMERA_MODE=dummy` and
creates current images at:

```text
captures/{session_id}/current_1.jpg
captures/{session_id}/current_2.jpg
```

The shooting page shows all four frames from the start. Old photo 1 and old
photo 2 are already filled, and the operator captures only current photo 1 and
current photo 2.

The frontend flow is:

```text
Start new shoot -> Capture current 1 -> Capture current 2 -> Compose result -> /result/{session_id}
```

The separate result page displays `final.jpg`, `qr.png`, and buttons to return
to shooting or start a new shoot.

Start the backend for local development:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and run the shooting flow. A successful compose
creates:

```text
output/sessions/{session_id}/final.jpg
output/sessions/{session_id}/qr.png
```

Useful API checks:

```powershell
$session = Invoke-RestMethod -Method Post http://127.0.0.1:8000/sessions -ContentType "application/json" -Body '{"template_id":"default"}'
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/capture" -ContentType "application/json" -Body '{"slot":1}'
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/capture" -ContentType "application/json" -Body '{"slot":2}'
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/compose" -ContentType "application/json" -Body '{"template_id":"default"}'
Invoke-WebRequest "http://127.0.0.1:8000/sessions/$($session.session_id)/image" -OutFile "..\output\sessions\$($session.session_id)\api-final.jpg"
Invoke-WebRequest "http://127.0.0.1:8000/sessions/$($session.session_id)/qr" -OutFile "..\output\sessions\$($session.session_id)\api-qr.png"
```

The existing `demo` session is still valid for Phase 2-4 verification:

```powershell
cd backend
python -m app.scripts.compose_demo --create-samples
Invoke-RestMethod -Method Post http://127.0.0.1:8000/sessions/demo/qr
```

### Hotspot/LAN QR Verification

Use this when participant phones need to scan the QR from the event network.

1. Turn on your phone hotspot.
2. Connect the laptop to that hotspot.
3. Connect participant phones to the same hotspot.
4. On the laptop, run `ipconfig` and find the Wi-Fi IPv4 address.
5. Set the backend public URL in `.env`:

```text
PUBLIC_BASE_URL=http://{노트북_IP}:8000
FRONTEND_ORIGINS=http://localhost:5173,http://{노트북_IP}:5173
```

6. Set the frontend API URL in `frontend/.env`:

```text
VITE_API_BASE_URL=http://{노트북_IP}:8000
```

7. Start the backend on all interfaces:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

8. Start the frontend:

```powershell
cd frontend
npm run dev
```

9. From a participant phone, open `http://{노트북_IP}:8000/health`. It should
   return the backend health response.
10. Run a new shooting flow in the frontend. After compose, scan the QR from a
    participant phone and confirm the final image opens. If `PUBLIC_BASE_URL`
    changes, regenerate the QR by composing again or calling:

```powershell
Invoke-RestMethod -Method Post http://{노트북_IP}:8000/sessions/{session_id}/qr
```

## Current Scope

Implemented in this setup:

- React/Vite frontend scaffold in `frontend/`
- FastAPI backend scaffold in `backend/`
- `GET /` and `GET /health`
- CORS configuration for the local frontend
- `.env.example`
- Initial storage and asset directories
- Pillow-based Phase 2 image composition for the default 2x2 frame
- Demo composition script that can generate sample inputs
- File-backed Phase 3 session metadata lookup
- `GET /sessions/{session_id}`
- `GET /sessions/{session_id}/image`
- `POST /sessions/{session_id}/compose` for local verification
- File-backed Phase 4 QR generation
- `POST /sessions/{session_id}/qr`
- `GET /sessions/{session_id}/qr`
- Phase 5 dummy capture flow
- `POST /sessions`
- `POST /sessions/{session_id}/capture`
- `GET /sessions/{session_id}/capture/{slot}`
- React shooting UI with final image and QR display

Not implemented yet:

- Nikon direct control or watch-folder capture flow
- Gallery UI and download-specific API
- Admin UI
