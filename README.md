<div align="center">

# Reshot

**현장 포토부스용 4컷 사진 촬영 앱**

8장의 현재 사진을 촬영한 뒤 마음에 드는 4장을 골라 4컷 결과 이미지를 만들고, QR 코드로 휴대폰에서 받을 수 있게 하는 로컬 서버 기반 앱입니다.

<br>

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vite.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## 기능

- **8장 연속 촬영**: 촬영 화면에서 7초 카운트다운 후 1번부터 8번까지 순서대로 촬영합니다.
- **4장 선택 합성**: 촬영 완료 후 4컷 프레임의 각 영역을 누르고, 8장 중 원하는 사진을 골라 배치합니다.
- **세로형 최종 이미지**: 기본 템플릿은 `1200 x 1854` 캔버스와 `518 x 744` 사진 슬롯 4개를 사용합니다.
- **결과 화면 최적화**: 최종 사진은 원본 비율에 맞는 검은 프레임 안에 표시되고, 아래에는 `QR 보기`와 `처음으로` 버튼만 배치됩니다.
- **QR 공유**: 결과 이미지 URL을 담은 QR 이미지를 생성하고 모달로 표시합니다.
- **세션 기반 저장**: 촬영 원본, 최종 이미지, QR, 메타데이터를 세션별 폴더에 저장합니다.
- **카메라 모드 분리**: 현재는 `dummy` 모드 중심이며, `watch_folder`와 Nikon 직접 제어를 붙일 수 있는 구조를 둡니다.

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

기본 개발 모드는 `CAMERA_MODE=dummy`입니다. 실제 Nikon 연결 없이도 촬영, 선택, 합성, QR 흐름을 확인할 수 있습니다.

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
  -> 8장 연속 촬영
  -> 촬영된 8장 중 4장 선택
  -> final.jpg + qr.png 생성
  -> /result/{session_id} 이동
  -> 최종 이미지 확인
  -> QR 보기 또는 처음으로 이동
```

촬영 중에는 마지막 촬영 이미지가 큰 미리보기 영역에 표시됩니다. 촬영 완료 후에는 최종 4컷 프레임이 보이고, 각 칸을 눌러 8장 중 원하는 사진을 배치합니다.

---

## 결과 화면 레이아웃

결과 화면은 화면 전체를 다음처럼 나눕니다.

```text
result-panel 전체 높이
  - 아래 버튼 바 높이
  - 이미지/버튼 간격
  = final-image-wrap 높이
```

`final-image-wrap`은 최종 이미지와 같은 `1200 / 1854` 비율을 갖는 검은 프레임입니다. 사진은 이 프레임 안에 `object-fit: contain`으로 표시됩니다. 아래 버튼 바는 고정 높이로 예약되어 사진 영역과 겹치지 않습니다.

하단 버튼 텍스트는 한국어 폰트 fallback과 줄바꿈 방지 스타일을 적용해 `QR 보기`, `처음으로`, `닫기`가 깨지거나 이상하게 줄바꿈되지 않게 했습니다.

---

## 로컬 네트워크 QR 테스트

휴대폰에서 QR을 열려면 `localhost`가 아니라 서버 PC의 Wi-Fi IP를 써야 합니다.

1. 노트북과 휴대폰을 같은 Wi-Fi 또는 핫스팟에 연결합니다.
2. 노트북에서 `ipconfig`를 실행해 Wi-Fi IPv4 주소를 확인합니다.
3. `.env`를 수정합니다.

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

---

## 설정

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `APP_NAME` | `reshot` | FastAPI 앱 이름 |
| `ENVIRONMENT` | `development` | 실행 환경 이름 |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | QR에 들어갈 공개 백엔드 URL |
| `FRONTEND_ORIGINS` | `http://localhost:5173` | CORS 허용 프론트엔드 주소 |
| `CAPTURES_DIR` | `captures` | 촬영 원본 저장 경로 |
| `OUTPUT_DIR` | `output/sessions` | 최종 이미지, QR, 세션 메타데이터 저장 경로 |
| `ASSETS_DIR` | `assets` | 프레임 템플릿과 고정 자산 경로 |
| `CAMERA_MODE` | `dummy` | 카메라 처리 모드 |
| `VITE_API_BASE_URL` | `http://localhost:8000` | 프론트엔드가 호출할 백엔드 주소 |

