# Reshot ROADMAP

## 1. 프로젝트 목표

Reshot은 행사 현장에서 운영자가 로컬 PC로 촬영 플로우를 진행하고, 참가자가 QR 코드로 결과 이미지를 받을 수 있게 하는 포토부스 앱이다.

현재 구현 방향은 다음과 같다.

- 한 세션에서 현재 사진 8장을 순서대로 촬영한다.
- 촬영 중에는 브라우저 카메라 또는 HDMI 캡처 장치로 구도를 확인한다.
- 촬영 완료 후 8장 중 최종 4컷에 사용할 사진 4장을 고른다.
- 선택한 4장을 세로형 4컷 템플릿에 합성한다.
- 결과 화면에서 최종 이미지를 크게 보여주고, QR 모달과 처음 화면 이동 버튼을 제공한다.
- 백엔드는 세션, 촬영 원본, 합성 결과, QR 이미지를 파일 시스템에 저장한다.

---

## 2. 현재 구현된 사용자 흐름

```text
시작 화면
  -> Start 클릭
  -> 세션 자동 생성
  -> 촬영 화면 이동
  -> 프리뷰 소스 선택
  -> 5초 카운트다운 후 1~8번 사진 연속 촬영
  -> 촬영 완료 후 선택 화면 표시
  -> 4컷 프레임의 각 칸을 누르고 8장 중 1장 선택
  -> Save final 클릭
  -> final.jpg 합성 + qr.png 생성
  -> 결과 화면 이동
  -> QR 보기 또는 처음으로 이동
```

### 촬영 화면

- `PhotoStripPreview`가 촬영 전후 상태를 전환한다.
- `LiveCameraPreview`가 브라우저 `getUserMedia` 입력을 보여준다.
- 프리뷰 장치 목록은 `videoinput` 기준으로 표시하며, 선택값은 `localStorage`에 저장한다.
- 장치명이 `capture`, `hdmi`, `cam link`, `usb video`, `uvc`를 포함하면 우선 선택 후보로 사용한다.
- 촬영 버튼을 누르면 남은 slot부터 8번까지 5초 카운트다운 후 순차 촬영한다.
- 프리뷰가 실패해도 최근 촬영 이미지 또는 fallback 상태가 표시된다.

### 선택 화면

- 촬영 8장이 모두 존재하면 선택 모드로 전환한다.
- 최종 4컷 프레임의 칸을 누르면 8장 선택 모달이 열린다.
- 이미 다른 칸에 배치한 사진을 새 칸에 선택하면 기존 배치는 해제된다.
- 4개 칸이 모두 채워지면 `Save final`이 활성화된다.
- 선택 slot은 `selected_capture_slots`로 백엔드에 전달된다.

### 결과 화면

- 최종 이미지는 `1200 / 1854` 비율의 프레임 안에 표시된다.
- 하단에는 `QR 보기`, `처음으로` 버튼만 둔다.
- QR은 결과 화면에 상시 노출하지 않고 모달로 표시한다.
- QR은 `/sessions/{session_id}/image`를 가리키는 직접 이미지 링크 방식이다.

---

## 3. 현재 API 구조

| 메서드 | 경로 | 상태 | 설명 |
| --- | --- | --- | --- |
| `GET` | `/` | 구현 | 기본 상태 확인 |
| `GET` | `/health` | 구현 | 서버 상태, 카메라 모드, 저장 경로 확인 |
| `POST` | `/sessions` | 구현 | 세션 생성 |
| `GET` | `/sessions/{session_id}` | 구현 | 세션 메타데이터 조회 |
| `POST` | `/sessions/{session_id}/capture` | 구현 | slot 1~8 촬영 또는 dummy 생성 |
| `GET` | `/sessions/{session_id}/capture/{slot}` | 구현 | 촬영 이미지 조회 |
| `GET` | `/old-photos/{slot}` | 구현 | fallback 과거 사진 조회 |
| `POST` | `/sessions/{session_id}/compose` | 구현 | 선택한 4장 합성, QR 생성 |
| `GET` | `/sessions/{session_id}/image` | 구현 | 최종 이미지 반환 |
| `POST` | `/sessions/{session_id}/qr` | 구현 | QR 생성 또는 재생성 |
| `GET` | `/sessions/{session_id}/qr` | 구현 | QR 이미지 반환 |

