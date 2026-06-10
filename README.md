<div align="center">

# Reshot

**추억 네컷 촬영 앱** — 과거 사진 2장과 현재 촬영 사진 2장을 합성해 QR로 공유할 수 있는 4컷 사진을 생성합니다.

<br>

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vite.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

<br>

[기능](#기능) · [빠른-시작](#빠른-시작) · [사용법](#사용법) · [설정](#설정) · [아키텍처](#아키텍처) · [api](#api) · [현재-범위](#현재-범위)

</div>

---

## 기능

- **4컷 합성** — 고정 과거 사진 2장과 현재 사진 2장을 하나의 프레임 이미지로 합성합니다.
- **세션 기반 저장** — 촬영마다 고유 세션을 만들고 원본, 결과 이미지, QR 이미지를 분리해 저장합니다.
- **QR 공유** — 완성된 결과 이미지 URL을 QR 코드로 만들어 휴대폰에서 열 수 있게 합니다.
- **더미 촬영 플로우** — Nikon 카메라 없이도 샘플 이미지로 촬영 UI와 합성 플로우를 테스트합니다.
- **로컬 네트워크 운영** — 노트북을 서버로 사용하고 같은 Wi-Fi 또는 핫스팟에서 결과물을 공유합니다.
- **확장 가능한 카메라 구조** — 현재는 `dummy` 모드 중심이며, 이후 폴더 감시와 Nikon 연동을 붙일 수 있는 구조를 둡니다.

---

## 빠른 시작

### 1. 환경 설정

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

PowerShell에서 가상환경 활성화가 막히면 현재 터미널에만 실행 정책을 완화합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. 설정 파일

```powershell
cd C:\Users\kyle0\Develops\reshot
Copy-Item .env.example .env
Copy-Item frontend\.env.example frontend\.env
```

기본 개발 모드는 `CAMERA_MODE=dummy`입니다. Nikon 카메라가 없어도 촬영 흐름을 테스트할 수 있습니다.

### 3. 실행

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

## 사용법

### 웹 화면

| 경로 | 역할 |
| --- | --- |
| `http://localhost:5173/` | 시작 화면 |
| `http://localhost:5173/shoot` | 촬영 화면 |
| `http://localhost:5173/result/{session_id}` | 결과 이미지와 QR 표시 |

기본 플로우:

```text
Start
  │  새 세션 생성
  ▼
촬영 화면
  │  현재 사진 1 촬영
  ▼
촬영 화면
  │  현재 사진 2 촬영
  ▼
합성
  │  final.jpg + qr.png 생성
  ▼
결과 화면
```

> 현재 촬영은 실제 Nikon이 아니라 `assets/dummy-captures/` 또는 더미 생성 로직을 사용하는 개발용 흐름입니다.

### 백엔드 확인

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

정상 응답에는 `app`, `status`, `environment`, `camera_mode`, `paths`가 포함됩니다.

### 데모 합성

카메라 없이 `demo` 세션의 4컷 결과물을 생성합니다.

```powershell
cd C:\Users\kyle0\Develops\reshot\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.compose_demo --create-samples
```

생성 결과:

```text
output/sessions/demo/final.jpg
output/sessions/demo/session.json
```

### 핫스팟 또는 LAN에서 QR 테스트

참가자 휴대폰에서 QR을 열려면 `localhost`가 아니라 노트북의 Wi-Fi IP를 써야 합니다.

1. 휴대폰 핫스팟을 켭니다.
2. 노트북과 참가자 휴대폰을 같은 핫스팟에 연결합니다.
3. 노트북에서 `ipconfig`를 실행해 Wi-Fi IPv4 주소를 확인합니다.
4. `.env`를 수정합니다.

```text
PUBLIC_BASE_URL=http://{노트북_IP}:8000
FRONTEND_ORIGINS=http://localhost:5173,http://{노트북_IP}:5173
```

5. `frontend/.env`를 수정합니다.

```text
VITE_API_BASE_URL=http://{노트북_IP}:8000
```

6. 백엔드를 모든 인터페이스에서 실행합니다.

```powershell
cd C:\Users\kyle0\Develops\reshot\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. 참가자 휴대폰에서 `http://{노트북_IP}:8000/health`가 열리는지 확인합니다.

---

## 설정

모든 로컬 실행 설정은 `.env`와 `frontend/.env`로 제어합니다. 코드 수정 없이 서버 주소, 저장 경로, 카메라 모드를 바꿀 수 있습니다.

| 키 | 기본값 | 설명 |
| --- | --- | --- |
| `APP_NAME` | `reshot` | FastAPI 앱 이름 |
| `ENVIRONMENT` | `development` | 실행 환경 이름 |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | QR에 들어갈 공개 백엔드 URL |
| `FRONTEND_ORIGINS` | `http://localhost:5173` | CORS 허용 프론트엔드 주소 |
| `CAPTURES_DIR` | `captures` | 현재 촬영 원본 저장 경로 |
| `OUTPUT_DIR` | `output/sessions` | 합성 결과와 QR 저장 경로 |
| `ASSETS_DIR` | `assets` | 과거 사진, 프레임, 샘플 이미지 경로 |
| `CAMERA_MODE` | `dummy` | 카메라 처리 모드 |
| `VITE_API_BASE_URL` | `http://localhost:8000` | 프론트엔드가 호출할 백엔드 주소 |

---

## 아키텍처

### 폴더 구조

```text
reshot/
├── frontend/                 React + Vite 촬영 UI
│   └── src/
│       ├── api/              백엔드 API 클라이언트
│       ├── components/       촬영 미리보기와 QR 패널
│       └── App.tsx           화면 흐름 제어
├── backend/                  FastAPI 서버
│   └── app/
│       ├── api/              HTTP 라우트
│       ├── camera/           카메라 모드별 구현
│       ├── image/            크롭, 레이아웃, 템플릿 처리
│       ├── models/           세션 응답 모델
│       ├── scripts/          로컬 데모 실행 스크립트
│       └── services/         세션, 촬영, 합성, QR 서비스
├── assets/                   고정 사진, 프레임, 샘플 이미지
│   ├── frames/               4컷 템플릿 JSON
│   └── old-photos/           고정 과거 사진 2장
├── captures/                 세션별 현재 촬영 원본
├── output/sessions/          세션별 결과 이미지와 QR
├── docs/                     운영 및 카메라 문서
└── ROADMAP.md                개발 로드맵
```

### 데이터 흐름

```text
React 촬영 UI
   │  세션 생성/촬영/합성 API 요청
   ▼
FastAPI 라우트
   │  세션 상태 변경
   ▼
Session Service ──▶ captures/{session_id}/current_*.jpg
   │                 촬영 원본 경로
   ▼
Compose Service ──▶ output/sessions/{session_id}/final.jpg
   │                 합성 결과 이미지
   ▼
QR Service ───────▶ output/sessions/{session_id}/qr.png
   │                 결과 이미지 URL
   ▼
React 결과 화면 ──▶ 사용자 휴대폰 QR 스캔
```

> 실시간 프리뷰와 고화질 촬영 파일은 분리해서 설계합니다. 프리뷰는 HDMI 캡처카드가 있을 때 브라우저 영상 장치로 받고, 합성에는 카메라가 저장한 JPEG 파일을 사용합니다.

---

## API

| 메서드 | 경로 | 역할 |
| --- | --- | --- |
| `GET` | `/` | 기본 상태 확인 |
| `GET` | `/health` | 서버 상태, 카메라 모드, 저장 경로 확인 |
| `POST` | `/sessions` | 새 촬영 세션 생성 |
| `GET` | `/sessions/{session_id}` | 세션 메타데이터 조회 |
| `POST` | `/sessions/{session_id}/capture` | 현재 사진 1장 촬영 또는 더미 생성 |
| `GET` | `/sessions/{session_id}/capture/{slot}` | 촬영 원본 이미지 조회 |
| `GET` | `/old-photos/{slot}` | 고정 과거 사진 조회 |
| `POST` | `/sessions/{session_id}/compose` | 4컷 합성 및 QR 생성 |
| `GET` | `/sessions/{session_id}/image` | 최종 합성 이미지 조회 |
| `POST` | `/sessions/{session_id}/qr` | QR 이미지 생성 또는 재생성 |
| `GET` | `/sessions/{session_id}/qr` | QR 이미지 조회 |

촬영 API 예시:

```powershell
$session = Invoke-RestMethod -Method Post http://127.0.0.1:8000/sessions -ContentType "application/json" -Body '{"template_id":"default"}'
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/capture" -ContentType "application/json" -Body '{"slot":1}'
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/capture" -ContentType "application/json" -Body '{"slot":2}'
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sessions/$($session.session_id)/compose" -ContentType "application/json" -Body '{"template_id":"default"}'
```

---

## 카메라와 프리뷰

현재 구현된 촬영 모드는 `dummy`입니다. 실제 Nikon 연동은 아직 운영 기능으로 연결되지 않았습니다.

실시간 프리뷰를 웹앱에 넣으려면 보통 아래 구성이 필요합니다.

```text
Nikon 카메라
   │  HDMI 출력
   ▼
USB HDMI 캡처카드
   │  웹캠 장치로 인식
   ▼
노트북 브라우저
```

HDMI 케이블만 노트북에 바로 연결하는 방식은 대부분 동작하지 않습니다. 노트북 HDMI 포트는 보통 출력용이므로 카메라 화면을 받으려면 USB HDMI 캡처카드가 필요합니다.

---

## 현재 범위

구현됨:

- React/Vite 기반 촬영 UI
- FastAPI 기반 백엔드
- 헬스체크 API
- 세션 생성과 메타데이터 저장
- 더미 촬영 플로우
- 과거 사진 2장과 현재 사진 2장의 4컷 합성
- 결과 이미지 저장
- QR 이미지 생성
- 로컬 네트워크 QR 검증 절차

아직 구현되지 않음:

- Nikon 직접 제어
- 폴더 감시 기반 실제 촬영 파일 수집
- 브라우저 실시간 프리뷰 컴포넌트
- 갤러리 전용 UI
- 다운로드 전용 API
- 관리자 화면

---

## 의존성

| 영역 | 주요 도구 |
| --- | --- |
| 프론트엔드 | React, Vite, TypeScript |
| 백엔드 | FastAPI, Uvicorn, Pydantic |
| 이미지 처리 | Pillow |
| QR 생성 | qrcode |
| 로컬 운영 | Windows PowerShell, 같은 Wi-Fi 또는 핫스팟 |

---

## 라이선스

현재 저장소에는 라이선스 파일이 없습니다. 외부 공개 또는 배포 전에 `LICENSE` 파일을 추가하고 사용 범위를 결정해야 합니다.
