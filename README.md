<div align="center">

# Reshot

**현장 포토부스용 4컷 사진 촬영 앱**

8장의 현재 사진을 촬영한 뒤 마음에 드는 4장을 골라 세로형 4컷 결과 이미지를 만들고, QR 코드로 휴대폰에서 받을 수 있게 하는 로컬 서버 기반 앱입니다.

<br>

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vite.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## 기능

- **8장 연속 촬영**: 촬영 화면에서 5초 카운트다운 후 1번부터 8번까지 순서대로 촬영합니다.
- **라이브 프리뷰**: 브라우저 카메라 입력 또는 HDMI 캡처 장치를 선택해 구도를 확인합니다.
- **4장 선택 합성**: 촬영 완료 후 4컷 프레임의 각 영역을 누르고, 8장 중 원하는 사진을 골라 배치합니다.
- **세로형 최종 이미지**: 기본 템플릿은 `1200 x 1854` 캔버스와 `518 x 744` 사진 슬롯 4개를 사용합니다.
- **QR 공유**: 최종 이미지 URL을 담은 QR 이미지를 생성하고 결과 화면에서 모달로 표시합니다.
- **세션 기반 저장**: 촬영 원본, 최종 이미지, QR, 메타데이터를 세션별 폴더에 저장합니다.
- **Google Drive 업로드 옵션**: 설정을 켜면 최종 이미지를 지정한 Drive 폴더에 업로드하고, QR이 Drive 공유 링크를 가리키게 할 수 있습니다.
- **카메라 모드 분리**: `dummy`와 `watch_folder` 모드를 구현했으며, Nikon 직접 제어는 어댑터 자리만 준비되어 있습니다.

---

## 빠른 시작

### 1. 의존성 설치

PowerShell 기준입니다.

```powershell
cd C:\Users\kyle0\Develops\reshot

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

cd ..\frontend
npm install
```

PowerShell 실행 정책 때문에 가상환경 활성화가 막히면 현재 터미널에서만 완화합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. 환경 파일 준비

```powershell
cd C:\Users\kyle0\Develops\reshot
Copy-Item .env.example .env
Copy-Item frontend\.env.example frontend\.env
```

기본 개발 모드는 `CAMERA_MODE=dummy`입니다. 실제 카메라 연결 없이도 세션 생성, 촬영 더미 생성, 4장 선택, 합성, QR 흐름을 확인할 수 있습니다.

### 3. 서버 실행

터미널을 2개 열고 각각 실행합니다.

```powershell
cd C:\Users\kyle0\Develops\reshot\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd C:\Users\kyle0\Develops\reshot\frontend
npm run dev
```

브라우저에서 `http://localhost:5173`을 엽니다.

---

## 사용 흐름

### 화면 경로

| 경로 | 역할 |
| --- | --- |
| `http://localhost:5173/` | 시작 화면 |
| `http://localhost:5173/shoot` | 촬영 및 4장 선택 화면 |
| `http://localhost:5173/result/{session_id}` | 최종 이미지와 QR 버튼 화면 |

### 기본 플로우

```text
Start
  -> 세션 생성
  -> /shoot 이동
  -> 프리뷰 소스 선택
  -> 5초 카운트다운 후 1~8번 사진 연속 촬영
  -> 4컷 프레임의 각 칸 선택
  -> 8장 중 원하는 사진을 각 칸에 배치
  -> Save final
  -> final.jpg + qr.png 생성
  -> /result/{session_id} 이동
  -> QR 보기 또는 처음으로 이동
```

촬영 중에는 프리뷰 영역에 브라우저 카메라 또는 캡처 장치 입력이 표시됩니다. 프리뷰는 구도 확인용이며, 최종 합성에는 백엔드 카메라 모드가 저장한 JPEG 파일을 사용합니다.

---

## 카메라 모드

### `dummy`

기본값입니다. 실제 카메라 없이 slot별 샘플 이미지를 복사하거나 fallback 이미지를 생성합니다.

```text
CAMERA_MODE=dummy
```

### `watch_folder`

Nikon NX Tether, digiCamControl, 카메라 제조사 유틸리티처럼 촬영 파일을 특정 폴더에 저장하는 프로그램과 함께 쓰는 모드입니다.