별도 `/gallery/{id}` 또는 `/download/{id}` 라우트는 아직 없다.

---

## 4. 저장 구조

```text
captures/{session_id}/current_1.jpg
captures/{session_id}/current_2.jpg
...
captures/{session_id}/current_8.jpg

output/sessions/{session_id}/final.jpg
output/sessions/{session_id}/qr.png
output/sessions/{session_id}/session.json
```

세션 ID 형식:

```text
YYYYMMDD-HHMMSS-random6
```

예시:

```text
20260704-105143-d1f242
```

---

## 5. 이미지 합성 규칙

기본 템플릿: `assets/frames/default.json`

- 캔버스: `1200 x 1854`
- 사진 슬롯: `518 x 744`
- 슬롯 개수: 4개
- 배경: `#000000`
- 로고: `assets/frames/mpnu-logo.png`
- 텍스트: `매직PNU 홈커밍 26.07.04`
- 저장 형식: JPEG quality 92

현재 선택 합성 방식:

```text
selected_capture_slots: [a, b, c, d]

slot a -> template key old_1 위치
slot b -> template key current_1 위치
slot c -> template key current_2 위치
slot d -> template key old_2 위치
```

템플릿 key 이름은 기존 과거 사진 2장 + 현재 사진 2장 구조에서 온 이름이다. 현재 UI에서는 네 칸 모두 사용자가 선택한 현재 촬영 사진으로 채운다.

---

## 6. 완료된 작업

### 프론트엔드

- [x] 시작 화면
- [x] `/shoot` 촬영 화면
- [x] 세션 자동 생성
- [x] 브라우저 라이브 프리뷰
- [x] 프리뷰 소스 선택 및 선택값 저장
- [x] 5초 카운트다운
- [x] 8장 순차 촬영
- [x] 최신 촬영 이미지 fallback 표시
- [x] 4컷 선택 화면
- [x] 8장 선택 모달
- [x] 중복 선택 해제 로직
- [x] 선택한 4장 합성 요청
- [x] 결과 화면
- [x] QR 모달
- [x] 처음 화면 이동
- [x] 결과 이미지 프레임과 하단 버튼 분리 레이아웃
- [x] 한국어 버튼 텍스트 깨짐 방지 스타일

### 백엔드

- [x] FastAPI 앱 구성
- [x] 환경변수 설정 로딩
- [x] 세션 생성/조회
- [x] slot 1~8 촬영 저장
- [x] `dummy` 카메라 모드
- [x] `watch_folder` 카메라 모드
- [x] 선택 트리거 명령 실행
- [x] 촬영 이미지 조회
- [x] 선택 slot 4개 검증
- [x] 선택 slot 4개 합성
- [x] 최종 이미지 저장
- [x] QR 이미지 생성 및 조회
- [x] 세션 메타데이터 저장

### 운영 보조

- [x] `.env.example` 기본값 정리
- [x] `frontend/.env.example` 추가
- [x] NX Tether 창 포커스 및 `Ctrl+1` 전송 스크립트
- [x] 로컬 네트워크 QR 설정 문서화

---

## 7. 남은 작업

### High

- [ ] 실제 행사 환경에서 전체 플로우 반복 테스트
- [ ] `CAMERA_MODE=watch_folder`와 NX Tether 저장 폴더 연동 장시간 테스트
- [ ] `tools/trigger_nx_tether.ps1`이 현장 PC의 NX Tether 단축키와 맞는지 검증
- [ ] iPhone Safari와 Android Chrome에서 QR 열기 및 이미지 저장 검증
- [ ] 촬영 실패 시 사용자에게 명확한 재시도 UI 제공
- [ ] Windows 방화벽, 같은 Wi-Fi, 핫스팟 운영 절차 최종 점검

