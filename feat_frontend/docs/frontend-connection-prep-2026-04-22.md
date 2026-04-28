# 프론트-백엔드 연결 준비 현황 정리 (2026-04-22 수)

## 문서 목적

본 문서는 `Project Docs System`의 `#15 UserJourney`, `#16 Screen Spec`, `#17 Component Spec`, `#18 UX Writing Guide`, 그리고 `프론트 최종 정합성 감사 - 목금 연결용 (4/22)`를 기준으로 현재 프론트 코드 상태를 다시 정리한 문서입니다.

이번 작업의 목적은 서비스 전체 완성이 아니라, 목요일/금요일에 백엔드와 연결할 수 있는 최소 흐름을 준비하고 어떤 부분을 연결 대상으로 둘지 명확히 나누는 것입니다.

## 결론 요약

현재 프론트는 4/22 감사 문서에 적힌 블로커 중 여러 항목을 이미 수정한 상태입니다. 특히 `body_info_mode` 저장, `DualCTAButton` 사용, 파일 업로드 input 추가, EP2/EP3 호출 위치 마련, EP4 저장 호출, localStorage 히스토리 기록, History 라우트 수정, EP3 응답 필드명 대응은 오늘 코드에 반영되어 있습니다.

다만 실제 백엔드 연결 전에는 아직 최소 4가지를 더 맞춰야 합니다.

1. `Analyzing.jsx`의 EP2 `FormData`에 `session.image`를 append해야 합니다.
2. 정보 없이 시작하는 경로에서 EP3에 보낼 기본 `model_id` 값을 확정해야 합니다.
3. API prefix가 `/api`인지 `/api/v1`인지 백엔드와 맞춰야 합니다.
4. `ResultVideo.jsx`는 아직 실제 `<video src={video_url}>`가 아니라 placeholder입니다. 다만 영상 파일이 아직 없는 상태라 구조만 열어둔 것으로 볼 수 있습니다.

## 오늘 기준 수정 완료로 볼 수 있는 항목

### 1. 정보 제공 여부 분기 저장

- 기준 문서: 감사 문서 B-02, #17 SC-02
- 현재 코드: `src/pages/Consent.jsx`
- 상태: 완료

`정보 입력하고 시작할게요`를 누르면 `body_info_mode: "full"`을 저장하고 `/body-info`로 이동합니다. `정보 없이 시작할게요`를 누르면 `body_info_mode: null`을 저장하고 `/analyzing`으로 이동합니다. 또한 #17에서 요구한 `DualCTAButton`도 사용 중입니다.

### 2. 파일 업로드 input 추가

- 기준 문서: 감사 문서 B-03, #16 Scene 3, #17 ImageUploader
- 현재 코드: `src/pages/BodyInfo.jsx`
- 상태: 부분 완료

`<input type="file" accept="image/jpeg,image/png">`가 추가되었고, 파일 타입과 10MB 용량 검사를 한 뒤 `updateSession({ image: file })`로 File 객체를 저장합니다.

남은 점은 `Analyzing.jsx`에서 이 `session.image`를 EP2 `FormData`에 실제로 넣는 작업입니다.

### 3. EP2/EP3 호출 위치 마련

- 기준 문서: 감사 문서 B-01, #16 Scene 4, #17 SC-04
- 현재 코드: `src/pages/Analyzing.jsx`, `src/api/index.js`
- 상태: 연결 뼈대 완료, 일부 필드 누락

`Analyzing.jsx`에서 `body_info_mode === "full"`이면 EP2 `matchBody()`를 호출하고, 이후 EP3 `getTapingRecommend()`를 호출하도록 변경되어 있습니다. EP3 응답의 `options`를 `session.taping_options`에 저장하는 흐름도 있습니다.

남은 점:

- EP2 `FormData`에 `image`가 빠져 있습니다.
- `body_info_mode === null`일 때 `model_id`가 `null`로 전달됩니다. 백엔드가 기본 모델을 허용하지 않으면 실패할 수 있습니다.
- EP2 응답의 `match_type`, `body_metrics`, `glb_url`은 아직 세션에 저장하지 않습니다.

### 4. EP3 응답 필드명 대응

- 기준 문서: 감사 문서 W-02, W-03, #17 TapingOption
- 현재 코드: `src/api/index.js`, `src/context/SessionContext.jsx`, `src/pages/ResultVideo.jsx`, `src/pages/Complete.jsx`
- 상태: 대체로 완료