```text
CAMERA_MODE=watch_folder
CAMERA_WATCH_DIR=C:\Users\kyle0\Pictures\ReshotTether
CAMERA_CAPTURE_TIMEOUT_SECONDS=20
CAMERA_TRIGGER_COMMAND=powershell -ExecutionPolicy Bypass -File "C:\Users\kyle0\Develops\reshot\tools\trigger_nx_tether.ps1"
CAMERA_TRIGGER_TIMEOUT_SECONDS=5
```

동작 방식:

1. 촬영 요청이 들어오면 감시 폴더의 기존 JPG 목록을 기억합니다.
2. `CAMERA_TRIGGER_COMMAND`가 있으면 먼저 실행합니다.
3. 새 JPG 또는 촬영 시작 시점 이후 갱신된 JPG를 기다립니다.
4. 파일 크기와 수정 시간이 안정되면 `captures/{session_id}/current_{slot}.jpg`로 복사합니다.

`tools/trigger_nx_tether.ps1`은 실행 중인 NX Tether 창을 찾아 앞으로 가져온 뒤 `Ctrl+1`을 보내는 보조 스크립트입니다. NX Tether 단축키 설정이 다르면 스크립트의 `SendKeys` 값을 조정해야 합니다.

### 프리뷰 소스

프리뷰는 프론트엔드에서 `navigator.mediaDevices.getUserMedia`로 처리합니다. 운영 PC에서는 `http://localhost:5173`에서 실행하는 것이 가장 안정적입니다. 브라우저는 보통 `localhost` 또는 HTTPS가 아닌 일반 LAN HTTP 주소에서 카메라 권한을 제한합니다.

---

## 로컬 네트워크 QR 테스트

휴대폰에서 QR을 열려면 QR URL에 `localhost`가 아니라 서버 PC의 Wi-Fi 또는 핫스팟 IP가 들어가야 합니다.

1. 노트북과 휴대폰을 같은 Wi-Fi 또는 핫스팟에 연결합니다.
2. 노트북에서 `ipconfig`를 실행해 Wi-Fi IPv4 주소를 확인합니다.
3. 루트 `.env`를 수정합니다.

```text
PUBLIC_BASE_URL=http://{노트북_IP}:8000
FRONTEND_ORIGINS=http://localhost:5173,http://{노트북_IP}:5173
```

4. `frontend/.env`를 수정합니다.

```text
VITE_API_BASE_URL=http://{노트북_IP}:8000
```

5. 백엔드를 모든 인터페이스에서 실행합니다.

```powershell
cd C:\Users\kyle0\Develops\reshot\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

6. 휴대폰에서 `http://{노트북_IP}:8000/health`가 열리는지 확인합니다.

프리뷰를 쓰는 운영 화면은 PC의 `localhost:5173`에서 열고, QR을 스캔하는 휴대폰은 백엔드의 최종 이미지 URL만 열면 됩니다.

---

## Google Drive 공유 옵션

기본값은 로컬 백엔드 이미지 URL을 QR에 넣는 방식입니다. 행사장 네트워크 대신 Google Drive 공유 링크를 쓰고 싶으면 루트 `.env`에서 Drive 업로드를 켭니다.

```text
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID={Drive_폴더_ID}
GOOGLE_DRIVE_CREDENTIALS_FILE=secrets/google/credentials.json
GOOGLE_DRIVE_TOKEN_FILE=secrets/google/token.json
GOOGLE_DRIVE_SHARE_PUBLIC=true
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive
```

준비 절차:

1. Google Cloud에서 OAuth 클라이언트의 `credentials.json`을 내려받아 `secrets/google/credentials.json`에 둡니다.
2. 백엔드 가상환경을 활성화한 뒤 OAuth 토큰을 생성합니다.

```powershell
cd C:\Users\kyle0\Develops\reshot\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.google_drive_auth
```

3. `.env`의 `GOOGLE_DRIVE_FOLDER_ID`를 업로드 대상 폴더 ID로 설정합니다.
4. 서버를 재시작하고 `/health`의 `google_drive.enabled`, `folder_configured`, `share_public` 값을 확인합니다.

