# Reshot ROADMAP

## 1. 프로젝트 목표

### 프로젝트 개요

Reshot은 사용자가 현장에서 현재 사진 2장을 촬영하고, 미리 준비해둔 과거 사진 2장과 합쳐 총 4컷 인생네컷 이미지를 생성하는 로컬 서버 기반 포토부스 앱이다. 외부 Nikon 카메라를 컴퓨터에 연결하고, 컴퓨터에서 촬영 제어, 이미지 합성, 결과 저장, QR 다운로드 링크 제공까지 처리한다.

### 해결하려는 문제

- 과거 사진과 현재 사진을 한 장의 4컷 프레임으로 자연스럽게 조합한다.
- 행사 현장에서 사용자가 별도 앱 설치 없이 QR 코드로 결과물을 받을 수 있게 한다.
- 운영자가 복잡한 편집 도구 없이 고정 사진, 프레임, 촬영 플로우를 관리할 수 있게 한다.
- 카메라 연동이 불안정해도 파일 업로드 또는 폴더 감시 방식으로 운영을 지속할 수 있게 한다.

### 최종 사용자 경험

1. 사용자가 촬영 화면 앞에 선다.
2. 운영자 또는 사용자가 `촬영 시작`을 누른다.
3. 앱이 2장의 현재 사진을 순차적으로 촬영한다.
4. 앱이 미리 설정된 과거 사진 2장과 현재 사진 2장을 자동 합성한다.
5. 완성된 4컷 이미지가 화면에 표시된다.
6. 사용자는 QR 코드를 휴대폰으로 스캔한다.
7. 휴대폰 브라우저에서 결과 이미지를 확인하고 저장한다.

### MVP 필수 기능

- 세션 생성
- 과거 사진 2장 설정
- 더미 이미지 또는 업로드 이미지 기반 4컷 합성
- 결과 이미지 저장
- 결과 이미지 조회 페이지
- QR 코드 생성
- 촬영 UI
- Nikon 연동 전 fallback 촬영 플로우

### MVP 이후 확장 기능

- Nikon 직접 촬영 제어
- 여러 프레임 템플릿 선택
- 과거 사진 세트 여러 개 관리
- 촬영 전 카운트다운 애니메이션
- 다시 찍기 기능
- 관리자 화면
- 출력용 고해상도 이미지 생성
- 프린터 연동
- Cloudflare Tunnel 또는 ngrok 기반 외부 공유
- 결과물 자동 만료 및 관리자 다운로드

## 2. 전체 시스템 흐름

### 기본 촬영 흐름

1. `POST /api/session`으로 새 촬영 세션을 만든다.
2. 서버는 `session_id`를 생성하고 `output/sessions/{session_id}/` 폴더를 만든다.
3. 프론트엔드는 촬영 화면을 열고 카운트다운을 보여준다.
4. `POST /api/session/{id}/capture`를 호출해 첫 번째 현재 사진을 촬영한다.
5. 카메라 연동 모듈은 Nikon 촬영 명령, 폴더 감시, 또는 더미 이미지 복사를 수행한다.
6. 첫 번째 촬영 결과를 `captures/{session_id}/current_1.jpg`로 저장한다.
7. 같은 방식으로 두 번째 현재 사진을 `captures/{session_id}/current_2.jpg`로 저장한다.
8. `POST /api/session/{id}/compose`를 호출한다.
9. 이미지 처리 모듈은 과거 사진 2장과 현재 사진 2장을 불러온다.
10. 지정된 템플릿 규칙에 따라 4컷 이미지를 합성한다.
11. 결과 이미지를 `output/sessions/{session_id}/final.jpg`로 저장한다.
12. 서버는 `/gallery/{session_id}`와 `/download/{session_id}` 링크를 생성한다.
13. QR 생성 모듈은 갤러리 링크를 QR 코드 이미지 또는 SVG로 만든다.
14. 프론트엔드는 최종 이미지와 QR 코드를 화면에 표시한다.
15. 사용자는 QR 코드를 스캔해 휴대폰에서 결과 이미지를 다운로드한다.

### 데이터 흐름

```text
Frontend UI
  -> Backend API
  -> Session Service
  -> Camera Service
  -> Capture Storage
  -> Compose Service
  -> Output Storage
  -> Gallery/Download API
  -> QR Code
  -> User Mobile Browser
```

## 3. 기술 아키텍처

### 프론트엔드 역할

- 촬영 시작, 카운트다운, 촬영 진행 상태 표시
- 카메라 실시간 프리뷰 표시
- 촬영된 사진 미리보기
- 결과 이미지 표시
- QR 코드 표시
- 다시 촬영, 새 세션 시작 UI 제공

추천 파일:

- `frontend/src/App.tsx`
- `frontend/src/pages/CapturePage.tsx`
- `frontend/src/pages/GalleryPage.tsx`
- `frontend/src/components/Countdown.tsx`
- `frontend/src/components/CameraPreview.tsx`
- `frontend/src/components/PhotoStripPreview.tsx`
- `frontend/src/components/QrPanel.tsx`
- `frontend/src/api/client.ts`

### 백엔드 역할

- 세션 생성 및 상태 관리
- 촬영 요청 처리
- 이미지 합성 요청 처리
- 정적 파일 제공
- QR 코드 생성
- 카메라 연동 모듈 호출
- 운영 설정 로딩

추천 파일:

- `backend/app/main.py`
- `backend/app/api/routes.py`
- `backend/app/core/config.py`
- `backend/app/services/session_service.py`
- `backend/app/services/camera_service.py`
- `backend/app/services/compose_service.py`
- `backend/app/services/qr_service.py`
- `backend/app/models/session.py`

### 이미지 처리 모듈 역할

