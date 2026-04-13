# taping-knowledge-base

키네시올로지 테이핑 교본 2권을 전처리하여, RAG 시스템 + 3D 모델링 레퍼런스로 활용할 수 있는 데이터셋으로 변환한 결과물.

---

## 소스 교본

| 구분 | 서적 | 저자 | 포맷 | 기법 수 | 비고 |
|------|------|------|------|---------|------|
| book1 | A Practical Guide to Kinesiology Taping, 3rd ed. | John Gibbons | PDF | 60+ | 부위별 체계적 구조, 해부도 포함 |
| book2 | Kinesiology Taping for Rehab and Injury Prevention | Aliana Kim | EPUB | 30+ | 셀프케어 관점, step-by-step 상세 |

두 교본을 교차 참조하여 소스를 다원화했다. 추출된 데이터는 의학적 사실(부위, stretch %, 방향 등)의 파라미터화이며, 원문 문장을 그대로 포함하지 않는다.

---

## 폴더 구조

```
taping-knowledge-base/
│
├── README.md                ← 이 파일
│
├── scripts/                 ← 전처리 코드
│   ├── extract_pdf.py       ← PDF → 텍스트/이미지/매핑 추출
│   ├── extract_epub.py      ← EPUB → 텍스트/이미지/매핑 추출 (sub-chapter 자동 합침 포함)
│   ├── README.md            ← 추출 파이프라인 상세 설명 (영문)
│   └── requirements.txt
│
├── source/                  ← 원본 파일 (⚠️ Git에 올리지 않음)
│   ├── gibbons_3rd_ed.pdf
│   └── kim_rehab_prevention.epub
│
├── rag/                     ← Azure Blob Storage에 올라가는 텍스트
│   ├── book1_gibbons_preface.txt
│   ├── book1_gibbons_glossary.txt
│   ├── book1_gibbons_ch01_overview.txt
│   ├── book1_gibbons_ch02_lower_limbs.txt
│   ├── book1_gibbons_ch03_knee.txt
│   ├── book1_gibbons_ch04_thigh.txt
│   ├── book1_gibbons_ch05_back_trunk_pelvis.txt
│   ├── book1_gibbons_ch06_upper_back_neck_chest.txt
│   ├── book1_gibbons_ch07_upper_limbs.txt
│   ├── book1_gibbons_ch08_forearm_hand_wrist.txt
│   ├── book1_gibbons_ch09_edema.txt
│   ├── book2_kim_intro_what_is_kinesiology_taping.txt
│   ├── book2_kim_basic_terms.txt
│   ├── book2_kim_before_you_begin.txt
│   ├── book2_kim_basic_techniques.txt
│   ├── book2_kim_face_and_neck.txt
│   ├── book2_kim_shoulder_and_chest.txt
│   ├── book2_kim_back_and_trunk.txt
│   ├── book2_kim_arm_and_hand.txt
│   ├── book2_kim_leg_and_hip.txt
│   └── book2_kim_foot.txt
│
├── images/                  ← 3D 모델러 레퍼런스용 이미지
│   ├── book1_gibbons/
│   │   ├── embedded/        ← 테이핑 사진 (190개, PNG, 원본 해상도)
│   │   └── pages/           ← 해부도 래스터화 (28개, JPG, 200dpi)
│   └── book2_kim/           ← EPUB 추출 이미지
│
└── mappings/                ← 이미지-기법 연결 메타데이터
    ├── book1_gibbons_image_mapping.json
    └── book2_kim_image_mapping.json
```

---

## 각 폴더의 역할

### scripts/

교본 원본(PDF/EPUB)에서 텍스트와 이미지를 추출하는 전처리 코드.

- `extract_pdf.py`: PyMuPDF 기반. 이미지 필터링(6,800개 중 190개 콘텐츠 이미지만 추출), 해부도 래스터화, 워터마크 노이즈 제거 포함.
- `extract_epub.py`: BeautifulSoup 기반. EPUB의 sub-chapter 파일을 챕터 단위로 자동 합침. RAG에 불필요한 파일(cover, bibliography 등) 자동 제외.

실행 방법은 `scripts/README.md` 참조.

### source/