### Medium

- [ ] 촬영 중 취소/처음부터 다시 시작 UX
- [ ] 8장 중 개별 재촬영 UX
- [ ] 선택 화면에서 이미 배치된 사진 표시 개선
- [ ] 결과 화면에서 QR URL 또는 접속 상태 확인 기능
- [ ] 세션 정리 정책과 오래된 파일 삭제 기능
- [ ] 운영자용 상태 화면
- [ ] 오류 로그 확인 가이드

### Low

- [ ] 여러 템플릿 선택
- [ ] 로고, 이벤트명, 날짜 오버레이 옵션
- [ ] Cloudflare Tunnel 또는 ngrok 운영 모드
- [ ] 프린터 연동
- [ ] 관리자 일괄 다운로드
- [ ] 얼굴 인식 기반 크롭 보정 검토

---

## 8. 카메라 연동 전략

### 현재 상태

- `dummy` 모드로 전체 UI와 합성 플로우를 개발/검증할 수 있다.
- `watch_folder` 모드가 구현되어 있으며, 새 JPG를 감시하고 안정화 후 복사한다.
- 선택적으로 `CAMERA_TRIGGER_COMMAND`를 실행해 NX Tether 같은 외부 프로그램에 촬영 명령을 보낼 수 있다.
- Nikon 직접 제어 어댑터 파일은 placeholder 상태다.

### 권장 단계

1. `dummy` 모드로 행사 전 UI/QR/합성 검증
2. `watch_folder` 모드로 NX Tether 또는 보조 프로그램이 저장한 파일 감시
3. 트리거 명령으로 촬영 버튼 자동화 검증
4. 안정성이 부족하면 운영자 수동 촬영 + watch folder 감시 방식으로 후퇴
5. 필요성이 명확하면 Nikon 직접 제어 또는 digiCamControl 연동 검토

### 실시간 프리뷰 원칙

- 프리뷰는 구도 확인용이다.
- 최종 합성에는 카메라가 저장한 JPEG 원본을 사용한다.
- 프리뷰 실패가 촬영 플로우 전체를 막지 않게 한다.
- 운영 PC의 프리뷰는 `localhost`에서 여는 것을 기준으로 한다.

---

## 9. 운영 리스크와 대응

### QR 접속 실패

원인:

- QR에 `localhost`가 들어감
- 휴대폰과 서버 PC가 다른 네트워크에 있음
- Windows 방화벽이 8000 포트를 막음

대응:

- `PUBLIC_BASE_URL`을 서버 PC의 LAN IP로 설정
- 휴대폰에서 `http://{서버_IP}:8000/health` 사전 확인
- 행사장에서는 같은 Wi-Fi 또는 핫스팟 사용

### 촬영 파일 누락

원인:

- 카메라 저장 지연
- watch folder 경로 불일치
- 파일 쓰기 완료 전 처리
- 트리거 명령 실패

대응:

- `CAMERA_WATCH_DIR` 실제 저장 위치 확인
- `CAMERA_CAPTURE_TIMEOUT_SECONDS` 여유 있게 설정
- 파일 크기 안정화 후 복사 로직 유지
- 실패 slot 재촬영 UI 추가

### 프리뷰 실패

원인:

- 브라우저 카메라 권한 거부
- LAN HTTP 주소에서 `getUserMedia` 제한
- HDMI 캡처 장치 드라이버 또는 연결 문제

대응:

- 운영 화면은 `http://localhost:5173`에서 실행
- 프리뷰 소스 선택 드롭다운에서 장치 확인
- 프리뷰 실패 시에도 촬영 파일 기반 플로우는 유지