- 이미지 로딩
- EXIF 회전 보정
- 지정 비율 중앙 크롭
- 프레임 슬롯에 맞게 리사이즈
- 배경, 여백, 라벨, 날짜 텍스트 적용
- 최종 이미지 저장

추천 파일:

- `backend/app/services/compose_service.py`
- `backend/app/image/crop.py`
- `backend/app/image/layout.py`
- `backend/app/image/templates.py`

### 카메라 연동 모듈 역할

- 개발 초기에는 더미 이미지 반환
- 다음 단계에서는 특정 폴더에 새로 생긴 이미지 감시
- 최종 단계에서는 Nikon 카메라 직접 제어 시도
- 촬영 실패 시 사용자에게 재시도 또는 수동 업로드 fallback 제공

추천 파일:

- `backend/app/services/camera_service.py`
- `backend/app/camera/base.py`
- `backend/app/camera/dummy.py`
- `backend/app/camera/watch_folder.py`
- `backend/app/camera/nikon.py`

### 실시간 프리뷰 아키텍처

실시간 프리뷰는 최종 고화질 사진 저장과 분리해서 설계한다. Nikon 카메라의 라이브 화면을 사용자가 노트북 또는 연결된 모니터에서 확인하고, 실제 합성에는 카메라가 저장한 고화질 JPEG 파일을 사용한다.

권장 구조:

```text
실시간 프리뷰:
Nikon HDMI 출력
  -> USB HDMI 캡처카드
  -> 노트북 웹캠 장치로 인식
  -> 브라우저 getUserMedia()
  -> frontend/src/components/CameraPreview.tsx

고화질 촬영 파일:
Nikon 촬영
  -> Nikon 소프트웨어/digiCamControl/저장 폴더
  -> backend watch_folder
  -> captures/{session_id}/current_{slot}.jpg
  -> compose_service
```

이 구조의 핵심은 프리뷰와 촬영 결과 파일을 같은 경로로 처리하지 않는 것이다. 프리뷰는 사용자가 구도와 포즈를 확인하기 위한 저지연 영상이고, 합성에는 카메라가 실제로 저장한 원본에 가까운 사진 파일을 사용한다.

MVP 기준:

- 노트북 또는 노트북에 연결된 모니터에서 프리뷰를 보여준다.
- 브라우저의 `navigator.mediaDevices.getUserMedia()`로 캡처카드 영상을 표시한다.
- 프리뷰 장치가 없으면 검은 화면 대신 `카메라 프리뷰를 사용할 수 없음` 상태를 표시한다.
- 태블릿에서 원격으로 프리뷰를 보는 기능은 MVP 필수에서 제외한다.

태블릿 원격 프리뷰가 필요한 경우:

- 백엔드 또는 별도 미디어 서버가 캡처카드 영상을 MJPEG, HLS, WebRTC 중 하나로 스트리밍해야 한다.
- 같은 Wi-Fi 환경에서 지연 시간과 접속 안정성을 별도로 테스트해야 한다.
- 행사장 MVP에서는 노트북 화면 또는 외부 모니터 사용을 우선한다.

### 파일 저장 구조

```text
captures/{session_id}/current_1.jpg
captures/{session_id}/current_2.jpg
output/sessions/{session_id}/final.jpg
output/sessions/{session_id}/qr.png
output/sessions/{session_id}/session.json
assets/old-photos/old_1.jpg
assets/old-photos/old_2.jpg
assets/frames/default.json
```

### QR/공유 링크 구조

- QR에는 이미지 파일 직접 링크보다 갤러리 페이지 링크를 넣는다.
- 권장 QR URL: `http://{server_ip}:8000/gallery/{session_id}`
- 다운로드 URL: `http://{server_ip}:8000/download/{session_id}`
- 같은 Wi-Fi에서만 쓸 경우 로컬 IP를 사용한다.
- 외부 네트워크에서도 접근해야 하면 Cloudflare Tunnel 또는 ngrok을 사용한다.

### 로컬 네트워크 또는 외부 접속 방식

- MVP: 같은 Wi-Fi 내 로컬 IP 접근
- 행사장 권장: 공유기 고정, 서버 PC 고정 IP 설정
- 외부 접속 필요 시: Cloudflare Tunnel 우선 검토
- 인터넷 불안정 환경: QR 대신 로컬 Wi-Fi 안내 또는 운영자 전송 fallback 준비

## 4. 추천 기술 스택

### 프론트엔드

| 후보 | 장점 | 단점 | 추천도 |
| --- | --- | --- | --- |
| React + Vite | 빠른 개발, 단순한 SPA에 적합 | SSR 없음 | 높음 |
| Next.js | 라우팅/배포 구조 강함 | 로컬 장비 제어 앱에는 다소 무거움 | 중간 |
| 순수 HTML/JS | 가장 단순 | 상태 관리와 UI 확장성 낮음 | 낮음 |

MVP 추천: `React + Vite`

### 백엔드

| 후보 | 장점 | 단점 | 추천도 |
| --- | --- | --- | --- |
| FastAPI | 이미지 처리/Pillow와 궁합 좋음, API 작성 빠름 | Python 환경 관리 필요 | 높음 |
| Node.js/Express | 프론트엔드와 언어 통일 | 이미지 처리와 카메라 제어는 Python보다 번거로울 수 있음 | 중간 |
| Electron 단독 앱 | 데스크톱 앱처럼 배포 가능 | 초기 복잡도 높음 | 낮음 |

MVP 추천: `FastAPI`

### 이미지 합성

| 후보 | 장점 | 단점 | 추천도 |
| --- | --- | --- | --- |
| Python Pillow | 크롭/합성/텍스트 처리 쉬움 | 고성능 대량 처리에는 제한 | 높음 |
| Node sharp | 빠르고 품질 좋음 | Python 기반 카메라 도구와 분리됨 | 중간 |