Mock option과 화면 렌더링이 `taping_id`, `tape_type`, `stretch_pct`, `video_url`, `step_glb_urls`, `disclaimer` 기준으로 바뀌었습니다. `selected_option`도 문자열이 아니라 숫자 index로 초기화되어 있습니다.

남은 점:

- `step_glb_urls`는 필드만 열려 있고 값은 빈 배열입니다.
- 실제 단계별 GLB 렌더링은 아직 구현하지 않습니다. 이는 Q-EM-17 및 호진 파트 결정 사항입니다.

### 5. 결과 저장 및 히스토리 기록

- 기준 문서: 감사 문서 B-04, B-05
- 현재 코드: `src/pages/Complete.jsx`, `src/api/index.js`
- 상태: 완료에 가까움

`결과 저장할게요` 클릭 시 `saveSession({ session_id, taping_id })`를 호출하고, 성공하면 localStorage `history`에 `{ date, body_part, option }` 형태로 기록합니다.

주의할 점:

- 현재 localStorage 기록은 EP4 성공 이후에만 실행됩니다.
- 백엔드 저장 API가 아직 불안정하면, 발표용 히스토리를 위해 mock 모드 또는 저장 실패 시 localStorage fallback 여부를 결정해야 합니다.

### 6. History 라우트 수정

- 기준 문서: 감사 문서 B-06, W-07
- 현재 코드: `src/pages/History.jsx`
- 상태: 부분 완료

기존의 없는 라우트 `/guide/1` 대신 `/result-3d`로 이동하도록 수정되어 있습니다.

남은 점:

- 버튼 문구는 `네, 같아요` / `아니요, 달라요`입니다. #18 확정 문구인 `네, 바로 시작할게요` / `아니요, 다시 선택할게요`와 완전히 같지는 않습니다.
- Scene 8의 Cosmos DB 히스토리 조회 API는 아직 없으므로 localStorage 기반 유지가 맞습니다.

## 아직 목요일/금요일 연결 때 처리해야 하는 항목

### A. EP2 사진 전송 누락

현재 `BodyInfo.jsx`는 File 객체를 저장하지만 `Analyzing.jsx`의 `FormData`에는 아래 필드만 들어갑니다.

```js
session_id
height_cm
weight_kg
gender
```

목요일 연결 전 아래 항목을 추가해야 합니다.

```js
if (session.image) {
  formData.append("image", session.image);
}
```

이 작업을 하지 않으면 백엔드 `/api/body/match`는 실제 사진을 받지 못합니다.

### B. 기본 model_id 확정

`정보 없이 시작하기` 경로는 EP2를 스킵하고 EP3만 호출합니다. 현재 코드는 `model_id: null`을 보냅니다.

목요일에 백엔드/호진 파트와 아래 중 하나를 결정해야 합니다.

1. 프론트에서 기본 `model_id`를 하드코딩해서 EP3에 보낸다.
2. 백엔드 EP3가 `model_id: null`을 받으면 기본 모델로 처리한다.
3. 별도 default model endpoint 또는 config를 둔다.

현재 상태는 2번을 기대하는 형태에 가깝지만, 감사 문서 기준으로는 아직 결정 필요 항목입니다.

### C. API prefix 통일

현재 `src/api/index.js`는 다음 경로를 호출합니다.

```plain text
/api/symptoms/analyze
/api/body/match
/api/taping/recommend
/api/session/save
```

감사 문서 D-04에는 백엔드 FastAPI 경로가 `/api/v1/...`일 수 있다고 되어 있습니다. 백엔드가 `/api/v1`을 쓰면 프론트 API 파일에서 prefix만 일괄 수정하면 됩니다.

### D. Scene Hospital 이후 session_id null 문제

`SymptomInput.jsx`에서 급성 부상 키워드가 감지되면 EP1 호출 전에 `/hospital`로 이동합니다. `SceneHospital.jsx`에서 `그래도 계속 진행할게요`를 누르면 `/consent`로 이동합니다.

이 경우 `session_id`가 없는 상태로 EP3까지 갈 수 있습니다. 목요일 연결 전 아래 중 하나를 결정해야 합니다.

1. `Consent` 또는 `Analyzing` 진입 시 `session_id`가 없으면 EP1을 먼저 호출한다.
2. 발표용으로 hospital 이후 계속 진행 경로는 mock fallback으로 둔다.
3. hospital 이후 계속 진행을 막고 처음부터 다시 시작하게 한다.

