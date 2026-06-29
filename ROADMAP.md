# Reshot ROADMAP

## 1. 프로젝트 목표

Reshot은 행사 현장에서 운영자가 로컬 PC로 촬영 플로우를 진행하고, 참가자가 QR 코드로 결과 이미지를 받을 수 있게 하는 포토부스 앱이다.

현재 구현 방향은 다음과 같다.

- 한 세션에서 현재 사진 8장을 촬영한다.
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
  -> 7초 카운트다운 후 1~8번 사진 연속 촬영
  -> 촬영 완료 후 선택 화면 표시
  -> 4컷 프레임의 각 칸을 누르고 8장 중 1장 선택
  -> Save final 클릭
  -> final.jpg 합성 + qr.png 생성
  -> 결과 화면 이동
  -> QR 보기 또는 처음으로 이동
```

### 촬영 화면

- `PhotoStripPreview`가 촬영 전/후 상태를 모두 담당한다.
- 촬영 중에는 `shooting-preview` 영역이 최신 촬영 이미지를 크게 보여준다.
- 실시간 뷰 영역은 `518 / 744` 비율을 유지하되, 최근 수정으로 좌우 여백을 줄여 더 크게 보이도록 했다.
- 현재 UI는 8장을 순차 촬영한다. 중간에 개별 재촬영 UI는 아직 없다.

### 선택 화면

- 촬영 8장이 모두 존재하면 선택 모드로 전환된다.
- 최종 4컷 프레임의 칸을 누르면 사진 선택 모달이 뜬다.
- 8장 중 선택한 사진 4장이 `selected_capture_slots`로 백엔드에 전달된다.
- 선택 slot은 4개, 중복 없음, 1~8 범위여야 한다.

### 결과 화면

- 최종 이미지는 `1200 / 1854` 비율의 검은 프레임 안에 표시한다.
- 프레임은 하단 버튼 바와 분리해서 계산한다.
- 하단 버튼 바에는 `QR 보기`, `처음으로` 버튼만 둔다.
- QR은 결과 화면에 상시 노출하지 않고 모달로 표시한다.
- 한국어 버튼 텍스트 깨짐 방지를 위해 폰트 fallback과 줄바꿈 방지 스타일을 적용했다.

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
| `POST` | `/sessions/{session_id}/qr` | 구현 | QR 생성/재생성 |
| `GET` | `/sessions/{session_id}/qr` | 구현 | QR 이미지 반환 |

현재 별도 `/gallery/{id}` 또는 `/download/{id}` 라우트는 없다. QR은 `/sessions/{session_id}/image`를 가리키는 이미지 직접 링크 방식이다.

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
20260629-105143-d1f242
```

---

## 5. 이미지 합성 규칙

기본 템플릿: `assets/frames/default.json`

- 캔버스: `1200 x 1854`
- 사진 슬롯: `518 x 744`
- 슬롯 개수: 4개
- 배경: `#000000`
- 로고: `assets/frames/mpnu-logo.png`
- 저장 형식: JPEG quality 92

현재 선택 합성 방식:

```text
selected_capture_slots: [a, b, c, d]

slot a -> frame old_1 위치
slot b -> frame current_1 위치
slot c -> frame current_2 위치
slot d -> frame old_2 위치
```

프레임 키 이름은 기존 2장 과거 사진 + 2장 현재 사진 구조에서 온 이름이다. 현재 UI에서는 네 칸 모두 사용자가 선택한 현재 촬영 사진으로 채운다.

---

## 6. 완료된 작업

### 프론트엔드

- [x] 시작 화면
- [x] `/shoot` 촬영 화면
- [x] 세션 자동 생성
- [x] 7초 카운트다운
- [x] 8장 순차 촬영
- [x] 최신 촬영 이미지 큰 미리보기
- [x] 4컷 선택 화면
- [x] 8장 선택 모달
- [x] 선택한 4장 합성 요청
- [x] 결과 화면
- [x] QR 모달
- [x] 처음 화면 이동
- [x] 결과 이미지 프레임/버튼 바 분리 레이아웃
- [x] 한국어 버튼 텍스트 깨짐 방지
- [x] shoot 미리보기 영역 확대

### 백엔드