MVP 추천: `Pillow`

### QR 생성

- Python: `qrcode[pil]`
- Node: `qrcode`
- QR 내용은 `/gallery/{session_id}` URL
- QR 이미지는 저장하지 않고 API에서 동적 생성해도 된다.
- 운영 안정성을 위해 MVP에서는 `output/sessions/{session_id}/qr.png`로 저장한다.

### Nikon 카메라 연동 후보

| 방식 | 장점 | 단점 | 현실성 |
| --- | --- | --- | --- |
| 더미 이미지 | 개발 즉시 가능 | 실제 촬영 아님 | 개발 초기 필수 |
| 폴더 감시 | Windows에서 현실적, 카메라 앱과 병행 가능 | 촬영 트리거는 별도 필요할 수 있음 | 높음 |
| digiCamControl | Windows Nikon 테더링에 유용 | 외부 프로그램 의존 | 높음 |
| Nikon SDK | 정교한 제어 가능 | SDK 접근/문서/모델 호환성 부담 | 중간 |
| gphoto2 | DSLR 제어 사례 많음 | Windows 네이티브 사용이 까다로움 | 낮음-중간 |

MVP 추천 순서:

1. 더미 이미지
2. 폴더 감시
3. digiCamControl CLI 또는 연동 자동화
4. Nikon SDK 직접 제어 검토

### 실시간 프리뷰 방식 후보

| 방식 | 장점 | 단점 | 추천도 |
| --- | --- | --- | --- |
| HDMI 캡처카드 | 브라우저에서 웹캠처럼 인식, 프리뷰 안정성 높음, 촬영 파일 처리와 분리 가능 | 캡처카드와 HDMI 케이블 필요, 카메라의 clean HDMI 지원 확인 필요 | 높음 |
| Nikon 테더링 소프트웨어 라이브뷰 | 카메라 제어와 라이브뷰를 같은 도구에서 처리 가능 | 웹앱 안에 직접 넣기 어렵고 모델별 지원 차이가 큼 | 중간 |
| Nikon Webcam Utility | 일부 Nikon을 USB 웹캠처럼 사용 가능 | 해상도/지연/호환성 제한 가능, 고화질 사진 저장과 별도 처리 필요 | 중간 |
| 백엔드 영상 스트리밍 | 태블릿에서도 원격 프리뷰 가능 | WebRTC/MJPEG/HLS 구현과 네트워크 안정화 필요 | 낮음-MVP 이후 |

MVP 추천:

1. HDMI 캡처카드로 노트북 브라우저 프리뷰 구현
2. 실제 사진 저장은 폴더 감시 방식으로 처리
3. 태블릿 원격 프리뷰는 현장 요구가 확정된 뒤 WebRTC 또는 MJPEG로 검토

## 5. MVP 개발 단계

### 1단계: 프로젝트 초기 세팅

- 목표: 프론트엔드와 백엔드가 로컬에서 실행되는 기본 골격 구축
- 구현할 기능:
  - `frontend/` React + Vite 생성
  - `backend/` FastAPI 생성
  - 정적 파일 경로 설정
  - 환경 변수 파일 작성
  - 기본 헬스체크 API 작성
- 필요한 파일/모듈:
  - `frontend/package.json`
  - `frontend/src/App.tsx`
  - `backend/requirements.txt`
  - `backend/app/main.py`
  - `backend/app/core/config.py`
  - `.env.example`
- 완료 기준:
  - `http://localhost:5173`에서 프론트엔드 실행
  - `http://localhost:8000/health`에서 백엔드 응답
- 예상 리스크:
  - Python/Node 버전 충돌
  - CORS 설정 누락

### 2단계: 4컷 이미지 합성 기능

- 목표: 카메라 없이 파일 4장을 합성해 최종 이미지를 생성
- 구현할 기능:
  - 과거 사진 2장 로딩
  - 현재 사진 2장 로딩
  - 중앙 크롭 및 리사이즈
  - 2x2 레이아웃 합성
  - 결과 이미지 저장
- 필요한 파일/모듈:
  - `backend/app/services/compose_service.py`
  - `backend/app/image/crop.py`
  - `backend/app/image/layout.py`
  - `assets/old-photos/old_1.jpg`
  - `assets/old-photos/old_2.jpg`
  - `assets/frames/default.json`
- 완료 기준:
  - CLI 또는 API 호출로 `output/sessions/demo/final.jpg` 생성
  - 사진 비율이 깨지지 않고 슬롯에 맞게 크롭됨
- 예상 리스크:
  - 원본 사진 EXIF 회전 문제
  - 얼굴이 잘리는 크롭 문제

### 3단계: 결과 이미지 저장 및 조회

- 목표: 세션별 결과물을 저장하고 브라우저에서 조회
- 구현할 기능:
  - 세션 폴더 생성
  - `session.json` 저장
  - `/gallery/{id}` 페이지 제공
  - `/download/{id}` 다운로드 제공
- 필요한 파일/모듈:
  - `backend/app/services/session_service.py`
  - `backend/app/api/routes.py`
  - `output/sessions/{session_id}/session.json`
- 완료 기준:
  - 합성 완료 후 갤러리 링크에서 최종 이미지 표시
  - 다운로드 링크가 이미지 파일을 반환
- 예상 리스크:
  - 경로 탐색 취약점
  - 잘못된 세션 ID 요청 처리

### 4단계: QR 코드 생성

- 목표: 사용자가 휴대폰으로 결과물을 받을 수 있는 QR 코드 제공
- 구현할 기능:
  - 서버 IP 기반 갤러리 URL 생성
  - QR 이미지 생성
  - QR API 제공
  - 결과 화면에 QR 표시