### 결과 이미지 잘림

원인:

- 결과 이미지 영역과 하단 버튼 바가 겹침
- 컨테이너 비율과 이미지 비율 불일치

대응:

- 결과 화면에서 버튼 바 높이를 먼저 예약
- `final-image-wrap`을 최종 이미지와 같은 `1200 / 1854` 비율로 유지
- 이미지는 `object-fit: contain`으로 표시

### 텍스트 깨짐

원인:

- 문서와 소스 인코딩 불일치
- 버튼 폭 부족으로 한글 줄바꿈
- 한국어 폰트 fallback 부족

대응:

- 문서와 소스를 UTF-8로 저장
- `Malgun Gothic`, `Apple SD Gothic Neo`, `Noto Sans KR` fallback 유지
- 버튼 텍스트는 `white-space: nowrap`, `word-break: keep-all` 적용

---

## 10. 테스트 계획

### 개발 테스트

- [ ] `npm run build` 통과
- [ ] `uvicorn app.main:app` 실행
- [ ] `/health` 응답 확인
- [ ] 세션 생성 API 확인
- [ ] slot 1~8 capture API 확인
- [ ] selected_capture_slots 4개 합성 확인
- [ ] 중복 slot, 범위 밖 slot 에러 확인
- [ ] final.jpg 생성 확인
- [ ] qr.png 생성 확인

### 카메라 테스트

- [ ] `dummy` 모드 전체 플로우 확인
- [ ] `watch_folder` 모드에서 새 JPG 감지 확인
- [ ] `CAMERA_TRIGGER_COMMAND` 성공/실패 확인
- [ ] NX Tether 저장 폴더와 `CAMERA_WATCH_DIR` 일치 확인
- [ ] 파일 저장 지연 상황에서 timeout 동작 확인

### UI 테스트

- [ ] 시작 화면에서 촬영 화면 이동
- [ ] 라이브 프리뷰 권한 요청 및 소스 선택
- [ ] 카운트다운 표시
- [ ] 8장 촬영 후 선택 화면 전환
- [ ] 4개 프레임에 각각 사진 선택
- [ ] 이미 선택된 사진 재배치 동작 확인
- [ ] Save final 비활성/활성 상태 확인
- [ ] 결과 화면 최종 이미지 비율 확인
- [ ] QR 모달 열기/닫기
- [ ] 처음으로 버튼 동작 확인
- [ ] 한국어 텍스트 깨짐 여부 확인

### 현장 테스트

- [ ] 같은 Wi-Fi에서 휴대폰 QR 접근
- [ ] iPhone Safari 저장 확인
- [ ] Android Chrome 저장 확인
- [ ] 20세션 이상 반복 촬영
- [ ] 서버 재시작 후 기존 결과 조회
- [ ] 네트워크 재연결 후 QR 접근

---

## 11. MVP 완료 기준

MVP는 다음 조건을 만족하면 완료로 본다.

- `dummy`와 `watch_folder` 중 현장 운영 모드 하나에서 시작부터 결과 QR까지 끊기지 않는다.
- 8장 촬영 후 4장 선택 합성이 안정적으로 동작한다.
- 최종 이미지가 잘리지 않고 결과 화면에 표시된다.
- QR을 휴대폰으로 스캔해 결과 이미지를 열 수 있다.
- 현장 운영자가 실패 원인을 확인하고 다시 시도할 수 있다.
- 실제 카메라 연동 전에도 데모와 리허설이 가능하다.

---

## 12. 다음 우선순위

1. 실제 백엔드와 프론트엔드 빌드 실행 환경 점검
2. `dummy` 모드 전체 플로우를 브라우저에서 캡처하며 검증
3. `watch_folder`와 NX Tether 저장 폴더 연결 테스트
4. 모바일 QR 열기와 이미지 저장 테스트
5. 실패 복구 UI와 운영자 가이드 보강