---

## 프로젝트 구조

```text
reshot/
├── frontend/                 React + Vite UI
│   └── src/
│       ├── api/              백엔드 API 클라이언트
│       ├── components/       촬영, 선택, QR 화면 컴포넌트
│       └── App.tsx           화면 라우팅과 플로우 제어
├── backend/                  FastAPI 서버
│   └── app/
│       ├── api/              HTTP 라우트
│       ├── camera/           dummy/watch_folder/Nikon 카메라 모드
│       ├── image/            템플릿, 레이아웃, 크롭 처리
│       ├── models/           세션 응답 모델
│       └── services/         세션, 촬영, 합성, QR 서비스
├── assets/
│   ├── frames/               4컷 템플릿 JSON
│   └── old-photos/           기본 합성 fallback 자산
├── captures/                 세션별 촬영 원본
├── output/sessions/          세션별 final.jpg, qr.png, session.json
├── README.md
└── ROADMAP.md
```

---

## API

| 메서드 | 경로 | 역할 |
| --- | --- | --- |
| `GET` | `/` | 기본 상태 확인 |
| `GET` | `/health` | 서버 상태, 카메라 모드, 경로 확인 |
| `POST` | `/sessions` | 새 촬영 세션 생성 |
| `GET` | `/sessions/{session_id}` | 세션 메타데이터 조회 |
| `POST` | `/sessions/{session_id}/capture` | 지정 slot의 사진 촬영 또는 dummy 생성 |
| `GET` | `/sessions/{session_id}/capture/{slot}` | 촬영 원본 이미지 조회 |
| `GET` | `/old-photos/{slot}` | 기본 과거 사진 조회 |
| `POST` | `/sessions/{session_id}/compose` | 선택한 4장으로 최종 이미지 합성 및 QR 생성 |
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

`selected_capture_slots`는 반드시 4개이고, 1부터 8까지의 중복 없는 slot 번호여야 합니다.

---

## 이미지 합성 규칙

기본 템플릿은 `assets/frames/default.json`에 정의되어 있습니다.

- 캔버스: `1200 x 1854`
- 사진 슬롯: `518 x 744` 4개
- 배경: `#000000`
- 로고: `assets/frames/mpnu-logo.png`
- 저장 형식: JPEG quality 92

현재 UI에서는 사용자가 고른 4장의 촬영 이미지를 템플릿의 4개 슬롯에 순서대로 배치합니다. `selected_capture_slots`를 보내지 않는 경우에는 기존 fallback 경로인 고정 과거 사진 2장과 현재 사진 2장을 사용합니다.

---

## 현재 범위

구현됨:

- React/Vite 기반 시작, 촬영, 선택, 결과 화면
- FastAPI 기반 세션/촬영/합성/QR API
- 8장 촬영 플로우
- 8장 중 4장 선택 UI
- 선택한 4장으로 최종 이미지 합성
- 결과 화면의 세로형 이미지 프레임과 하단 QR/처음 버튼
- QR 모달 표시
- 한국어 버튼 텍스트 깨짐 방지
- 로컬 네트워크 QR 설정 절차

아직 남은 일:

- 실제 Nikon 직접 제어 안정화
- watch folder 운영 검증
- 브라우저 실시간 카메라 프리뷰 연결
- 관리자 화면
- 세션 정리/보존 정책
- 행사 운영용 오류 복구 UI
- 모바일 기기별 QR 다운로드 검증

---

## 의존성

| 영역 | 주요 도구 |
| --- | --- |
| 프론트엔드 | React, Vite, TypeScript |
| 백엔드 | FastAPI, Uvicorn, Pydantic Settings |
| 이미지 처리 | Pillow |
| QR 생성 | qrcode[pil] |
| 로컬 운영 | Windows PowerShell, 같은 Wi-Fi 또는 핫스팟 |

---

## 라이선스

현재 저장소에는 라이선스 파일이 없습니다. 공개 또는 배포 전에 `LICENSE` 파일을 추가하고 사용 범위를 결정해야 합니다.