- 필요한 파일/모듈:
  - `backend/app/services/qr_service.py`
  - `backend/app/api/routes.py`
  - `frontend/src/components/QrPanel.tsx`
- 완료 기준:
  - 휴대폰으로 QR 스캔 시 `/gallery/{id}` 접근 가능
  - 같은 Wi-Fi 환경에서 이미지 다운로드 가능
- 예상 리스크:
  - 서버 IP 자동 감지 실패
  - 휴대폰과 서버 PC가 서로 다른 네트워크에 연결됨

### 5단계: 촬영 UI 제작

- 목표: 현장에서 운영 가능한 촬영 화면 구현
- 구현할 기능:
  - 카메라 실시간 프리뷰 표시
  - 새 세션 시작
  - 촬영 카운트다운
  - 1번/2번 촬영 진행 표시
  - 합성 진행 상태 표시
  - 결과 이미지 및 QR 표시
  - 다시 촬영 버튼
- 필요한 파일/모듈:
  - `frontend/src/pages/CapturePage.tsx`
  - `frontend/src/components/CameraPreview.tsx`
  - `frontend/src/components/Countdown.tsx`
  - `frontend/src/components/PhotoStripPreview.tsx`
  - `frontend/src/api/client.ts`
- 완료 기준:
  - 운영자가 한 화면에서 촬영 시작부터 QR 표시까지 진행 가능
  - HDMI 캡처카드 또는 웹캠 장치가 있을 때 프리뷰가 표시됨
  - 프리뷰 장치가 없을 때도 촬영 플로우가 막히지 않음
  - API 실패 시 재시도 버튼 표시
- 예상 리스크:
  - 브라우저 카메라 권한 차단
  - 캡처카드가 다른 프로그램에서 이미 사용 중인 상태
  - 촬영 상태와 서버 세션 상태 불일치
  - 여러 번 클릭으로 중복 요청 발생

### 6단계: Nikon 카메라 연동

- 목표: 실제 카메라 촬영 결과를 세션에 연결
- 구현할 기능:
  - 카메라 모드 추상화
  - HDMI 캡처카드 기반 프리뷰와 촬영 파일 저장 플로우 분리
  - `dummy` 모드
  - `watch_folder` 모드
  - Nikon 직접 제어 후보 실험
  - 촬영 실패 시 fallback 처리
- 필요한 파일/모듈:
  - `backend/app/camera/base.py`
  - `backend/app/camera/dummy.py`
  - `backend/app/camera/watch_folder.py`
  - `backend/app/camera/nikon.py`
  - `backend/app/services/camera_service.py`
- 완료 기준:
  - `CAMERA_MODE=dummy`에서 더미 이미지 사용
  - `CAMERA_MODE=watch_folder`에서 새 이미지 감지 후 세션으로 복사
  - 카메라 미연결 시 명확한 에러 반환
- 예상 리스크:
  - Nikon 모델별 테더링 지원 차이
  - Windows 권한/드라이버 문제
  - 촬영 파일 생성 완료 전 읽기 시도

### 7단계: 실제 촬영 플로우 연결

- 목표: 세션 생성, 2회 촬영, 합성, QR 표시를 하나의 플로우로 연결
- 구현할 기능:
  - `POST /api/session/{id}/capture` 2회 호출
  - 촬영 결과 세션 상태 업데이트
  - 합성 자동 실행 또는 명시적 실행
  - 결과 화면 전환
- 필요한 파일/모듈:
  - `backend/app/models/session.py`
  - `backend/app/services/session_service.py`
  - `frontend/src/pages/CapturePage.tsx`
- 완료 기준:
  - 사용자가 한 번의 흐름으로 최종 QR까지 도달
  - 중간 실패 시 현재 단계에서 재시도 가능
- 예상 리스크:
  - 촬영 중 사용자가 새 세션을 시작하는 문제
  - 이미지 파일 누락 시 합성 실패

### 8단계: 현장 테스트 및 안정화

- 목표: 행사장에서 반복 촬영 가능한 안정성 확보
- 구현할 기능:
  - 오래된 파일 정리
  - 운영 로그 저장
  - 네트워크 점검 화면
  - 카메라 연결 점검
  - 수동 이미지 교체 기능
- 필요한 파일/모듈:
  - `backend/app/services/cleanup_service.py`
  - `backend/app/services/health_service.py`
  - `frontend/src/pages/AdminPage.tsx`
- 완료 기준:
  - 연속 20회 이상 촬영 플로우 성공
  - 휴대폰 3종 이상에서 QR 다운로드 확인
  - 카메라 연결 해제 후 복구 시나리오 검증
- 예상 리스크:
  - 현장 Wi-Fi 불안정
  - 카메라 배터리/저장장치 문제
  - 장시간 실행 중 메모리/디스크 누적

## 6. 폴더 구조 제안

```text
reshot/
  README.md
  ROADMAP.md
  .env.example
  frontend/
    package.json
    src/
      App.tsx
      api/
        client.ts
      pages/
        CapturePage.tsx
        GalleryPage.tsx
        AdminPage.tsx
      components/
        Countdown.tsx
        PhotoStripPreview.tsx
        QrPanel.tsx
  backend/
    requirements.txt
    app/
      main.py
      api/
        routes.py
      core/
        config.py
      models/
        session.py
      services/
        session_service.py
        camera_service.py
        compose_service.py
        qr_service.py
        cleanup_service.py
      camera/
        base.py
        dummy.py
        watch_folder.py
        nikon.py
      image/
        crop.py
        layout.py
        templates.py
  assets/
    old-photos/
      old_1.jpg
      old_2.jpg
    frames/
      default.json
      default_overlay.png
    dummy-captures/
      sample_1.jpg
      sample_2.jpg
  captures/
    .gitkeep
  output/
    sessions/
      .gitkeep
  docs/
    camera-setup.md
    operations.md
```

