# TerryPiQ — 프론트엔드

AI 기반 맞춤 테이핑 가이드 서비스의 프론트엔드입니다.  
React + Vite로 구성된 모바일 웹앱이며, 390px 중심의 앱형 레이아웃을 사용합니다.

---

## 기술 스택

| 항목 | 내용 |
|---|---|
| 프레임워크 | React 19 |
| 번들러 | Vite 8 |
| 라우팅 | React Router v7 |
| 상태 관리 | Context API (`SessionContext`) |
| 폰트 | Pretendard (CDN) |
| 스타일 | 글로벌 CSS (디자인 토큰 기반) |

---

## 화면 구성 및 라우트

| 경로 | 컴포넌트 | 화면 |
|---|---|---|
| `/` | `Splash` | 스플래시 — 로고, CTA |
| `/1` | `BodyPart` | 신체 부위 선택 (무릎 외 잠금) |
| `/2` | `SymptomInput` | 증상 입력 (상황 선택 → 증상 채팅) |
| `/consent` | `Consent` | 체형 정보 제공 동의 |
| `/3` | `BodyInfo` | 체형 정보 입력 (3탭: 기본정보 · 촬영가이드 · 사진업로드) |
| `/6` | `Analyzing` | AI 분석 중 로딩 화면 |
| `/7` | `ResultVideo` | 테이핑 옵션 추천 (A/B 선택) |
| `/9` | `TapingGuide` | 단계별 테이핑 가이드 + 챗봇 시트 |
| `/10` | `Complete` | 완료 화면 — 결과 저장/공유 |

> `/4`, `/5`, `/8`, `/11`은 각각 `/3`, `/3`, `/7`, `/`로 리다이렉트됩니다.

---

## 디자인 시스템

`src/index.css`에 CSS 변수로 정의된 토큰을 사용합니다.

```css
--color-primary: #ff7a00;       /* 오렌지 */
--color-secondary: #2563e8;     /* 파랑 (유저 말풍선) */
--color-primary-light: #fff3e0; /* 연한 오렌지 배경 */
--font-base: "Pretendard", ...;
--radius-md: 12px;
--radius-full: 9999px;
```

공통 UI 클래스 (`App.css`):
- `.page` — 전체 화면 레이아웃 (절대 위치, flex column)
- `.topbar` / `.bottombar` — 상단/하단 고정 영역
- `.content` — 스크롤 가능한 본문 영역
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-text` — 버튼
- `.chip`, `.chip.selected`, `.chip.locked` — 선택지 칩
- `.bubble-bot`, `.bubble-user`, `.typing` — 채팅 말풍선
- `.card`, `.badge-rec` — 카드 및 추천 뱃지
- `.dots`, `.step-tabs`, `.field`, `.seg` — 진행 표시 및 폼

---

## 세션 상태 (`SessionContext`)

```js
{
  part: '무릎',           // 선택된 신체 부위
  situation: null,        // 불편한 상황 (운동 전/중/후 등)
  symptom: null,          // 증상 텍스트
  height: null,           // 키 (cm)
  weight: null,           // 몸무게 (kg)
  gender: null,           // 성별
  photoUploaded: false,   // 사진 업로드 여부
  selected_option: 'A',  // 선택한 테이핑 옵션
}
```

---

## 개발 실행

```bash
npm install
npm run dev
```

빌드:

```bash
npm run build
```

---

## 주요 구현 사항 (2026-04-20)

- **디자인 핸드오프 완전 반영** — `TerryPiQ Prototype (standalone source).html` 기준으로 전 화면 재구현
- **Pretendard 폰트** 적용 (CDN)
- **모바일 쉘** — 최대 390px, 500px 이상 데스크톱에서 폰 프레임 표시
- **SC-02 Consent 페이지** 신규 추가 (`/consent`)
- **BodyInfo 3탭 통합** — 기존 `/3` `/4` `/5`를 단일 탭 UI(`/3`)로 병합
- **SymptomInput 2단계 통합** — 상황 선택(SC-01-2) + 증상 입력(SC-01-3)을 한 컴포넌트로
- **TapingGuide 챗봇 시트** — FAB 버튼 → 바텀 시트 인라인 구현
- **오렌지 디자인 토큰** (`#ff7a00`) 전체 적용