Drive 업로드가 켜진 상태에서 `POST /sessions/{session_id}/compose`를 호출하면 `final.jpg`를 업로드하거나 기존 Drive 파일을 갱신하고, 세션 메타데이터의 `drive_file_id`, `drive_share_url`, `qr_target_url`을 저장합니다. 이때 QR은 로컬 `/sessions/{session_id}/image`가 아니라 Drive 공유 링크를 담습니다.

`secrets/`는 `.gitignore`에 포함되어 있으므로 OAuth 자격 증명과 토큰은 저장소에 커밋하지 않습니다.

---

## 설정

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `APP_NAME` | `reshot` | FastAPI 앱 이름 |
| `ENVIRONMENT` | `development` | 실행 환경 이름 |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | QR에 들어갈 공개 백엔드 URL |
| `FRONTEND_ORIGINS` | `http://localhost:5173` | CORS 허용 프론트엔드 주소 목록 |
| `CAPTURES_DIR` | `captures` | 촬영 원본 저장 경로 |
| `OUTPUT_DIR` | `output/sessions` | 최종 이미지, QR, 세션 메타데이터 저장 경로 |
| `ASSETS_DIR` | `assets` | 프레임 템플릿과 고정 자산 경로 |
| `CAMERA_MODE` | `dummy` | `dummy` 또는 `watch_folder` |
| `CAMERA_WATCH_DIR` | 비어 있음 | `watch_folder` 모드에서 감시할 JPG 저장 폴더 |
| `CAMERA_CAPTURE_TIMEOUT_SECONDS` | `20` | 새 촬영 파일을 기다릴 최대 시간 |
| `CAMERA_TRIGGER_COMMAND` | 비어 있음 | 촬영 요청 전에 실행할 선택 명령 |
| `CAMERA_TRIGGER_TIMEOUT_SECONDS` | `5` | 트리거 명령 제한 시간 |
| `VITE_API_BASE_URL` | `http://localhost:8000` | 프론트엔드가 호출할 백엔드 주소 |
| `GOOGLE_DRIVE_ENABLED` | `false` | 최종 이미지 Google Drive 업로드 사용 여부 |
| `GOOGLE_DRIVE_FOLDER_ID` | 비어 있음 | 업로드할 Google Drive 폴더 ID |
| `GOOGLE_DRIVE_CREDENTIALS_FILE` | `secrets/google/credentials.json` | OAuth 클라이언트 자격 증명 파일 |
| `GOOGLE_DRIVE_TOKEN_FILE` | `secrets/google/token.json` | 로컬 OAuth 토큰 저장 파일 |
| `GOOGLE_DRIVE_SHARE_PUBLIC` | `true` | 업로드 파일을 링크가 있는 모든 사용자가 읽게 할지 여부 |
| `GOOGLE_DRIVE_SCOPES` | `https://www.googleapis.com/auth/drive` | OAuth 승인 범위. 쉼표로 여러 scope를 지정할 수 있음 |

---

## 프로젝트 구조

```text
reshot/
├── frontend/                 React + Vite UI
│   ├── .env.example          프론트엔드 API 주소 예시
│   └── src/
│       ├── api/              백엔드 API 클라이언트
│       ├── components/       프리뷰, 촬영, 선택, QR 컴포넌트
│       └── App.tsx           화면 라우팅과 플로우 제어
├── backend/                  FastAPI 서버
│   └── app/
│       ├── api/              HTTP 라우트
│       ├── camera/           dummy/watch_folder/Nikon 카메라 어댑터
│       ├── image/            템플릿, 레이아웃, 크롭 처리
│       ├── models/           세션 응답 모델
│       ├── scripts/          Google Drive OAuth 등 운영 스크립트
│       └── services/         세션, 촬영, 합성, QR, Google Drive 서비스
├── assets/
│   ├── frames/               4컷 템플릿 JSON, 로고
│   ├── fonts/                합성 텍스트용 폰트
│   └── old-photos/           기본 합성 fallback 자산
├── captures/                 세션별 촬영 원본
├── output/sessions/          세션별 final.jpg, qr.png, session.json
├── tools/                    현장 운영 보조 스크립트
├── README.md
└── ROADMAP.md
```

---

## API