### 폴더 목적

- `frontend/`: 촬영 UI, 결과 화면, 관리자 화면
- `backend/`: API 서버, 이미지 처리, 카메라 연동
- `assets/old-photos/`: 고정으로 사용할 과거 사진 2장
- `assets/frames/`: 프레임 템플릿 JSON, 오버레이 PNG
- `assets/dummy-captures/`: 카메라 없이 개발할 때 쓰는 샘플 사진
- `captures/`: 세션별 현재 촬영 원본 저장
- `output/sessions/`: 최종 합성 이미지, QR, 세션 메타데이터 저장
- `docs/`: 카메라 연결법, 운영 매뉴얼, 문제 해결 문서

## 7. API 설계 초안

### `GET /`

- 역할: 프론트엔드 앱 또는 기본 상태 페이지 반환
- 요청 데이터: 없음
- 응답 데이터:

```json
{
  "app": "reshot",
  "status": "ok"
}
```

- 실패 케이스:
  - 서버 시작 실패
  - 정적 파일 경로 누락

### `POST /api/session`

- 역할: 새 촬영 세션 생성
- 요청 데이터:

```json
{
  "template_id": "default",
  "old_photo_set": "default"
}
```

- 응답 데이터:

```json
{
  "id": "20260610-184501-a1b2c3",
  "status": "created",
  "capture_count": 0,
  "gallery_url": "/gallery/20260610-184501-a1b2c3"
}
```

- 실패 케이스:
  - 템플릿 파일 없음
  - 과거 사진 2장 없음
  - 세션 폴더 생성 실패

### `POST /api/session/{id}/capture`

- 역할: 현재 사진 1장을 촬영하거나 감지해 세션에 저장
- 요청 데이터:

```json
{
  "slot": 1
}
```

- 응답 데이터:

```json
{
  "id": "20260610-184501-a1b2c3",
  "status": "capturing",
  "slot": 1,
  "file": "/captures/20260610-184501-a1b2c3/current_1.jpg"
}
```

- 실패 케이스:
  - 세션 없음
  - `slot`이 1 또는 2가 아님
  - 카메라 미연결
  - 폴더 감시 타임아웃
  - 촬영 파일 저장 실패

### `POST /api/session/{id}/compose`

- 역할: 과거 사진 2장과 현재 사진 2장을 합성
- 요청 데이터:

```json
{
  "template_id": "default"
}
```

- 응답 데이터:

```json
{
  "id": "20260610-184501-a1b2c3",
  "status": "composed",
  "final_image_url": "/download/20260610-184501-a1b2c3",
  "gallery_url": "/gallery/20260610-184501-a1b2c3",
  "qr_url": "/api/session/20260610-184501-a1b2c3/qr"
}
```

- 실패 케이스:
  - 현재 사진 2장 미완료
  - 과거 사진 누락
  - 템플릿 JSON 오류
  - 이미지 파일 손상
  - 출력 경로 쓰기 실패

### `GET /api/session/{id}`

- 역할: 세션 상태 조회
- 요청 데이터: 없음
- 응답 데이터:

```json
{
  "id": "20260610-184501-a1b2c3",
  "status": "composed",
  "captures": [
    "/captures/20260610-184501-a1b2c3/current_1.jpg",
    "/captures/20260610-184501-a1b2c3/current_2.jpg"
  ],
  "final_image_url": "/download/20260610-184501-a1b2c3",
  "gallery_url": "/gallery/20260610-184501-a1b2c3"
}
```

- 실패 케이스:
  - 세션 없음
  - `session.json` 손상

### `GET /gallery/{id}`

- 역할: 사용자가 QR로 접속하는 결과 페이지 반환
- 요청 데이터: 없음
- 응답 데이터:
  - HTML 페이지
  - 최종 이미지
  - 다운로드 버튼
- 실패 케이스:
  - 세션 없음
  - 아직 합성 전
  - 결과 이미지 없음

### `GET /download/{id}`

- 역할: 최종 합성 이미지 다운로드
- 요청 데이터: 없음
- 응답 데이터:
  - `image/jpeg` 또는 `image/png`
  - 파일명 예시: `reshot-20260610-184501-a1b2c3.jpg`
- 실패 케이스:
  - 세션 없음
  - 결과 이미지 없음

### `GET /api/session/{id}/qr`

- 역할: 갤러리 URL이 담긴 QR 코드 반환
- 요청 데이터: 없음
- 응답 데이터:
  - `image/png`
- 실패 케이스:
  - 세션 없음
  - 서버 공개 URL 설정 누락
  - QR 생성 실패

## 8. 이미지 합성 규칙

### 기본 배치 방식

MVP에서는 2x2 그리드를 사용한다.

```text
+----------------+----------------+
| old_1          | current_1      |
+----------------+----------------+
| old_2          | current_2      |
+----------------+----------------+
```

### 사진 위치

- 1번 슬롯: 고정 과거 사진 1
- 2번 슬롯: 현재 촬영 사진 1
- 3번 슬롯: 고정 과거 사진 2
- 4번 슬롯: 현재 촬영 사진 2

추후 템플릿에서 위치를 바꿀 수 있도록 슬롯 정보를 JSON으로 관리한다.

### 출력 이미지 해상도

MVP 기본값:

- 최종 이미지: `1200 x 1854`
- 바깥 여백: `76px`
- 슬롯 간 간격: `30px`
- 각 사진 슬롯: `518 x 744`
- 배경색: `#000000`
- logo: `assets/frames/mpnu-logo.png`, top center
- 저장 형식: `JPEG quality 92`

### 크롭 방식