- [x] FastAPI 앱 구성
- [x] 환경변수 설정 로딩
- [x] 세션 생성/조회
- [x] slot 1~8 촬영 저장
- [x] dummy 카메라 모드
- [x] 촬영 이미지 조회
- [x] 선택 slot 4개 합성
- [x] 최종 이미지 저장
- [x] QR 이미지 생성 및 조회
- [x] 세션 메타데이터 저장

---

## 7. 남은 작업

### High

- [ ] 실제 행사 환경에서 전체 플로우 반복 테스트
- [ ] 백엔드 의존성 설치 절차 검증 (`qrcode[pil]` 포함)
- [ ] `CAMERA_MODE=watch_folder` 실제 카메라 저장 폴더 연동 테스트
- [ ] 촬영 실패 시 사용자에게 명확한 복구 UI 제공
- [ ] 최종 이미지와 QR을 iPhone/Android에서 열고 저장하는 절차 검증
- [ ] Windows 방화벽, 같은 Wi-Fi, 핫스팟 운영 절차 문서화

### Medium

- [ ] 촬영 중 취소/재시작 UX
- [ ] 촬영 8장 중 개별 재촬영 UX
- [ ] 선택 화면에서 이미 선택된 사진 표시 개선
- [ ] 결과 화면에서 QR URL/접속 상태 확인 기능
- [ ] 세션 정리 정책과 오래된 파일 삭제 기능
- [ ] 운영자용 상태 화면
- [ ] 오류 로그 확인 가이드

### Low

- [ ] 여러 템플릿 선택
- [ ] 로고/이벤트명/날짜 오버레이 옵션
- [ ] Cloudflare Tunnel 또는 ngrok 운영 모드
- [ ] 프린터 연동
- [ ] 관리자 일괄 다운로드
- [ ] 얼굴 인식 기반 크롭 품질 개선

---

## 8. 카메라 연동 전략

### 현재

- `dummy` 모드로 전체 UI와 합성 플로우를 개발/검증한다.
- 실제 Nikon 직접 제어는 아직 운영 안정화 전이다.

### 권장 단계

1. `dummy` 모드로 행사 전 UI/QR/합성 검증
2. `watch_folder` 모드로 Nikon 또는 보조 프로그램이 저장한 파일을 감시
3. 안정성이 확인되면 Nikon 직접 제어 또는 digiCamControl 연동 검토
4. 실시간 프리뷰는 촬영 파일 처리와 분리해서 HDMI 캡처 장치 또는 브라우저 카메라 입력으로 다룬다.

### 실시간 프리뷰 원칙

- 프리뷰는 구도 확인용이다.
- 최종 합성에는 카메라가 저장한 JPEG 원본을 사용한다.
- 프리뷰 실패가 촬영 플로우 전체를 막지 않게 한다.

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

대응:

- 파일 크기 안정화 확인 후 복사
- timeout과 명확한 오류 메시지 제공
- 실패 slot 재촬영 UI 추가

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

- 한글 문서/소스 인코딩 불일치
- 버튼 폭 부족으로 글자 줄바꿈
- 한국어 폰트 fallback 부족

대응:

- 문서와 소스를 UTF-8로 저장
- `Malgun Gothic`, `Apple SD Gothic Neo`, `Noto Sans KR` fallback 추가
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
- [ ] 중복 slot 또는 범위 밖 slot 에러 확인
- [ ] final.jpg 생성 확인
- [ ] qr.png 생성 확인

### UI 테스트

- [ ] 시작 화면에서 촬영 화면 이동
- [ ] 카운트다운 표시
- [ ] 8장 촬영 후 선택 화면 전환
- [ ] 4개 프레임에 각각 사진 선택
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

- `dummy` 모드에서 시작부터 결과 QR까지 끊기지 않는다.
- 8장 촬영 후 4장 선택 합성이 안정적으로 동작한다.
- 최종 이미지가 잘리지 않고 결과 화면에 표시된다.
- QR을 휴대폰으로 스캔해 결과 이미지를 열 수 있다.
- 현장 운영자가 실패 원인을 확인하고 다시 시도할 수 있다.
- 실제 카메라 연동 전에도 데모와 리허설이 가능하다.

---

## 12. 다음 우선순위

1. 실제 백엔드 실행 환경 의존성 점검
2. 전체 플로우를 실제 브라우저에서 화면 캡처로 검증
3. `watch_folder` 모드 연결 테스트
4. 모바일 QR 저장 테스트
5. 실패 복구 UI와 운영자 가이드 보강