현재 코드는 2번에 가깝지만, 실제 API 연결에서는 백엔드 400 가능성이 있습니다.

### E. ResultVideo의 video_url 연결

EP3 옵션에는 `video_url` 필드가 들어오도록 구조가 맞춰져 있지만, 현재 `ResultVideo.jsx`는 실제 `<video>` 태그가 아니라 `video-placeholder`를 표시합니다.

다만 문서 기준으로 `.mp4` 파일 12개 중 업로드된 파일이 없으므로, 지금은 손대지 않아도 됩니다. 영상 파일과 URL이 준비되면 placeholder를 아래 구조로 교체하면 됩니다.

```jsx
<video src={o.video_url} controls playsInline />
```

### F. 3D 렌더링과 step_glb_urls

`TapingGuide.jsx`는 아직 `GUIDE_STEPS` 하드코딩과 3D placeholder를 사용합니다. `step_glb_urls` 필드는 타입과 mock 구조에는 열려 있지만 실제 렌더링에는 사용하지 않습니다.

이 부분은 문서의 Q-EM-17과 동일하게 호진 파트 및 GLB 단계 구조 결정 전까지 건드리지 않는 것이 맞습니다.

### G. 챗봇 API

`TapingGuide.jsx`의 챗봇 바텀시트는 현재 하드코딩 응답입니다. `/api/chat` 엔드포인트가 확정되지 않았으므로 지금 연결 대상에서 제외합니다.

### H. 아웃라이어 고지 UI

MD 계산 결과가 백엔드에서 오지 않으면 프론트에서 Scene 5 문구를 분기할 수 없습니다. 현재는 구현하지 않는 것이 맞습니다.

### I. BodyPart 선택값 하드코딩

`BodyPart.jsx`는 선택 가능한 부위가 현재 무릎뿐이라 실제 사용 흐름에서는 문제가 크지 않습니다. 다만 `pickPart()`에서 선택값을 저장한 뒤 `handleNext()`에서 다시 `part: "무릎"`으로 덮어쓰는 구조가 남아 있습니다.

MVP 범위가 무릎만이면 목요일 연결 블로커는 아닙니다. 이후 발목, 어깨 등을 열 계획이면 `handleNext()`의 하드코딩은 제거해야 합니다.

## 목요일 연결 순서 제안

1. 백엔드와 API prefix(`/api` vs `/api/v1`)를 확정합니다.
2. `Analyzing.jsx`에서 EP2 `FormData`에 `image`를 추가합니다.
3. 기본 `model_id` 처리 방식을 확정합니다.
4. EP2 응답의 `model_id`, `match_type`, `body_metrics`, `glb_url` 저장 범위를 맞춥니다.
5. EP3 응답 `options`, `coaching_text`, `disclaimer` 저장 구조를 백엔드 응답과 맞춥니다.
6. `ResultVideo.jsx`는 영상 파일이 준비되면 `video_url`을 `<video>`에 연결합니다.
7. EP4 저장 API가 준비되면 `Complete.jsx` 저장 흐름을 실제 서버 응답으로 테스트합니다.
8. History API가 없다면 localStorage 유지, API가 생기면 `History.jsx`만 교체합니다.

## 검증 결과

- `npm.cmd run build`: 성공
- `npm.cmd run lint`: 실패 3건

Lint 실패 항목:

1. `SessionContext.jsx`: React Fast Refresh 규칙. 동작 블로커는 아니지만 구조 분리하면 해결됩니다.
2. `SymptomInput.jsx`: `catch (error)`의 `error` 미사용.
3. `TapingGuide.jsx`: `session`을 import해서 꺼내지만 아직 사용하지 않음. 이는 `step_glb_urls` 연결을 위해 열어둔 흔적으로 볼 수 있습니다.

## 최종 상태 판단

현재 프론트는 목요일 연결을 시작할 수 있는 상태에 가까워졌습니다. 다만 “연결 가능한 최소 흐름”으로 보려면 EP2 이미지 전송, 기본 `model_id`, API prefix, hospital 이후 `session_id` 처리만은 연결 전에 합의하거나 바로 수정해야 합니다.

반대로 아래 항목은 지금 비워둬도 됩니다.

- Three.js GLB 실제 렌더링
- 단계별 누적 GLB 구조
- 영상 파일 재생 테스트
- Scene 5 아웃라이어 문구 분기
- 챗봇 API 연결
- Cosmos DB 기반 History 조회
- 무릎 외 부위 확장