- 모든 입력 이미지는 슬롯 비율에 맞춰 중앙 크롭한다.
- EXIF orientation을 먼저 적용한다.
- 얼굴 인식 기반 크롭은 MVP 이후 기능으로 둔다.
- 원본 비율이 너무 다르면 중앙 크롭 전에 긴 변 기준 리사이즈를 수행한다.

### 프레임/여백/배경 처리

- MVP는 단색 배경과 일정 여백을 사용한다.
- 추후 `default_overlay.png`를 최상단에 합성해 브랜드 프레임을 적용한다.
- 날짜, 행사명, 로고는 템플릿 JSON의 옵션으로 둔다.

예시 템플릿:

```json
{
  "id": "default",
  "canvas": {
    "width": 1200,
    "height": 1854,
    "background": "#000000"
  },
  "logo": {
    "src": "assets/frames/mpnu-logo.png",
    "x": 420,
    "y": 48,
    "width": 360,
    "height": 170,
    "fit": "contain"
  },
  "slots": [
    { "key": "old_1", "x": 76, "y": 251, "width": 518, "height": 744 },
    { "key": "current_1", "x": 628, "y": 251, "width": 518, "height": 744 },
    { "key": "old_2", "x": 76, "y": 1017, "width": 518, "height": 744 },
    { "key": "current_2", "x": 628, "y": 1017, "width": 518, "height": 744 }
  ],
  "overlay": "assets/frames/default_overlay.png",
  "output": {
    "format": "jpg",
    "quality": 92
  }
}
```

## 9. 카메라 연동 전략

### 1단계: 더미 이미지 개발

- `CAMERA_MODE=dummy`
- `assets/dummy-captures/sample_1.jpg`, `sample_2.jpg`를 세션 폴더로 복사한다.
- 카메라 없이 API, 합성, UI를 먼저 완성한다.

### 2단계: 폴더 감시 방식

- `CAMERA_MODE=watch_folder`
- Nikon 또는 보조 프로그램이 특정 폴더에 사진을 저장한다.
- 서버는 `CAMERA_WATCH_DIR`에서 새 이미지 파일을 기다린다.
- 새 파일이 생기면 파일 크기가 안정될 때까지 기다린 뒤 `captures/{session_id}/current_{slot}.jpg`로 복사한다.

권장 감시 규칙:

- 허용 확장자: `.jpg`, `.jpeg`, `.png`
- 타임아웃: 30초
- 안정화 확인: 1초 간격으로 파일 크기 2회 동일
- 중복 방지: 마지막 처리 파일 목록 저장

### 3단계: Nikon 직접 제어 검토

Windows에서 검토 순서:

1. Nikon 카메라가 USB 테더링 및 PC 제어를 지원하는지 확인
2. Nikon 공식 소프트웨어 또는 SDK 확인
3. digiCamControl 설치 및 CLI 가능 여부 확인
4. 앱에서 외부 명령 실행 방식으로 촬영 트리거
5. 실패하면 폴더 감시 + 수동 셔터 방식 유지

### 4단계: 실시간 프리뷰 연결

- Nikon 카메라의 HDMI 출력이 가능한지 확인한다.
- 카메라 모델이 clean HDMI를 지원하는지 확인한다.
- HDMI 캡처카드를 노트북에 연결하고 Windows 카메라 앱 또는 브라우저에서 영상 장치로 잡히는지 확인한다.
- 프론트엔드의 `CameraPreview.tsx`에서 `getUserMedia()`로 캡처카드 영상을 표시한다.
- 프리뷰 영상은 구도 확인용으로만 사용하고, 합성용 이미지는 `watch_folder` 또는 Nikon 직접 제어 결과 파일을 사용한다.

권장 장비:

- Nikon 카메라 HDMI 출력 케이블
- USB HDMI 캡처카드
- 장시간 운영용 더미 배터리 또는 전원 어댑터
- 노트북 또는 외부 모니터

프리뷰 구현 기준:

- 브라우저 권한 요청 실패 시 안내 메시지를 표시한다.
- 여러 영상 장치가 있을 경우 장치 선택 UI를 제공한다.
- 캡처카드가 연결되지 않아도 촬영 플로우는 더미/폴더 감시 모드로 계속 가능해야 한다.
- 태블릿 원격 프리뷰는 MVP 이후 기능으로 분리한다.

### fallback 전략

- 카메라 미연결: 더미 모드 또는 수동 업로드 모드로 전환
- 촬영 실패: 같은 slot 재촬영
- 파일 감시 타임아웃: 운영자에게 카메라 상태 확인 메시지 표시
- 직접 제어 실패: 폴더 감시 방식으로 복귀
- 프리뷰 장치 미연결: 실시간 화면 없이 촬영 진행 또는 외부 카메라 LCD로 구도 확인

## 10. 데이터 저장 전략

### 세션 ID 생성 방식

형식:

```text
YYYYMMDD-HHMMSS-random6
```

예시:

```text
20260610-184501-a1b2c3
```

장점:

- 생성 시점 확인 가능
- 파일 정렬 쉬움
- 충돌 가능성 낮음

### 원본 촬영 이미지 저장

```text
captures/{session_id}/current_1.jpg
captures/{session_id}/current_2.jpg
```

원본은 디버깅과 재합성을 위해 보관한다. 개인정보 이슈가 있으므로 보관 기간을 명확히 둔다.

### 합성 결과 이미지 저장

```text
output/sessions/{session_id}/final.jpg
```

갤러리와 다운로드 API는 이 파일을 기준으로 응답한다.

### QR 코드 저장 여부

MVP에서는 저장한다.

```text
output/sessions/{session_id}/qr.png
```

추후에는 동적 생성으로 변경 가능하다.

### 세션 메타데이터

```text
output/sessions/{session_id}/session.json
```

예시:

```json
{
  "id": "20260610-184501-a1b2c3",
  "status": "composed",
  "created_at": "2026-06-10T18:45:01+09:00",
  "template_id": "default",
  "old_photos": ["assets/old-photos/old_1.jpg", "assets/old-photos/old_2.jpg"],
  "captures": ["captures/20260610-184501-a1b2c3/current_1.jpg", "captures/20260610-184501-a1b2c3/current_2.jpg"],
  "final_image": "output/sessions/20260610-184501-a1b2c3/final.jpg",
  "gallery_url": "/gallery/20260610-184501-a1b2c3"
}
```

### 오래된 파일 삭제 정책

- 개발 환경: 자동 삭제 없음
- 행사 운영 환경:
  - 기본 보관 기간: 7일
  - 관리자 설정으로 1일, 7일, 30일 선택
  - 삭제 대상: `captures/`, `output/sessions/`
  - 삭제 전 운영자 백업 옵션 제공

### 개인정보/초상권 주의사항

- 화면 또는 안내문에 결과물이 일정 기간 저장된다는 사실을 표시한다.
- 외부 공유 URL은 예측이 어려운 세션 ID를 사용한다.
- 관리자 화면에는 전체 갤러리 공개를 기본 제공하지 않는다.
- 행사 종료 후 원본과 결과물 삭제 절차를 운영 매뉴얼에 포함한다.

## 11. 테스트 계획

### 이미지 합성 테스트

- 서로 다른 비율의 이미지 4장으로 합성 테스트
- 세로/가로 사진 혼합 테스트
- EXIF 회전이 있는 스마트폰 사진 테스트
- 과거 사진 누락 시 에러 테스트
- 템플릿 JSON 오류 테스트

### API 테스트

- 세션 생성 성공
- 존재하지 않는 세션 조회 실패
- 촬영 slot 1/2 성공
- 잘못된 slot 요청 실패
- 촬영 2장 미만 상태에서 합성 실패
- 합성 완료 후 다운로드 성공

### QR 링크 테스트

- PC 브라우저에서 QR URL 접속
- iPhone Safari 접속
- Android Chrome 접속
- 같은 Wi-Fi가 아닌 네트워크에서 실패하는지 확인
- Cloudflare Tunnel 사용 시 외부 접속 확인

### 모바일 다운로드 테스트

- 이미지 길게 눌러 저장 가능 여부 확인
- 다운로드 버튼 동작 확인
- 파일명이 정상적으로 내려오는지 확인
- 세로 화면에서 결과 이미지가 잘 보이는지 확인

### 카메라 미연결 상황 테스트

- `CAMERA_MODE=watch_folder`에서 새 파일이 안 생기는 경우
- 카메라 촬영 중 USB 연결 해제
- 파일 생성 중 서버가 먼저 읽으려는 경우
- 재시도 버튼으로 같은 slot 재촬영 가능 여부

### 현장 운영 테스트

- 연속 20회 이상 촬영
- 서버 재시작 후 기존 세션 조회
- 노트북 절전 모드 비활성화 확인
- 디스크 용량 부족 상황 점검
- Wi-Fi 재연결 후 QR 접속 확인

## 12. 운영 시나리오

### 행사 시작 전 준비

1. 노트북 전원 연결
2. 카메라 전원 및 배터리 확인
3. HDMI 캡처카드 연결 및 프리뷰 확인
4. 카메라 USB 연결
5. 카메라 저장 모드 확인
6. 서버 PC와 사용자 휴대폰이 같은 Wi-Fi에 접속 가능한지 확인
7. `assets/old-photos/old_1.jpg`, `old_2.jpg` 교체
8. 프레임 템플릿 확인
9. 백엔드 실행
10. 프론트엔드 실행
11. 테스트 세션 1회 생성
12. 휴대폰으로 QR 다운로드 확인

### 촬영 진행

1. 운영자가 촬영 화면을 연다.
2. 사용자가 위치를 잡는다.
3. 운영자가 `촬영 시작`을 누른다.
4. 앱이 카운트다운 후 첫 번째 사진을 촬영한다.
5. 앱이 카운트다운 후 두 번째 사진을 촬영한다.
6. 앱이 자동 합성을 실행한다.
7. 결과와 QR 코드가 화면에 표시된다.
8. 사용자가 QR 코드를 스캔해 저장한다.
9. 운영자가 `새 촬영`을 눌러 다음 사용자로 넘어간다.

### 오류 발생 시 대응

- QR 접속 실패:
  - 휴대폰 Wi-Fi 확인
  - 서버 IP 확인
  - 방화벽 허용 확인
- 카메라 촬영 실패:
  - 카메라 전원 확인
  - USB 재연결
  - fallback으로 수동 촬영 후 폴더 감시 사용
- 실시간 프리뷰 실패:
  - 브라우저 카메라 권한 확인
  - HDMI 케이블 및 캡처카드 재연결
  - Windows 카메라 앱에서 캡처카드 인식 여부 확인
  - 프리뷰 없이 카메라 LCD 또는 외부 모니터로 구도 확인
- 이미지 합성 실패:
  - 현재 사진 2장 존재 확인
  - 과거 사진 파일 존재 확인
  - 템플릿 JSON 문법 확인
- 다운로드 실패:
  - `output/sessions/{session_id}/final.jpg` 존재 확인
  - 서버 로그 확인

## 13. 리스크와 대응책

### Nikon 카메라 제어 문제

- 리스크: 모델별 SDK/테더링 지원이 다르다.
- 대응:
  - 직접 제어를 MVP 필수로 두지 않는다.
  - 더미 모드와 폴더 감시 모드를 먼저 구현한다.
  - 운영 전 실제 카메라 모델로 별도 PoC를 진행한다.

### 실시간 프리뷰 문제

