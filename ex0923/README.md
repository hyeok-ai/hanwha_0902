# RAG · 임베딩 · 검색 기술 정리

## 목차

1. [개발 환경: uv + VS Code + Jupyter](#1-개발-환경-uv--vs-code--jupyter)
2. [RAG 파이프라인 개요](#2-rag-파이프라인-개요)
3. [임베딩 기초](#3-임베딩-기초)
4. [멀티모달 임베딩: OpenCLIP](#4-멀티모달-임베딩-openclip)
5. [검색(Retrieval) 기법](#5-검색retrieval-기법)
6. [실습 분석 사례](#6-실습-분석-사례)
7. [최근 RAG 개발 동향](#7-최근-rag-개발-동향)
8. [임베딩 역전(Embedding Inversion)](#8-임베딩-역전embedding-inversion)
9. [참고 자료](#9-참고-자료)

---

## 1. 개발 환경: uv + VS Code + Jupyter

uv는 가상환경을 없애는 도구가 아니라, 프로젝트 안의 `.venv`를 uv가 만들고 관리해 주는 도구다. 따라서 VS Code에서 커널을 선택하는 방식은 기존 venv와 거의 같다.

### 1.1 추천 시작 루틴

```bash
mkdir python-practice          # 폴더 생성
cd python-practice             # 폴더로 이동
uv init --bare                 # 최소 구성의 uv 프로젝트로 초기화 (pyproject.toml만 생성)
uv add --dev ipykernel         # Jupyter 커널용 패키지를 개발 의존성으로 추가
uv add numpy pandas matplotlib scikit-learn   # 일반 의존성 추가
code .                         # 현재 폴더를 VS Code로 열기
```

이후 VS Code에서 `.ipynb`를 열고 **Select Kernel → Python Environments → `.venv`의 Python**을 선택한다.

| OS | 커널 경로 |
|---|---|
| macOS / Linux | `.venv/bin/python` |
| Windows | `.venv\Scripts\python.exe` |

### 1.2 명령어 구조 읽는 법

```
uv add --dev ipykernel
│   │    │     └─ 인자(argument): 대상 패키지
│   │    └─────── 옵션(option/flag)
│   └──────────── 서브커맨드(subcommand)
└──────────────── 프로그램(command)
```

uv CLI의 기본 문법은 `uv [OPTIONS] <COMMAND>`이다. `scikit-learn`의 `-`는 옵션 표시가 아니라 패키지 이름의 일부이며, 옵션은 `--dev`, `--group`처럼 하이픈으로 시작한다.

### 1.3 주요 명령어

| 명령 | 의미 |
|---|---|
| `uv init` | 새 프로젝트 생성. `uv init my-project`처럼 이름을 주면 하위 폴더를 만들고, 이름이 없으면 현재 폴더가 프로젝트가 됨 |
| `uv init --bare` | `pyproject.toml`만 생성. README, Python 버전 pin 파일, 소스 디렉터리, Git 초기화 등을 생략. 기존 실습 폴더에 적합 |
| `uv add <pkg>` | `pyproject.toml`에 의존성 기록 → 의존성 해결 → `uv.lock` 갱신 → `.venv` 동기화. 여러 패키지를 한 번에 받을 수 있음 |
| `uv add --dev <pkg>` | `--group dev`의 별칭. `[dependency-groups]`의 `dev` 그룹에 기록. dev 그룹은 기본적으로 `uv sync`, `uv run`에 포함됨 |
| `uv sync` | `pyproject.toml` / `uv.lock`에 맞게 `.venv`를 동기화. `.venv`가 없으면 생성. 기본값은 exact sync라 선언되지 않은 패키지는 제거 |
| `uv pip install <pkg>` | pip 호환 인터페이스. 현재 환경에만 설치하고 프로젝트 의존성으로 기록하지 않음 |
| `mkdir` / `cd` | 셸 명령. make directory / change directory |
| `code .` | VS Code CLI. `.`은 현재 디렉터리. macOS에서는 Command Palette의 *Shell Command: Install 'code' command in PATH*로 먼저 등록해야 할 수 있음 |

> **주의:** `uv init --bare` 직후에는 `.venv`가 없다. `uv add`나 `uv sync`처럼 환경 동기화가 필요한 명령을 실행할 때 `.venv`가 생성된다.

`ipykernel`만 `--dev`로 넣는 이유: 이 패키지는 `.venv`의 Python을 Jupyter 커널로 구동하는 연결 역할일 뿐, 작성하는 프로그램의 기능 자체에는 필요 없기 때문이다.

### 1.4 `uv add` vs `uv pip install`

| 항목 | `uv add pandas` | `uv pip install pandas` |
|---|---|---|
| 관점 | 프로젝트 관리 | 환경 조작 |
| `pyproject.toml` 기록 | ✅ | ❌ |
| `uv.lock` 기록 | ✅ | ❌ |
| `.venv` 설치 | ✅ | ✅ |

노트북 안에서 `%pip install`을 쓰기보다 터미널에서 `uv add`를 쓰는 편이 좋다. "이 노트북을 실행하려면 무엇이 필요한가"가 파일로 남기 때문이다.

### 1.5 세 파일의 관계

```
pyproject.toml   "numpy, pandas가 필요하다"          (의도/요구사항)
      │
      ▼
uv.lock          "실제로는 이 정확한 버전 조합을 쓴다"  (간접 의존성까지 잠금)
      │
      ▼
.venv            실제 설치 위치 → Python / Jupyter 실행
```

Git에는 `pyproject.toml`과 `uv.lock`만 올리고 `.venv/`는 제외한다. 다른 PC에서는 `uv sync`로 환경을 복원한다.

### 1.6 기존 방식과 비교

| 기존 (venv + pip) | uv |
|---|---|
| `python -m venv .venv` | uv가 `.venv` 관리 |
| `pip install pandas` | `uv add pandas` |
| `pip install ipykernel` | `uv add --dev ipykernel` |
| `requirements.txt` 직접 관리 | `pyproject.toml` + `uv.lock` |
| `pip freeze` | 보통 불필요 |
| 다른 PC에서 수동 재설치 | `uv sync` |

---

## 2. RAG 파이프라인 개요

RAG(Retrieval-Augmented Generation, 검색 증강 생성)는 문서를 검색해 LLM 프롬프트에 넣어 답변을 생성하는 방식이다. 조립 단계는 다음과 같다.

```
데이터 → 로더 선택 → 청킹(분할) → 임베딩 → 벡터 DB 저장 → 리트리버 → LLM 생성
```

RAG는 두 시점으로 나뉜다.

| 시점 | 하는 일 |
|---|---|
| **인덱싱 (사전 준비)** | 문서를 청크로 자르고, 각 청크를 임베딩 모델로 벡터화해 벡터 DB에 저장. 책에서 말하는 "임베딩 단계"는 주로 이것 |
| **검색 (실시간)** | 사용자 질문을 벡터로 바꿔 문서 벡터와 거리를 비교. 리트리버가 담당 |

임베딩의 결과물이 곧 벡터다. 질문과 문서는 **반드시 같은 임베딩 모델**로 벡터화해야 한다. 모델이 다르면 두 벡터가 서로 다른 좌표계에 놓여 비교가 무의미해진다. 다만 일부 모델은 질문과 문서를 약간 다르게 처리한다.

- **E5 등**: 질문에는 `query:`, 문서에는 `passage:` 접두어를 붙이도록 권장
- **DPR**: 질문용 인코더와 문서용 인코더를 따로 둠

---

## 3. 임베딩 기초

### 3.1 임베딩이 담는 것

임베딩 모델은 문장의 형식보다 **의미**를 벡터로 표현하도록 학습된다. 따라서 "Word2Vec에 대하여 알려줘"와 "Word2Vec은 단어를 벡터로 표현하는 기법이다"는 핵심 주제가 같아 가깝게 나온다. 다만 짧은 질문과 긴 설명문은 성격이 달라(**비대칭 검색**) 약간 손해를 본다.

반면 "W로 시작하고 숫자가 들어간 거"처럼 **철자에 대한 단서**는 임베딩이 거의 활용하지 못한다. 임베딩은 철자보다 의미를 담기 때문이다.

### 3.2 Sparse 임베딩 vs Dense 임베딩

| 구분 | Sparse | Dense |
|---|---|---|
| 예시 | BM25, SPLADE, uniCOIL | OpenAI 임베딩, CLIP 등 |
| 차원 | 어휘 크기 (수만~수십만) | 수백~수천 |
| 값 분포 | 실제 등장한 소수 용어만 0이 아님 | 거의 모든 값이 채워짐 |
| 해석 가능성 | "이 용어가 얼마만큼 기여했다"로 분해 가능, 디버깅 쉬움 | 코사인 유사도가 블랙박스 |
| 강점 | 고유명사, 코드 등 정확한 키워드 | 의미적 유사성 |

- **SPLADE**는 출력 차원이 BERT 어휘 크기(약 30,000)이지만, 쿼리/문서 하나당 수백 개 차원만 활성화된다.
- **BM25**는 표현이 다르면 매칭하지 못한다. **SPLADE**는 확장(expansion) 기능이 있어 "feline"이 나오면 "cat", "kitten", "pet"에도 가중치를 준다.
- 이미지에는 "단어"가 없으므로 이미지와 텍스트를 같은 공간에 두는 CLIP 같은 모델은 dense 방식을 쓴다.

---

## 4. 멀티모달 임베딩: OpenCLIP

### 4.1 코드

```python
from langchain_experimental.open_clip import OpenCLIPEmbeddings

image_embedding_function = OpenCLIPEmbeddings(
    model_name="ViT-B-32", checkpoint="laion2b_s34b_b79k"
)
```

- 필요 패키지: `langchain-experimental`, `pillow`, `open_clip_torch`, `torch`
- 인자 생략 시 기본값: `model_name="ViT-H-14"`, `checkpoint="laion2b_s32b_b79k"`
- 내부 동작: `open_clip.create_model_and_transforms`로 모델과 전처리 함수를, `open_clip.get_tokenizer`로 토크나이저를 로드
- 텍스트 임베딩은 `encode_text` 후 **L2 norm으로 정규화**해 리스트로 변환. 정규화된 벡터끼리는 내적 = 코사인 유사도
- 텍스트: `embed_documents`, 이미지: `embed_image(이미지 URI 리스트)`
- Chroma 연동: `langchain_chroma.Chroma`의 `add_images(uris, metadatas, ids)`로 이미지를 벡터스토어에 추가

### 4.2 모델 이름·체크포인트 읽는 법

| 토큰 | 의미 |
|---|---|
| `ViT` | Vision Transformer (이미지 쪽 아키텍처) |
| `B` | 크기. B(base) < L(large) < H(huge) < g(gigantic) |
| `32` | 비전 인코더의 패치 크기 (14, 16, 32가 흔함) |
| `laion2b` | LAION-2B, 20억 개 이미지-텍스트 쌍 데이터셋 |
| `s34b` | 학습 중 본 샘플 수 약 340억 |
| `b79k` | 글로벌 배치 크기 약 7만 9천 |

패치가 큰 작은 모델은 추론이 빨라서, 빠른 추론이 필요할 때 유리하다.

### 4.3 ViT-B/32 구조

| 항목 | 값 | 의미 |
|---|---|---|
| `image_size` | 224 | 입력 이미지 해상도(px) |
| `patch_size` | 32 | 패치 한 변 크기. 224÷32 = 7 → 7×7 = 49개 패치 |
| `projection_dim` | 512 | 최종 임베딩 차원 (이미지·텍스트 공통) |
| `max_position_embeddings` | 77 | 텍스트 최대 토큰 수 |

### 4.4 성능과 유의점 (laion2B-s34B-b79K 모델 카드)

- LAION-5B의 영어 부분집합인 LAION-2B로 OpenCLIP을 사용해 학습
- ImageNet-1k 제로샷 top-1 정확도 **66.6%**, 파라미터 **151M**
- **영어 전용**: 영어 외 언어로는 학습·평가하지 않음
- 제한된 환경의 이미지 검색이라도 도메인 내 철저한 테스트 없이 배포하는 것은 권장하지 않음
- 다국어가 필요하면 `xlm-roberta-base-ViT-B-32` / `laion5b_s13b_b90k` 같은 다국어 텍스트 인코더 체크포인트 사용. 영어 전용보다 다국어 검색에 훨씬 낫지만, 전용 다국어 CLIP 모델이 더 좋음
- **텍스트 길이 제한**: 77토큰 절대 위치 임베딩. Long-CLIP 논문에 따르면 실제 유효 길이는 20토큰 미만 → 긴 문서보다 짧은 캡션·검색어에 적합

### 4.5 이미지와 텍스트가 같은 좌표계에 놓이는 원리

이미지는 이미지 인코더(ViT), 텍스트는 텍스트 인코더(Transformer)를 거치지만 둘 다 같은 512차원 벡터를 출력한다. **대조 학습(contrastive learning)**으로 짝이 맞는 쌍은 가깝게, 짝이 아닌 쌍은 멀게 학습한다. 벡터의 개별 숫자에는 해석 가능한 의미가 없고, 의미는 점들 사이의 거리와 방향에 담긴다.

**Modality gap** (Liang et al., NeurIPS 2022)
- 이미지 임베딩과 텍스트 임베딩이 공유 공간 안에서 분리된 두 영역에 위치
- 텍스트, 자연 이미지, 비디오, 의료 영상, 아미노산 서열 등 다양한 멀티모달 모델에서 일관되게 나타남
- 원인: 모델 초기화 + 대조 학습 최적화의 조합

**코사인 유사도 범위** (CLIPScore, EMNLP 2021)
- OpenAI CLIP ViT-B/32 기준 이론상 −1~1이지만 음수는 관찰되지 않았고, 대체로 **0~약 0.4**
- 단조 재스케일링은 순위에 영향을 주지 않으므로 검색의 상대 순위는 유효
- 이 범위는 ViT-B/32 한정. LAION 체크포인트로 임계값을 정할 때는 직접 측정할 것

### 4.6 CLIP의 한계

- **Bag-of-words 성향** (Yuksekgonul et al., ICLR 2023): 5만 개 이상 테스트로 구성된 ARO 벤치마크에서 관계 이해 부족, 객체-속성 잘못된 연결, 심각한 어순 둔감성을 보임. 가설: 기존 데이터셋은 어순 없이도 검색 성능이 잘 나와 대조 학습이 이를 배울 필요가 없었음
- **타이포그래피 공격** (OpenAI, Multimodal Neurons, 2021): 이미지 속 글자에 강하게 반응. "iPod" 쪽지를 붙인 사과 → iPod, "pizza" 글자가 있는 개 사진 → 피자. 단, ResNet 기반 RN50x4로 수행된 연구이며 ViT-B/32에서 직접 검증한 결과는 아님

---

## 5. 검색(Retrieval) 기법

질문을 그대로 임베딩해 가장 가까운 문서를 찾는 방식은 가장 기본형이며, 다음 기법들로 보완한다.

### 5.1 MMR (Maximal Marginal Relevance)

질문과의 **관련성**과 결과 간 **다양성**을 함께 고려하는 알고리즘 (Carbonell & Goldstein, 1998). 청크 중에는 거의 같은 내용이 많아, 일반 유사도 검색의 상위 k개가 같은 이야기만 반복할 수 있다. MMR은 "관련은 있지만 이미 고른 것과는 다른" 문서를 우선 선택한다.

$$
\text{MMR} = \arg\max_{d_i \in R \setminus S} \Big[ \lambda \cdot \text{Sim}(d_i, q) - (1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j) \Big]
$$

| 기호 | 의미 |
|---|---|
| $q$ | 사용자 질문 |
| $R$ | 후보 문서 집합 |
| $S$ | 지금까지 선택된 문서 집합 |
| $\text{Sim}(d_i, q)$ | 질문과의 관련성 |
| $\max \text{Sim}(d_i, d_j)$ | 이미 고른 문서와의 중복도 (클수록 감점) |
| $\lambda$ (0~1) | 1에 가까우면 관련성 위주(일반 유사도 검색과 동일), 0에 가까우면 다양성 위주 |

**동작 과정**
1. 벡터 검색으로 후보를 넉넉히 가져온다 (예: 20개)
2. 질문과 가장 유사한 문서 하나를 먼저 선택한다
3. 남은 후보마다 MMR 점수를 계산해 최고점 문서를 추가한다
4. k개가 될 때까지 3을 반복한다

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,             # 최종 반환 문서 수
        "fetch_k": 20,      # MMR을 적용할 후보 수
        "lambda_mult": 0.5  # λ (1: 관련성 중시, 0: 다양성 중시)
    }
)
```

### 5.2 쿼리 변환

| 기법 | 설명 |
|---|---|
| Query Rewriting | LLM이 사용자 질문을 검색하기 좋은 형태로 다시 씀 |
| MultiQueryRetriever | 여러 버전의 질문을 만들어 각각 검색한 뒤 합침 |
| HyDE | LLM이 가상의 답변 문서를 먼저 쓰고, 그것으로 검색. 질문과 문서의 형태 차이를 없앰 |

### 5.3 하이브리드 검색 (EnsembleRetriever)

BM25(키워드)는 고유명사를 정확히 잡는 데 강하고, 벡터 검색은 의미가 비슷한 것을 잡는 데 강하다. 둘을 결합하면 서로의 약점을 메운다.

`EnsembleRetriever`는 **RRF(Reciprocal Rank Fusion)**로 결과를 재정렬한다.

$$
\text{score}(doc) = \sum_i w_i \times \frac{1}{\text{rank}_i + c} \quad (c = 60,\ \text{rank는 1부터})
$$

**동작 과정**
1. 각 리트리버를 따로 실행한다
2. 결과를 **합집합**으로 모은다 (중복 문서는 하나로)
3. 문서별로 리트리버마다 RRF 점수를 계산해 더한다
4. 합산 점수 순으로 정렬해 전부 반환한다

- 원래 점수(BM25 점수, 코사인 유사도)가 아닌 **순위만** 사용하므로 스케일이 다른 점수를 직접 비교할 필요가 없다
- 한 리트리버만 찾은 문서도 **버려지지 않고** 순위만 뒤로 밀린다
- 두 리트리버 모두 상위로 꼽은 문서가 점수를 합산받아 유리하다 → "키워드로도, 의미로도 맞는 문서가 가장 신뢰할 만하다"

k=3 예시:

| 문서 | BM25 순위 | FAISS 순위 | 합산 점수 |
|---|---|---|---|
| X | 1위 | - | 0.7/61 ≈ 0.0115 |
| **Y** | 2위 | 1위 | 0.7/62 + 0.3/61 ≈ **0.0162** |
| Z | - | 2위 | 0.3/62 ≈ 0.0048 |

BM25 단독 1위는 X지만, 양쪽에서 상위권인 Y가 최종 1위가 된다.

### 5.4 재정렬 (Reranking)

일단 넉넉하게(예: 20개) 뽑은 뒤, 질문과 문서를 함께 보고 관련도를 정밀하게 판단하는 모델(Cross-Encoder 등)로 순서를 다시 매겨 상위 몇 개만 쓴다. `ContextualCompressionRetriever`와 함께 자주 쓰인다.

### 5.5 확인 방법

`similarity_search_with_score`로 여러 질문을 넣어 어떤 문서가 몇 점으로 나오는지 비교하면, 기본 리트리버의 한계를 직접 확인할 수 있다.

---

## 6. 실습 분석 사례

### 6.1 BM25 + FAISS 앙상블 (apple 예제)

```python
bm25_retriever = BM25Retriever.from_texts(doc_list)
bm25_retriever.k = 1

faiss_vectorstore = FAISS.from_texts(doc_list, embedding)
faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 1})

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever], weights=[0.7, 0.3]
)
```

질문: `"my favorite fruit is apple"`

**BM25 결과: "Apple is my favorite company"**

BM25는 TF(단어 빈도)와 IDF(희소성)로 점수를 매긴다. 기본 전처리는 `text.split()`(공백 분리)뿐이라 소문자 변환, 어간 추출, 구두점 처리가 없다.

| 문서 | 질문과 일치하는 토큰 |
|---|---|
| I like apples | 없음 (`apples` ≠ `apple`) |
| I like apple company | `apple` (1개) |
| I like apple's iphone | 없음 (`apple's` ≠ `apple`) |
| Apple is my favorite company | `is`, `my`, `favorite` (3개) |
| I like apple's ipad / macbook | 없음 |

- `Apple`은 대문자라 `apple`과 일치하지 않음
- 일치 단어들은 모두 6개 문서 중 1개에만 등장해 IDF가 같음 (BM25Okapi 기준 log((6−1+0.5)/(1+0.5)) ≈ 1.30) → 3개를 맞춘 문서가 승리
- `is`, `my` 같은 의미 없는 단어가 점수를 좌우 → 키워드 검색의 전형적 한계

**FAISS 결과: "I like apples"**

질문의 `fruit`과 `apple`이 함께 쓰여 "과일로서의 사과" 의미가 벡터에 반영된다. BM25에서 일치 토큰 0개였던 문서가 FAISS에서는 1위다.

**Ensemble 결과 순서**

| 문서 | BM25 기여 | FAISS 기여 | 최종 |
|---|---|---|---|
| Apple is my favorite company | 0.7 × 1/61 ≈ 0.01148 | - | 0.01148 |
| I like apples | - | 0.3 × 1/61 ≈ 0.00492 | 0.00492 |

각 리트리버가 k=1로 서로 다른 문서를 냈기 때문에 합산이 일어나지 않았고, 가중치는 정렬 순서만 결정했다.

**개선 방향**

```python
bm25_retriever = BM25Retriever.from_texts(
    doc_list,
    preprocess_func=lambda text: text.lower().replace("'s", "").split(),
)
```

- **전처리 개선**: 소문자 변환 등. 한국어는 Kiwi 같은 형태소 분석기 필수 (예: `langchain_teddynote`)
- **k 늘리기**: 여러 문서를 반환해야 RRF 합산 효과가 나타남
- **가중치 조정**: 의미 중심 질문이 많으면 FAISS 비중↑, 제품명·코드·고유명사가 중요하면 BM25 비중↑
- **불용어 제거**: `is`, `my` 등이 점수를 좌우하지 않도록. 문서 수가 너무 적어 IDF가 제 역할을 못한 것도 원인

### 6.2 메타데이터 필터 + 표기 변형 쿼리 (ESG 예제)

네 쿼리 모두 `finance-keywords.txt`만 반환 → 메타데이터 필터는 정상. k=1 설정대로 문서 1개씩 반환.

| 쿼리 | 반환 청크 | ESG 정의 포함 |
|---|---|---|
| `eSg` | 45f5bd06… | ✅ (청크 맨 앞) |
| `e/S/g` | 85ffb71b… | ❌ 제목만 (청크 맨 끝) |
| `E~S~G` | 85ffb71b… | ❌ 제목만 |
| `Environmental-Social-Governance` | 85ffb71b… | ❌ 제목만 |

**원인 1: 청크 경계에서 제목과 본문 분리**
원본이 "제목 → 빈 줄 → 정의/예시/연관키워드" 구조인데, 분할기가 `\n\n` 기준으로 자르면서 청크 크기 한계에 걸려 제목(85ffb71b 끝)과 정의(45f5bd06 앞)가 끊겼다.

**원인 2: 쿼리 표기에 따른 임베딩 차이**
- `eSg`는 대소문자만 달라 "ESG"와 거의 같게 처리 → "ESG"가 여러 번 등장하는 45f5bd06에 매칭
- `e/S/g`, `E~S~G`는 구분자 때문에 개별 글자로 쪼개질 가능성이 큼 → 약어 신호가 약해지고, 영문 풀네임·Governance 관련 단어가 모인 85ffb71b가 선택됨
- 임베딩 검색은 대소문자 변화에는 비교적 강하지만 구두점으로 쪼갠 표기에는 흔들린다

**개선 방법**
1. **청크 분할 수정 (가장 효과적)**: 항목 단위(제목+정의+예시+연관키워드)로 분할하거나 `chunk_overlap`을 충분히 줌
2. **k 늘리기**: k=2~3으로 두 청크를 함께 반환. 중복 줄이려면 `search_type="mmr"`
3. **쿼리 정규화/재작성**: 구분자 제거·대문자화 전처리 또는 `MultiQueryRetriever`
4. **하이브리드 검색**: BM25 + FAISS. 단, BM25도 정규화 없이는 `e/S/g`를 못 잡으므로 3번과 병행

> **참고:** FAISS의 `filter`는 먼저 `fetch_k`(기본 20)개를 가져온 뒤 필터링한다. 문서가 많아지면 필터 조건에 맞는 문서가 상위 20개에 들지 못해 결과가 빌 수 있으므로 `search_kwargs`에 `fetch_k`를 크게 지정한다.

---

## 7. 최근 RAG 개발 동향

| 영역 | 전통적 RAG | 최근 트렌드 |
|---|---|---|
| 전체 구조 | "검색 → 생성" 고정 파이프라인(체인) | LLM이 검색을 도구로 호출하는 에이전트 |
| 인프라 | 벡터 DB, 청킹, 임베딩 직접 구성 | 파일 업로드만 하면 되는 관리형 RAG |
| 검색 방식 | 벡터 검색 단독 | 하이브리드(벡터+BM25) + 리랭커가 사실상 기본 |
| 문서 처리 | 단순 텍스트 추출 | 레이아웃·표 구조 인식 파서 |
| 대안 | RAG가 거의 유일 | 긴 컨텍스트에 통째로 넣기, 에이전트 키워드 검색 등 |

### 7.1 체인에서 에이전트로
- **에이전틱 RAG**: 모델이 검색 필요 여부와 재검색 여부를 스스로 판단. 반성(reflection), 계획, 도구 사용, 멀티 에이전트 협업 패턴 활용
- **LangChain 1.0**: 핵심 추상화로 범위를 줄이고 레거시는 `langchain-classic`으로 이동. `create_agent`가 표준 에이전트 생성 방식이며 LangGraph 위에 구축(체크포인팅, 스트리밍, 사람 승인 단계 기본 제공). `MultiQueryRetriever` 등 기존 리트리버도 `langchain-classic`으로 이동 → **import 경로 확인 필요**

### 7.2 관리형 RAG
- **Google Gemini File Search**: Gemini API 내장 완전 관리형 RAG. 저장·쿼리 시 임베딩 무료, 최초 인덱싱만 100만 토큰당 $0.15. 2026년 5월 멀티모달, 커스텀 메타데이터, 페이지 단위 인용 추가
- **OpenAI File Search**: Responses API의 호스팅 도구. 의미+키워드 검색, RRF에서 임베딩/키워드 가중치 조절 옵션
- **Amazon Bedrock Knowledge Bases**: 수집부터 검색, 프롬프트 증강까지 완전 관리형

관리형 서비스도 내부적으로 하이브리드 검색, 메타데이터 필터 등을 쓰므로 원리 이해는 튜닝에 여전히 중요하다.

### 7.3 하이브리드 검색과 리랭킹
Anthropic Contextual Retrieval: 청크에 문맥을 덧붙인 임베딩 + BM25로 검색 실패율 49% 감소, 리랭킹 추가 시 67% 감소 (상위 20개 기준 5.7% → 1.9%). 리랭킹은 지연 시간과 비용이 늘므로 균형점을 실험으로 찾을 것.

### 7.4 문서 파싱
**Docling** (IBM): 객체 탐지 기반 비전 모델로 레이아웃을 분석해 텍스트, 이미지, 표, 캡션을 구분하고, TableFormer로 이미지 형태의 표를 행·열 구조로 변환. 평면적 텍스트 추출은 위치·출처 정보를 잃어 표 중간에서 청크가 잘리고 근거 추적이 불가능해진다.

### 7.5 RAG를 쓰지 않는 선택지
- Anthropic: 지식 베이스가 20만 토큰(약 500페이지) 미만이면 전체를 프롬프트에 넣고, 프롬프트 캐싱으로 비용·속도 부담을 낮추는 방법 제안
- AWS 연구진 2026년 논문 (*Keyword search is all you need*): 벡터 DB 없이 에이전트가 키워드 검색 도구(RipGrep-All, PDF 검색 도구)만으로 기존 RAG 성능 지표의 90% 이상 달성. 특정 데이터셋 기준 결과이므로 대규모·의미 중심 검색에는 여전히 벡터 검색이 유리할 수 있음

**정리:** "모든 단계 직접 구현"과 "관리형 서비스"의 스펙트럼 위에서 선택한다. 관리형으로 시작해 평가로 부족한 지점(파싱, 검색, 리랭킹)을 찾아 그 부분만 교체하는 방식이 일반적이다.

---

## 8. 임베딩 역전(Embedding Inversion)

**요약:** 임베딩에서 원본을 완벽히 되살리는 것은 보장되지 않지만 실제로는 상당 부분 복원된다. 임베딩은 익명화나 암호화가 아니며, **벡터 DB는 원문 수준으로 보호해야 한다.**

### 8.1 텍스트 임베딩 → 원문 복원

**Vec2Text** (EMNLP 2023, Outstanding Paper)
- 방법: 텍스트를 추측해 다시 임베딩하고, 목표 벡터와의 차이를 보고 고치는 과정 반복. 임베딩 모델에 대한 질의 접근 필요
- 결과: 32토큰 입력의 **92%를 글자 그대로 복원**, 블랙박스 인코더 대상 BLEU 최대 97.3. 임상 기록(MIMIC)에서 환자 전체 이름도 복원
- 한계: 32토큰까지는 대부분 정확, 128토큰까지는 일부 정보만. 그 이상은 조사하지 않음
- 임베딩만 보고 한 번에 생성하는 단순 방식은 성능이 나빴고, 반복 수정 방식이 효과적

**TEIA** (Transferable Embedding Inversion Attack, ACL 2024)
- 원래 임베딩 모델에 접근하지 않고, 이를 흉내 내는 **대리 모델**을 학습시켜 공격
- 전제: 공격자가 임베딩과 대응 원문 일부가 유출된 데이터셋을 확보

### 8.2 CLIP 이미지 임베딩 → 이미지 (DALL·E 2 / unCLIP)
- CLIP 이미지 인코더를 역전하도록 디퓨전 디코더를 학습
- 역변환이 비결정적이라 한 임베딩에서 여러 이미지가 나옴
- **픽셀 복원이 아닌 의미 수준 복원**: 의미와 스타일은 유지되고, 임베딩에 담기지 않은 세부 사항은 달라짐
- Hugging Face Diffusers의 unCLIP 구현은 카카오브레인 Karlo에서 가져옴

### 8.3 CLIP ViT-B/32 임베딩 → 캡션 (ClipCap)
- CLIP 임베딩을 작은 매핑 네트워크로 변환해 GPT-2의 프리픽스로 넣고 캡션 생성
- CLIP과 GPT-2를 모두 고정하고 매핑 네트워크만 학습해도 잘 동작
- 공식 코드는 COCO 학습 시 CLIP 특징을 ViT-B/32로 추출

### 8.4 얼굴 인식 임베딩 → 얼굴 (템플릿 역전)

| 연구 | 학회 | 내용 |
|---|---|---|
| Face Adapter | CVPR 2025 | 4,200만 장으로 학습한 얼굴 파운데이션 모델로 블랙박스 모델의 임베딩에서 얼굴 재구성. 기존 공격보다 우수 |
| GaFaR | ICCV 2023 | 얼굴 템플릿에서 3D 얼굴 재구성 |

### 8.5 공격인가 기능인가

같은 "벡터에서 원본 되살리기"가 맥락에 따라 다르게 다뤄진다.

| 맥락 | 연구 | 다루는 방식 |
|---|---|---|
| 보안·프라이버시 | Vec2Text | 벡터 DB에 임베딩만 저장하거나 외부로 보내는 관행의 위험 검증 |
| 보안·프라이버시 | Face Adapter | 얼굴 인식 시스템 침입용 재구성 공격 |
| 이미지 생성 | unCLIP / DALL·E 2 | 이미지 생성·변형 기능 |
| 이미지 캡션 | ClipCap | 캡션 생성 |

보안 연구가 공격 시나리오를 쓰는 이유는 "임베딩만 넘기면 안전하다"는 가정을 검증하기 위해서다.

### 8.6 복원용 모델 vs 짝 맞추기 모델

| 모델 | 학습 목표 | 디코더 |
|---|---|---|
| 오토인코더 (Hinton & Salakhutdinov, 2006) | 작은 중앙층을 거쳐 입력 재구성 | 있음 |
| CLIP (Radford et al., 2021) | 4억 개 (이미지, 텍스트) 쌍으로 배치 안의 올바른 짝 예측 | 없음 |

복원을 목표로 학습하지 않은 임베딩에도 원문 정보가 많이 남는다 (단, Vec2Text 실험은 CLIP이 아닌 텍스트 임베딩 모델 대상).

### 8.7 프로빙(Probing)
"벡터에 무엇이 담겨 있나"를 분석 관점에서 측정하는 연구 분야. Conneau et al.(ACL 2018)은 단순한 언어적 특징을 잡는 10가지 프로빙 과제로 3종 인코더를 8가지 방식으로 학습한 임베딩을 분석했다.

---

## 9. 참고 자료

**개발 환경**
- Astral uv 공식 문서
- VS Code 공식 문서 (`code` CLI)

**임베딩 · CLIP**
- LangChain OpenCLIP 통합 문서: docs.langchain.com/oss/python/integrations/text_embedding/open_clip
- `langchain_experimental.open_clip` 소스 코드 및 API 문서
- `langchain_chroma` Chroma API 문서
- Hugging Face 모델 카드: huggingface.co/laion/CLIP-ViT-B-32-laion2B-s34B-b79K
- Hugging Face `openai/clip-vit-base-patch32` 설정
- Marqo, *Model Selection for Multimodal Search*
- Liang et al., *Mind the Gap*, NeurIPS 2022
- Hessel et al., *CLIPScore*, EMNLP 2021
- Zhang et al., *Long-CLIP*, ECCV 2024
- Yuksekgonul et al., *When and why vision-language models behave like bags-of-words*, ICLR 2023
- OpenAI, *Multimodal Neurons in Artificial Neural Networks*, 2021
- Radford et al., *Learning Transferable Visual Models From Natural Language Supervision*, 2021

**검색**
- Carbonell & Goldstein, MMR, 1998
- LangChain EnsembleRetriever 문서
- SPLADE 및 sparse retrieval 개념: zeroentropy.dev

**RAG 동향**
- LangChain 1.0: https://www.langchain.com/blog/langchain-langgraph-1dot0
- LangChain v1 변경 사항: https://docs.langchain.com/oss/python/releases/langchain-v1
- Agentic RAG 서베이: https://arxiv.org/abs/2501.09136
- Gemini File Search: https://blog.google/technology/developers/file-search-gemini-api/
- OpenAI File Search: https://developers.openai.com/api/docs/guides/tools-file-search
- Amazon Bedrock Knowledge Bases: https://aws.amazon.com/bedrock/knowledge-bases
- Anthropic Contextual Retrieval: https://www.anthropic.com/engineering/contextual-retrieval
- Docling: https://research.ibm.com/blog/docling-generative-AI
- Keyword search is all you need: https://arxiv.org/abs/2602.23368

**임베딩 역전**
- Morris et al., *Text Embeddings Reveal (Almost) As Much As Text*, EMNLP 2023 (arXiv 2310.06816)
- Huang et al., *Transferable Embedding Inversion Attack*, ACL 2024
- Ramesh et al., *Hierarchical Text-Conditional Image Generation with CLIP Latents*, 2022 (arXiv 2204.06125)
- Mokady et al., *ClipCap*, 2021 (arXiv 2111.09734)
- Otroshi Shahreza et al., *Face Reconstruction from Face Embeddings using Adapter to a Face Foundation Model*, CVPR 2025
- Otroshi Shahreza & Marcel, *Template Inversion Attack … using 3D Face Reconstruction*, ICCV 2023
- Hinton & Salakhutdinov, *Reducing the Dimensionality of Data with Neural Networks*, Science 2006
- Conneau et al., *What you can cram into a single vector*, ACL 2018
