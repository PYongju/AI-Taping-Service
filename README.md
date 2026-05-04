# 🩹 Terry: AI 3D Taping Guide Service

![Terry Banner](https://via.placeholder.com/1000x300.png?text=Terry:+AI+3D+Taping+Guide) <!-- 프로젝트 배너나 로고 이미지가 있다면 링크를 교체하세요 -->

> **"당신의 통증을 이해하고, 정확한 테이핑 방법을 3D로 안내하는 AI 어시스턴트, 테리(Terry)"**

**AI Taping Service**는 사용자의 전신 사진과 통증 증상을 입력받아, 컴퓨터 비전(CV)과 거대 언어 모델(LLM)을 통해 최적의 스포츠(키네시오) 테이핑 솔루션을 제공하는 웹 서비스입니다. 3D 인터랙티브 가이드와 실시간 AI 챗봇을 통해 누구나 쉽게 전문가 수준의 테이핑을 따라 할 수 있습니다.

---

## ✨ 주요 기능 (Key Features)

- 📸 **AI 체형 및 자세 분석 (Computer Vision)**
  - 사용자가 업로드한 전신 사진을 `OpenCV` 및 딥러닝 비전 모델을 통해 분석하여 신체 지표와 관절 위치를 정확히 추적합니다.
- 💬 **자연어 증상 분석 및 솔루션 매칭 (LLM)**
  - 사용자가 입력한 통증 부위와 증상을 `LlamaIndex` 기반의 AI가 구조화하여, 가장 적합한 테이핑 솔루션을 매칭합니다.
- 🤸‍♂️ **3D 인터랙티브 테이핑 가이드**
  - `@react-three/fiber`를 활용하여 3D 인체 모델(`body.glb`) 위에 테이프(`tape.glb`)가 부착되는 과정을 스텝 바이 스텝으로 렌더링합니다. (회전, 확대, 축소 가능)
- 🤖 **실시간 AI 챗봇 '테리'**
  - 테이핑을 하는 도중 궁금한 점이 생기면 각 단계(Step)에 맞춰 컨텍스트를 이해하는 챗봇 '테리'에게 실시간으로 질문하고 답변을 받을 수 있습니다.

---

## 🛠 기술 스택 (Tech Stack)

### Frontend
- **Framework:** React 18, Vite
- **3D Rendering:** Three.js, React Three Fiber, React Three Drei
- **Styling & UI:** CSS3
- **Deployment:** Azure Static Web Apps

### Backend
- **Framework:** FastAPI, Python 3.11
- **AI / ML:** OpenCV (Headless), LlamaIndex, LLM API
- **Server:** Gunicorn, Uvicorn
- **Deployment:** Azure App Service on Linux (B3 Tier)

### Database & Cloud Storage
- **Database:** Azure Cosmos DB
- **Storage:** Azure Blob Storage (3D 모델 `.glb` 및 에셋 호스팅)

---

## 🏗 아키텍처 및 시스템 흐름 (Architecture)

1. **사용자 입력:** 프론트엔드에서 사용자의 전신 사진과 통증 텍스트를 입력받습니다.
2. **백엔드 처리 (AI Pipeline):**
   - FastAPI 서버로 데이터를 전송합니다.
   - `feat_cv` 모듈이 사진을 분석하여 신체 랜드마크를 추출합니다.
   - `feat_llm` 모듈이 텍스트를 구조화하고 DB에서 적절한 테이핑 가이드를 매칭합니다.
3. **데이터 저장:** 분석된 세션 결과는 Azure Cosmos DB에 저장됩니다.
4. **3D 시각화:** 프론트엔드는 Azure Blob Storage에서 해당 부위의 3D 모델을 불러와 렌더링하고, 사용자는 가이드를 따라 테이핑을 진행합니다.
   - `feat_llm` 모듈이 텍스트를 구조화하고 DB에서 적절한 테이핑 가이드를 매칭합니다.
3. **데이터 저장:** 분석된 세션 결과는 Azure Cosmos DB에 저장됩니다.
4. **3D 시각화:** 프론트엔드는 Azure Blob Storage에서 해당 부위의 3D 모델을 불러와 렌더링하고, 사용자는 가이드를 따라 테이핑을 진행합니다.