교본 원본 파일. 저작권 보호 대상이므로 Git repo에 포함하지 않는다. `.gitignore`에 등록되어 있음. 팀 내부 드라이브에서만 공유.

### rag/

**Azure Blob Storage에 그대로 업로드하는 폴더.** AI Search Vectorizer가 이 텍스트를 청크 단위로 인덱싱하고, LLM이 RAG로 참조한다.

파일 설계 원칙:
- **챕터(부위) 단위로 분리.** "무릎 테이핑"을 질문하면 무릎 챕터 전체가 검색되어야 한다. 페이지 단위나 sub-chapter 단위로 쪼개면 기법의 전체 맥락이 유실된다.
- **파일명에 출처 + 부위가 포함.** LLM이 "Gibbons에 따르면... / Kim에 따르면..."으로 출처를 구분하여 답변할 수 있다.
- **원문 문장이 아닌 교본 내용의 구조화된 추출.** 추후 JSON 스키마 변환의 원본 텍스트 역할.

### images/

3D 모델러(호진)가 테이핑 경로를 3D mesh 위에 재현할 때 참고하는 이미지.

- `embedded/`: 교본에 포함된 테이핑 사진. 원본 해상도 유지. anchor 위치, stretch 방향, 테이프 형태 등을 시각적으로 확인할 수 있다.
- `pages/`: PDF 내 해부도는 수십~수천 개의 소형 벡터 파편으로 저장되어 있어 개별 추출이 불가능하다. 해당 페이지를 200dpi로 래스터화하여 합성된 상태의 해부도를 보존했다.

서비스 UI에 직접 노출하지 않는다 (저작권). 내부 작업 레퍼런스 용도로만 사용.

### mappings/

각 이미지가 어떤 챕터/기법에 속하는지를 기록한 메타데이터 JSON.

이게 없으면 이미지 수백 장을 사람이 하나하나 "이 사진이 IT band 테이핑인지 아킬레스 테이핑인지" 분류해야 한다. 매핑 JSON이 있으면 기법 ID로 해당 레퍼런스 이미지를 즉시 찾을 수 있다.

---

## 전처리 파이프라인 흐름

```
1. 원본 확보
   교본 PDF/EPUB 정식 구매 → source/ 에 저장

2. 텍스트 + 이미지 추출
   python scripts/extract_pdf.py source/gibbons.pdf -o output_pdf/
   python scripts/extract_epub.py source/kim.epub -o output_epub/ --book-prefix book2_kim

3. 파일명 정리 + RAG 폴더에 배치
   PDF 챕터 .txt → book1_gibbons_* 로 rename → rag/
   EPUB 챕터 .txt → 자동으로 book2_kim_* 생성됨 → rag/

4. 이미지 + 매핑 배치
   images/ 와 mappings/ 에 각각 배치

5. Azure 업로드
   rag/ 폴더를 Azure Blob Storage에 업로드
   → AI Search Indexer가 자동 인덱싱
   → LLM (Azure OpenAI)이 RAG로 참조
```

---

## 데이터 규모

| 항목 | book1 (Gibbons) | book2 (Kim) | 합계 |
|------|----------------|-------------|------|
| 챕터 텍스트 | 11개 (156K chars) | 10개 (101K chars) | 21개 |
| 콘텐츠 이미지 | 190개 (28MB) | ~50개 | ~240개 |
| 해부도 래스터 | 28개 (7.7MB) | — | 28개 |
| 이미지 매핑 | 218 entries | ~50 entries | ~268 entries |

---

## 저작권 대응

- 원본 파일(`source/`)은 repo에 포함하지 않음
- 추출된 텍스트(`rag/`)는 교본의 의학적 파라미터(부위, stretch %, 방향, contraindication 등)를 구조화한 것이며, 원문 문장을 그대로 옮기지 않음
- 이미지(`images/`)는 3D 모델링 작업의 내부 레퍼런스로만 사용하며, 서비스 UI에 직접 노출하지 않음
- 발표 시: "영어 교본 2권을 정식 구매하여, 의학적 사실 정보를 자체 스키마로 구조화했습니다. 원문을 그대로 사용하지 않았으며, 복수 출처를 교차 참조했습니다."