| 메서드 | 경로 | 역할 |
| --- | --- | --- |
| `GET` | `/` | 기본 상태 확인 |
| `GET` | `/health` | 서버 상태, 카메라 모드, 저장 경로, Google Drive 설정 상태 확인 |
| `POST` | `/sessions` | 새 촬영 세션 생성 |
| `GET` | `/sessions/{session_id}` | 세션 메타데이터 조회 |
| `POST` | `/sessions/{session_id}/capture` | 지정 slot 사진 촬영 또는 dummy 생성 |
| `GET` | `/sessions/{session_id}/capture/{slot}` | 촬영 원본 이미지 조회 |
| `GET` | `/old-photos/{slot}` | 기본 과거 사진 조회 |
| `POST` | `/sessions/{session_id}/compose` | 선택한 4장으로 최종 이미지 합성, 선택적 Drive 업로드, QR 생성 |
| `GET` | `/sessions/{session_id}/image` | 최종 이미지 조회 |
| `POST` | `/sessions/{session_id}/qr` | QR 이미지 생성 또는 재생성 |
| `GET` | `/sessions/{session_id}/qr` | QR 이미지 조회 |

### API 예시

```powershell
$session = Invoke-RestMethod -Method Post http://127.0.0.1:8000/sessions -ContentType "application/json" -Body '{"template_id":"default"}'

1..8 | ForEach-Object {
  Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/capture" -ContentType "application/json" -Body "{`"slot`":$_}"
}

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/compose" -ContentType "application/json" -Body '{"template_id":"default","selected_capture_slots":[1,3,5,7]}'
```

`selected_capture_slots`는 반드시 4개여야 하고, 1부터 8까지의 중복 없는 slot 번호여야 합니다.

Google Drive 업로드가 켜져 있으면 compose 응답의 `drive_share_url`과 `qr_target_url`에 Drive 링크가 들어갑니다. 꺼져 있으면 `qr_target_url`은 `PUBLIC_BASE_URL` 기반의 로컬 이미지 URL입니다.

---

## 이미지 합성 규칙

기본 템플릿은 `assets/frames/default.json`에 정의되어 있습니다.

- 캔버스: `1200 x 1854`
- 사진 슬롯: `518 x 744` 4개
- 배경: `#000000`
- 로고: `assets/frames/mpnu-logo.png`
- 텍스트: `매직PNU 홈커밍 26.07.04`
- 저장 형식: JPEG quality 92

선택 합성에서는 사용자가 고른 4장의 촬영 이미지를 템플릿 슬롯 순서대로 배치합니다. 각 원본은 슬롯 크기에 맞게 중앙 크롭됩니다.

---

## 현재 범위

구현됨:

- React/Vite 기반 시작, 촬영, 선택, 결과 화면
- 브라우저 카메라 또는 HDMI 캡처 장치 라이브 프리뷰
- FastAPI 기반 세션/촬영/합성/QR API
- `dummy` 카메라 모드
- `watch_folder` 카메라 모드와 선택 트리거 명령
- 8장 촬영 플로우
- 8장 중 4장 선택 UI
- 선택한 4장으로 최종 이미지 합성
- Google Drive 선택 업로드와 Drive 공유 링크 기반 QR 생성
- 결과 화면의 세로형 이미지 프레임과 하단 QR/처음 버튼
- QR 모달 표시
- 로컬 네트워크 QR 설정 절차

아직 남은 일:

- 실제 행사 환경에서 반복 리허설
- `watch_folder`와 NX Tether 조합의 장시간 안정성 검증
- Nikon 직접 제어 어댑터 구현 여부 결정
- 촬영 실패 후 재시도와 복구 UI
- iPhone/Android QR 열기와 이미지 저장 검증
- Google Drive OAuth/폴더 권한과 현장 네트워크 조건 검증
- 세션 정리, 보존 정책, 운영자 화면

---

## 의존성

| 영역 | 주요 도구 |
| --- | --- |
| 프론트엔드 | React, Vite, TypeScript |
| 백엔드 | FastAPI, Uvicorn, Pydantic Settings |
| 이미지 처리 | Pillow |
| QR 생성 | qrcode[pil] |
| Google Drive | google-api-python-client, google-auth, google-auth-oauthlib |
| 로컬 운영 | Windows PowerShell, 같은 Wi-Fi 또는 핫스팟 |

---

## 라이선스

현재 저장소에는 라이선스 파일이 없습니다. 공개 또는 배포 전 `LICENSE` 파일을 추가하고 사용 범위를 결정해야 합니다.