- 리스크: Nikon 모델이 clean HDMI를 지원하지 않거나 캡처카드가 브라우저에서 안정적으로 잡히지 않을 수 있다.
- 대응:
  - 프리뷰는 MVP 촬영 파일 처리와 분리한다.
  - HDMI 캡처카드가 Windows에서 웹캠 장치로 인식되는지 먼저 검증한다.
  - 브라우저 권한 차단, 다른 프로그램의 장치 점유, 케이블 불량을 운영 체크리스트에 포함한다.
  - 프리뷰 실패 시에도 폴더 감시/수동 촬영으로 촬영 플로우를 계속 진행할 수 있게 한다.

### 촬영 이미지 전송 지연

- 리스크: 촬영 후 파일이 서버에 늦게 도착한다.
- 대응:
  - 폴더 감시 타임아웃을 설정한다.
  - 파일 크기 안정화 확인 후 읽는다.
  - UI에 `사진 전송 중` 상태를 표시한다.

### 네트워크 접속 문제

- 리스크: 휴대폰이 로컬 서버에 접근하지 못한다.
- 대응:
  - 서버 PC 고정 IP를 설정한다.
  - 같은 Wi-Fi 접속을 안내한다.
  - Windows 방화벽 허용 규칙을 문서화한다.
  - 외부 접속이 필요하면 Cloudflare Tunnel을 사용한다.

### QR 링크 접근 문제

- 리스크: QR에 `localhost`가 들어가면 휴대폰에서 접속할 수 없다.
- 대응:
  - QR URL은 반드시 서버 PC의 LAN IP 또는 터널 URL을 사용한다.
  - `PUBLIC_BASE_URL` 환경 변수를 둔다.
  - 관리자 화면에서 현재 QR URL을 미리 확인한다.

### 이미지 크롭/비율 문제

- 리스크: 얼굴이 잘리거나 사진 구도가 이상해질 수 있다.
- 대응:
  - MVP에서는 중앙 크롭을 사용한다.
  - 촬영 위치 가이드를 화면에 표시한다.
  - 추후 얼굴 인식 기반 크롭 옵션을 추가한다.

### 세션 충돌 문제

- 리스크: 여러 사용자가 연속 촬영할 때 파일이 섞일 수 있다.
- 대응:
  - 모든 파일은 `session_id` 폴더 아래 저장한다.
  - 촬영 중에는 새 촬영 버튼을 비활성화한다.
  - 서버는 세션 상태 전이를 엄격히 검증한다.

## 14. 개발 체크리스트

### High

- [ ] `backend/app/main.py` FastAPI 기본 서버 생성
- [ ] `backend/app/core/config.py` 환경 변수 로딩 구현
- [ ] `backend/app/services/session_service.py` 세션 생성/조회 구현
- [ ] `backend/app/services/compose_service.py` 4컷 합성 구현
- [ ] `assets/frames/default.json` 기본 템플릿 작성
- [ ] `assets/old-photos/old_1.jpg`, `old_2.jpg` 샘플 배치
- [ ] `POST /api/session` 구현
- [ ] `POST /api/session/{id}/capture` 더미 모드 구현
- [ ] `POST /api/session/{id}/compose` 구현
- [ ] `GET /gallery/{id}` 구현
- [ ] `GET /download/{id}` 구현
- [ ] `GET /api/session/{id}/qr` 구현
- [ ] `frontend/src/pages/CapturePage.tsx` 촬영 화면 구현
- [ ] `frontend/src/components/CameraPreview.tsx` 실시간 프리뷰 컴포넌트 구현
- [ ] `frontend/src/components/QrPanel.tsx` QR 표시 구현
- [ ] 휴대폰에서 QR 접속 테스트

### Medium

- [ ] `backend/app/camera/watch_folder.py` 폴더 감시 모드 구현
- [ ] HDMI 캡처카드 기반 프리뷰 PoC 진행
- [ ] 프리뷰 장치 선택 UI 구현
- [ ] `backend/app/services/cleanup_service.py` 오래된 세션 삭제 구현
- [ ] `frontend/src/pages/AdminPage.tsx` 운영 점검 화면 구현
- [ ] 촬영 실패 시 재시도 UI 구현
- [ ] 합성 결과 미리보기 UI 개선
- [ ] Windows 방화벽/네트워크 설정 문서 작성
- [ ] `docs/camera-setup.md` Nikon 연결 문서 작성
- [ ] `docs/operations.md` 행사 운영 매뉴얼 작성

### Low

- [ ] 여러 프레임 템플릿 선택 기능
- [ ] 과거 사진 세트 관리 기능
- [ ] 얼굴 인식 기반 크롭 검토
- [ ] 프린터 연동 검토
- [ ] Cloudflare Tunnel 자동 실행 스크립트 검토
- [ ] 관리자용 전체 결과물 다운로드 기능
- [ ] 행사명/날짜/로고 텍스트 오버레이 기능

## MVP 완료 기준

MVP는 다음 조건을 만족하면 완료로 본다.

- 카메라 없이 더미 이미지로 전체 플로우가 동작한다.
- 과거 사진 2장과 현재 사진 2장을 합성해 `final.jpg`를 만든다.
- 브라우저에서 촬영 시작부터 결과 QR 표시까지 진행 가능하다.
- 휴대폰으로 QR을 스캔해 결과 이미지를 열고 저장할 수 있다.
- 카메라 연동 실패 상황에서도 수동 또는 더미 모드로 시연 가능하다.

## MVP 이후 우선순위

1. 폴더 감시 방식으로 실제 Nikon 촬영 파일 연결
2. 행사장 네트워크 안정화
3. 프레임 템플릿 관리
4. 관리자 화면
5. 직접 카메라 제어 또는 프린터 연동
