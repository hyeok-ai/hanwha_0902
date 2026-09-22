# RAG 정리 (9월 22일)

텍스트 분할 → 임베딩 → 벡터 DB(Pinecone) 저장 → 검색

---

## 1. 코사인 유사도 vs 내적

### 수학적 차이

| 구분 | 코사인 유사도 (`cosine_similarity`) | 내적 (Dot Product, `@`) |
|---|---|---|
| 초점 | 벡터의 방향(각도) | 벡터의 방향 + 크기 |
| 결과 범위 | -1 ~ 1 | 제한 없음 |
| 연산 속도 | 상대적으로 느림 (나눗셈 추가) | 매우 빠름 |
| 사용 시점 | 벡터 정규화 여부를 확신할 수 없을 때 | 벡터가 정규화(길이=1)되어 있고 빠른 검색이 필요할 때 |

$$\text{Cosine Similarity} = \frac{A \cdot B}{\|A\| \times \|B\|}$$

- $A \cdot B$: 내적, $\|A\|$: 벡터 A의 길이
- 코사인 유사도 = 내적을 두 벡터 길이의 곱으로 나눈 값

### 정규화된 벡터에서는 두 값이 같다

- OpenAI(`text-embedding-3-small` 등)와 다수의 HuggingFace 임베딩 모델은 길이가 1로 **정규화된 벡터**를 반환한다.
- $\|A\| = \|B\| = 1$이면 분모가 1 → **내적 = 코사인 유사도**.

### 실무에서 내적(`@`)을 쓰는 이유

- `cosine_similarity`: 내적 + 각 벡터 길이 계산 + 나눗셈
- `@` (NumPy 내적): 곱하고 더하기만 수행
- 질문 1개를 수만~수백만 개 문서 벡터와 비교하므로, 결과가 같다면 연산이 가벼운 내적이 유리하다.

---

## 2. CharacterTextSplitter vs RecursiveCharacterTextSplitter

두 클래스 모두 `langchain_text_splitters.TextSplitter`를 상속한다.

- 공통 파라미터: `chunk_size`, `chunk_overlap`, `length_function`, `add_start_index`
- 공통 메서드: `split_text()`, `create_documents()`, `split_documents()`

### 분할 전략

**CharacterTextSplitter**
- 단일 구분자(기본값 `"\n\n"`)로만 분할한 뒤, `chunk_size`를 넘지 않는 범위에서 조각을 병합한다.
- 조각 하나가 이미 `chunk_size`보다 크면 더 쪼개지 않는다 → 초과 청크가 남고 경고 출력:
  `Created a chunk of size X, which is longer than the specified Y`

**RecursiveCharacterTextSplitter**
- 구분자 목록(기본값 `["\n\n", "\n", " ", ""]`)을 순서대로 시도한다.
- 문단 → 줄 → 단어 → 글자 순으로 큰 조각을 재귀적으로 분할한다.
- 마지막 구분자가 `""`이므로 모든 청크가 `chunk_size` 이하로 보장된다.
- 가능한 한 의미 단위(문단, 문장, 단어)를 유지한다.

### 비교표

| 항목 | CharacterTextSplitter | RecursiveCharacterTextSplitter |
|---|---|---|
| 구분자 | 단일 (`separator="\n\n"`) | 목록 (`separators=["\n\n", "\n", " ", ""]`) |
| 분할 방식 | 한 번 분할 후 병합 | 큰 조각을 다음 구분자로 재귀 분할 후 병합 |
| `chunk_size` 보장 | 보장 안 됨 | 보장됨 (기본 설정 기준) |
| 의미 단위 보존 | 구분자가 텍스트 구조와 맞을 때만 좋음 | 문단 → 줄 → 단어 순으로 최대한 보존 |
| `keep_separator` 기본값 | `False` | `True` |
| 정규식 구분자 | `is_separator_regex=True` | 동일 |
| 코드 분할 | 없음 | `from_language(Language.PYTHON)` 등 |
| 추천 용도 | 구조가 명확하고 일정한 텍스트 | 일반 텍스트 (LangChain 권장 기본값) |

### 예제

```python
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

text = """LangChain은 LLM 애플리케이션 개발 프레임워크입니다.

이 문단은 줄바꿈 없이 매우 길게 이어지는 문장으로 구성되어 있어서 하나의 문단만으로도 chunk_size를 훌쩍 넘어가게 됩니다. 이런 경우 두 스플리터의 동작 차이가 드러납니다.

짧은 마지막 문단."""

# 1) CharacterTextSplitter
char_splitter = CharacterTextSplitter(separator="\n\n", chunk_size=50, chunk_overlap=0)
for c in char_splitter.split_text(text):
    print(len(c), repr(c))
# → 긴 문단이 50자를 넘는 청크로 그대로 남고 경고 출력

# 2) RecursiveCharacterTextSplitter
rec_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
for c in rec_splitter.split_text(text):
    print(len(c), repr(c))
# → 긴 문단이 공백(단어) 기준으로 다시 쪼개져 모든 청크가 50자 이하
```

코드 분할 시 언어별 구분자 사용:

```python
from langchain_text_splitters import Language

py_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=200, chunk_overlap=0
)
# "\nclass ", "\ndef ", "\n\tdef " 등을 우선 구분자로 사용
```

### 선택 기준

- **CharacterTextSplitter**: 로그 파일, `---`로 구분된 레코드처럼 구분자가 일정한 텍스트. 레코드를 쪼개지 않는 편이 나은 경우.
- **RecursiveCharacterTextSplitter**: 구조가 제각각인 일반 텍스트. 청크 크기 상한이 중요한 RAG(임베딩 모델 입력 길이, 컨텍스트 윈도우)에 유리. 대부분 이것으로 시작.
- 두 클래스 모두 `from_tiktoken_encoder()` 지원 → 글자 수 대신 **토큰 수**로 `chunk_size` 계산.

---

## 3. chunk_overlap

연속된 두 청크가 공유하는 텍스트의 **최대** 길이. 길이는 `length_function`(기본 `len`, 글자 수)으로 계산한다.

### 필요한 이유

고정 크기로 자르면 문장/논리가 청크 경계에서 끊긴다.
예: "이 방법의 단점은" | "메모리 사용량이 크다는 것이다"
→ 겹침을 두면 경계 부근 내용이 양쪽 청크에 모두 들어가 문맥 손실이 줄어든다.

### 실제 동작 방식

1. 텍스트를 구분자로 나눠 조각(split)을 만든다.
2. 조각을 이어 붙여 청크를 만든다.
3. 청크가 완성되면 앞에서부터 조각을 하나씩 버린다.
4. 남은 조각들의 길이 합이 `chunk_overlap` 이하가 되면, 남은 조각이 다음 청크의 시작이 된다.

결과적으로:
- 겹침은 항상 **조각 단위**로 구성된다 (단어/문단이 중간에서 잘린 채 겹치지 않음).
- 실제 겹침 길이는 `chunk_overlap`보다 작을 수 있다.
- 조각 하나가 `chunk_overlap`보다 크면 겹침이 생기지 않을 수 있다.

```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(separator=" ", chunk_size=5, chunk_overlap=2)
print(splitter.split_text("a b c d e f g h i j"))
# ['a b c', 'c d e', 'e f g', 'g h i', 'i j']
```

`chunk_overlap=2`인데 실제 겹침은 한 글자인 이유:
1. 첫 청크 `"a b c"` 완성 → 앞에서부터 조각 제거
2. `"a"` 제거 → `"b c"`(길이 3, 구분자 포함) > 2 → 계속 제거
3. `"b"` 제거 → `"c"`(길이 1) ≤ 2 → 다음 청크의 시작

### 스플리터별 차이

- **CharacterTextSplitter** (`"\n\n"`): 조각이 문단 단위라 대개 `chunk_overlap`보다 커서 겹침 효과가 거의 없는 경우가 많다.
- **RecursiveCharacterTextSplitter**: 조각이 줄/단어 단위로 작아 겹침이 설정값에 가깝게 적용된다.

### 제약과 설정 팁

- `chunk_overlap > chunk_size`이면 생성 시점에 `ValueError`. 음수 불가.
- 일반적으로 `chunk_size`의 **10~20%**로 시작 (예: `chunk_size=1000` → `chunk_overlap=100~200`).
- 장점: 경계 문맥 보존
- 단점: 중복 증가 → 청크 수, 임베딩 비용, 저장 공간 증가, 검색 결과에 유사 청크 중복
- 각 청크가 독립 단위(로그 레코드 등)이면 `chunk_overlap=0`이 적절.

### 겹침이 생기지 않는 경우

`chunk_overlap`은 겹침을 **보장하는 값이 아니라 허용 최대치**다.

**① 조각 하나가 `chunk_overlap`보다 클 때**

```python
from langchain_text_splitters import CharacterTextSplitter

p1 = "가" * 60
p2 = "나" * 60
text = p1 + "\n\n" + p2

splitter = CharacterTextSplitter(separator="\n\n", chunk_size=100, chunk_overlap=20)
chunks = splitter.split_text(text)
print([len(c) for c in chunks])      # [60, 60]
print(chunks[1].startswith("가"))     # False → 겹침 없음
```

문단(60자) > `chunk_overlap`(20자) → 첫 청크 이후 문단 전체를 버리고 두 번째 청크는 빈 상태에서 시작.

**② 다음 조각이 커서 공간이 부족할 때**

겹침 조각 + 다음 조각이 `chunk_size`를 넘으면 겹침 조각을 추가로 버린다. 다음 조각이 `chunk_size`에 가까우면 겹침이 전부 제거될 수 있다.

**③ RecursiveCharacterTextSplitter의 재귀 분할 경계**

너무 큰 조각을 만나면 모아 둔 작은 조각들을 먼저 청크로 확정하고, 큰 조각은 따로 재귀 분할한다. 두 결과는 단순히 이어 붙여지므로 그 **경계에는 겹침이 적용되지 않는다**. 재귀 분할된 내부 청크끼리는 정상 적용.

### 겹침을 확실히 원할 때

- RecursiveCharacterTextSplitter 사용 (조각이 단어 수준까지 작아짐)
- `chunk_overlap`을 조각 크기보다 충분히 크게 설정
- 실제 결과를 직접 확인:

```python
for a, b in zip(chunks, chunks[1:]):
    overlap = next(
        (k for k in range(min(len(a), len(b)), 0, -1) if a.endswith(b[:k])), 0
    )
    print(overlap)
```

- 글자 단위로 정확히 일정한 겹침이 필요하면 슬라이딩 윈도우로 직접 분할: `text[i:i+size]`를 `step = size - overlap` 간격으로 반복. (LangChain 스플리터는 겹침의 정확성보다 의미 단위 보존을 우선하도록 설계됨)

---

## 4. 벡터 데이터베이스와 Pinecone

### 벡터 데이터베이스

- 임베딩: 텍스트/이미지/오디오를 수백~수천 차원의 숫자 벡터로 변환. 의미가 비슷하면 벡터 공간에서 가깝다.
  - 예: "강아지가 공원에서 뛰어논다" ↔ "개가 잔디밭에서 달린다" → 단어는 달라도 벡터는 가까움
- 일반 DB: 키워드 **정확 일치** 검색에 강함
- 벡터 DB: **의미 유사도** 검색에 특화. 핵심 기능은 근사 최근접 이웃 검색(**ANN**).

### Pinecone

- 완전 관리형(fully managed) 클라우드 벡터 DB. 서버 운영 없이 API 키로 접속.
- (Chroma, FAISS는 로컬에서 직접 실행)
- 주요 용도: RAG, 의미 기반 검색, 추천 시스템, 유사 이미지 검색, 이상 탐지
- 장점: 인프라 관리 불필요, 확장 용이, 메타데이터 필터링, LangChain/LlamaIndex 연동
- 단점: 유료 클라우드, 셀프 호스팅 불가
- 대안: Weaviate, Milvus, Qdrant, Chroma (오픈소스), pgvector (PostgreSQL 확장)

### 데이터 계층 구조

```
Project (API 키가 속함)
└── Index (벡터 저장소. RDB의 데이터베이스/테이블에 해당)
    └── Namespace (인덱스 안의 논리적 칸막이)
        └── Record (저장 단위)
            ├── id            : 고유 식별자
            ├── values        : Dense 벡터 (예: 4096개 실수)
            ├── sparse_values : Sparse 벡터 (선택)
            └── metadata      : 부가 정보 (source, page, 원문 등)
```

### Index

생성 시 정하며 **이후 변경 불가**:

- **dimension**: 벡터 길이. 임베딩 모델 출력 차원과 반드시 일치해야 함.
  - OpenAI `text-embedding-3-small` / `ada-002`: 1536
  - OpenAI `text-embedding-3-large`: 3072
  - Upstage `solar-embedding-1-large`: 4096
- **metric**: `cosine`(방향), `euclidean`(거리), `dotproduct`(내적). 보통 임베딩 모델 권장 방식을 따름.
- **배포 방식**: Serverless(기본, 사용량 기반 자동 확장) / Pod. 클라우드 제공자와 리전 선택.

→ 한 인덱스에는 같은 차원·같은 임베딩 모델의 벡터만 저장. 다른 모델을 쓰면 인덱스를 새로 만들어야 함.

### Namespace

- 인덱스 내부를 논리적으로 분리 (폴더/파티션 개념)
- **검색은 항상 하나의 namespace 안에서만** 수행
- 별도 생성 불필요: upsert 시 이름을 지정하면 자동 생성, 미지정 시 기본 namespace

멀티테넌시 예시:

```
인덱스: company-docs (1536차원, cosine)
├─ 네임스페이스: customer-a   ← A사 문서만
├─ 네임스페이스: customer-b   ← B사 문서만
└─ 네임스페이스: customer-c   ← C사 문서만
```

다른 고객 문서가 섞일 위험이 없고, 탈퇴 시 namespace만 삭제하면 되며, 검색 범위가 작아 속도·비용 면에서 유리.

### Namespace vs 메타데이터 필터

| 상황 | 선택 |
|---|---|
| 데이터가 완전히 분리되어 섞여 검색될 일이 없음 (고객별, 사용자별) | Namespace |
| 같은 데이터 안에서 조건을 바꿔 유연하게 거름 (날짜, 카테고리, 문서 종류) | 메타데이터 필터 |

실무에서는 병행: 고객별 namespace + 그 안에서 "2024년 이후 문서만" 같은 조건은 메타데이터 필터.

> Pinecone은 원문 텍스트를 별도로 저장하지 않는다 → 원문을 `metadata`에 넣어 둔다 (예: `context` 키).

---

## 5. Pinecone 하이브리드 검색 실습 코드 흐름

문서 준비 → 인덱스 생성 → 벡터 변환·저장 → 관리(조회/삭제) → 검색

대부분의 함수는 `langchain_teddynote.community.pinecone`의 래퍼이며, 내부에서 Pinecone 공식 SDK(`create_index`, `upsert`, `query`, `delete` 등)를 호출한다.

### 5.1 준비

```python
from dotenv import load_dotenv
load_dotenv()   # .env의 PINECONE_API_KEY, UPSTAGE_API_KEY 등을 환경변수로 로드

from langchain_teddynote import logging
logging.langsmith("CH09-VectorStores")   # LangSmith 실행 기록 (디버깅용)

from langchain_teddynote.korean import stopwords
stopword = stopwords()   # 한국어 불용어 목록 (Sparse 벡터 생성 시 제거)
```

### 5.2 문서 로드 및 분할

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

split_docs = []
files = sorted(glob.glob("data/*.pdf"))
for file in files:
    loader = PyMuPDFLoader(file)
    split_docs.extend(loader.load_and_split(text_splitter))
```

- 문서 전체를 하나의 벡터로 만들면 의미가 뭉개지므로 작게 분할
- `split_docs`: `Document` 리스트 (`page_content` + `metadata`)

### 5.3 전처리: `preprocess_documents`

```python
contents, metadatas = preprocess_documents(
    split_docs=split_docs,
    metadata_keys=["source", "page", "author"],
    min_length=5,
    use_basename=True,
)
```

- `contents`: 본문 문자열 리스트
- `metadatas`: `{"source": [...], "page": [...], "author": [...]}` 형태
- `metadata_keys`: 필요한 메타데이터만 유지 (레코드당 메타데이터 용량 제한 있음)
- `min_length=5`: 5자 미만 조각 제거 (페이지 번호만 있는 조각 등)
- `use_basename=True`: 경로 제거, 파일명만 저장 → 파일명 필터링이 쉬워짐

### 5.4 인덱스 생성: `create_index`

```python
pc_index = create_index(
    api_key=os.environ["PINECONE_API_KEY"],
    index_name="teddynote-db-index",
    dimension=4096,
    metric="dotproduct",
)
```

내부적으로 공식 SDK 코드와 동일:

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=...)
pc.create_index(
    name=...,
    dimension=4096,
    metric="dotproduct",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)
index = pc.Index(name)
```

- `dimension=4096`: Upstage `solar-embedding-1-large` 출력 차원
- `metric="dotproduct"`: **Pinecone에서 Dense + Sparse 하이브리드 검색은 dotproduct 인덱스에서만 지원**

**Serverless vs Pod**
- Serverless: spec 미지정 시 기본. 무료 플랜 가능, 사용량 기반 과금, 인프라 관리 불필요.
- Pod: `PodSpec(environment="us-west1-gcp", pod_type="p1.x1", pods=1)`. 전용 서버 방식, 유료. `pod_type`은 서버 종류/크기, `pods`는 대수.

### 5.5 Sparse Encoder (키워드 검색용)

**Dense vs Sparse 벡터**

| | Dense | Sparse |
|---|---|---|
| 생성 | 임베딩 모델 | BM25 등 통계 기반 |
| 형태 | 모든 칸에 값 (예: 4096개 실수) | 어휘 사전 크기, 대부분 0 → `{indices: [...], values: [...]}`로 저장 |
| 강점 | 의미 유사도 ("AI 회사 투자" ≈ "앤스로픽에 20억 달러 투자") | 정확한 키워드 일치 (고유명사, 신조어) |

- **BM25**: 해당 문서에 자주 나오지만 전체 문서에서는 드문 단어에 높은 점수
- 두 방식을 섞으면 서로의 약점을 보완 → 하이브리드 검색

```python
sparse_encoder = create_sparse_encoder(stopwords(), mode="kiwi")
```

- 한국어는 조사 때문에 "앤스로픽의", "앤스로픽은"이 다른 단어로 취급됨 → Kiwi 형태소 분석기로 분리 후 불용어 제거

```python
saved_path = fit_sparse_encoder(
    sparse_encoder=sparse_encoder,
    contents=contents,
    save_path="./sparse_encoder.pkl",
)
```

- BM25는 전체 문서 기준 단어 통계를 먼저 학습해야 함 → 학습 후 pickle 저장
- 질문을 Sparse 벡터로 바꿀 때 **반드시 같은 인코더**를 써야 함 (단어 번호 체계 일치)
- 다시 불러오기: `load_sparse_encoder("./sparse_encoder.pkl")`

### 5.6 저장: Upsert

Upsert = Update + Insert. 같은 id가 없으면 삽입, 있으면 덮어씀.

```python
upstage_embeddings = UpstageEmbeddings(model="solar-embedding-1-large-passage")
```

- Upstage는 **문서 저장용(passage)**과 **질문용(query)** 모델을 분리 제공
- 검색 시에는 `solar-embedding-1-large-query` 사용 (두 모델은 같은 벡터 공간을 공유하도록 짝으로 학습됨)

```python
upsert_documents(
    index=pc_index,
    namespace="teddynote-namespace-01",
    contents=contents,
    metadatas=metadatas,
    sparse_encoder=sparse_encoder,
    embedder=upstage_embeddings,
    batch_size=32,
)
```

- 32개씩 배치 처리: Dense 벡터(embedder) + Sparse 벡터(sparse_encoder) + 메타데이터(원문 `context` 추가) → `index.upsert(vectors=[...], namespace=...)`
- 배치로 나누는 이유: Pinecone과 임베딩 API 모두 요청당 크기 제한

레코드 형태:

```python
{
    "id": "doc-0",
    "values": [0.01, -0.23, ...],   # 4096개
    "sparse_values": {"indices": [...], "values": [...]},
    "metadata": {"context": "원문...", "source": "xxx.pdf", "page": 13, "author": "dj"},
}
```

`upsert_documents_parallel`: 같은 작업을 `max_workers=30` 스레드로 병렬 처리. 대용량에서 빠르지만 API rate limit에 걸릴 수 있으므로 문서가 적으면 일반 버전 사용.

### 5.7 조회와 삭제

**인덱스 상태 확인** (공식 메서드)

```python
pc_index.describe_index_stats()
# {'dimension': 4096,
#  'index_fullness': 0.0,
#  'namespaces': {'teddynote-namespace-02': {'vector_count': 1291}},
#  'total_vector_count': 1291}
```

- `namespaces`: namespace별 벡터 수
- `index_fullness`: 용량 사용률 (주로 Pod 인덱스에서 의미)

**namespace 전체 삭제**

```python
delete_namespace(pinecone_index=pc_index, namespace="teddynote-namespace-01")
# 내부: index.delete(delete_all=True, namespace=...)
```

**메타데이터 조건 삭제**

```python
delete_by_filter(
    pinecone_index=pc_index,
    namespace="teddynote-namespace-02",
    filter={"source": {"$eq": "SPRi AI Brief_8월호_산업동향.pdf"}},
)
```

- 실습 자료 작성 당시 Serverless에서 미지원(Pod 전용)으로 안내됨. 지원 범위는 최신 공식 문서 확인 필요.

**필터 문법 (MongoDB 유사)**

| 연산자 | 의미 |
|---|---|
| `$eq` / `$ne` | 같음 / 다름 |
| `$gt` / `$gte` | 초과 / 이상 |
| `$lt` / `$lte` | 미만 / 이하 |
| `$in` / `$nin` | 목록에 포함 / 미포함 |

### 5.8 검색기(Retriever) 생성

```python
pinecone_params = init_pinecone_index(
    index_name="teddynote-db-index",
    namespace="teddynote-namespace-02",
    api_key=os.environ["PINECONE_API_KEY"],
    sparse_encoder_path="./sparse_encoder.pkl",
    stopwords=stopwords(),
    tokenizer="kiwi",
    embeddings=UpstageEmbeddings(model="solar-embedding-1-large-query"),
    top_k=5,
    alpha=0.5,
)

pinecone_retriever = PineconeKiwiHybridRetriever(**pinecone_params)
```

- `init_pinecone_index`: 기존 인덱스에 **연결**(생성 아님) + Sparse 인코더 로드 + 질문용 임베딩 + 검색 설정을 딕셔너리로 반환
- `top_k=5`: 상위 5개 결과
- `alpha`: Dense에 `alpha`, Sparse에 `1 - alpha` 가중치
  - `alpha=1`: 순수 의미 검색
  - `alpha=0`: 순수 키워드 검색
  - `alpha=0.5`: 반반
- `**`: 딕셔너리를 키워드 인자로 언패킹
- LangChain Retriever 규격 → RAG 체인에 바로 연결 가능

`invoke(질문)` 내부 동작:
1. 질문 → query 임베딩 모델로 Dense 벡터
2. 질문 → Kiwi + BM25 인코더로 Sparse 벡터
3. `alpha`로 두 벡터에 가중치 적용
4. `index.query(vector=..., sparse_vector=..., top_k=..., namespace=..., include_metadata=True)`
5. 결과 metadata의 `context`를 `page_content`로 삼아 `Document` 리스트 반환

### 5.9 검색 실행

```python
# 기본 검색 (top_k=5, alpha=0.5)
search_results = pinecone_retriever.invoke("gpt-4o 미니 출시 관련 정보에 대해서 알려줘")
```

- 결과 metadata의 `page`가 `13.0`인 이유: Pinecone은 메타데이터 숫자를 모두 **float**로 저장

**`search_kwargs`로 호출마다 설정 변경**

```python
pinecone_retriever.invoke("앤스로픽", search_kwargs={"k": 1})
pinecone_retriever.invoke("앤스로픽", search_kwargs={"alpha": 1, "k": 1})  # 의미 검색
pinecone_retriever.invoke("앤스로픽", search_kwargs={"alpha": 0, "k": 1})  # 키워드 검색
```

- `alpha=1` → "앤스로픽이 개발자 콘솔을 업데이트... 클로드 2.1" 문단
- `alpha=0` → "구글, 앤스로픽에 20억 달러 투자" 문단
- 같은 질문이라도 유사도 기준에 따라 결과가 달라짐

**메타데이터 필터링**

```python
search_kwargs={"filter": {"page": {"$lt": 5}}, "k": 2}
search_kwargs={"filter": {"source": {"$eq": "SPRi AI Brief_8월호_산업동향.pdf"}}, "k": 3}
```

- 필터는 유사도 계산 전에 후보를 좁힘 → "특정 파일에서만 검색" 같은 요구를 정확히 처리
- `use_basename=True`로 파일명만 저장해 두었기 때문에 필터가 간단해짐

### 5.10 Reranking (재순위화)

```python
reranked_results = pinecone_retriever.invoke(
    "앤스로픽의 클로드 소넷",
    search_kwargs={"rerank": True, "rerank_model": "bge-reranker-v2-m3", "top_n": 3},
)
```

- 벡터 검색: 질문과 문서를 **각각** 벡터화해 비교 → 빠르지만 정밀도 한계
- Reranker: 질문과 문서를 **한 쌍으로 함께** 읽고 관련도를 직접 채점 → 느리지만 정확
- 일반 패턴: 벡터 검색으로 후보를 넉넉히 뽑고 → reranker로 재정렬 → 상위 `top_n`만 유지
- Pinecone Inference API(`pc.inference.rerank`) 사용, 결과 metadata에 `rerank_score` 추가
- pinecone 라이브러리 버전에 따라 동작하지 않을 수 있음

---

## 6. 전체 흐름 요약

| 단계 | 사용 함수 | 역할 |
|---|---|---|
| 문서 준비 | `PyMuPDFLoader`, `RecursiveCharacterTextSplitter`, `preprocess_documents` | PDF를 300자 조각으로 분할, 본문/메타데이터 정리 |
| 저장소 생성 | `create_index` | 4096차원, dotproduct 인덱스 생성 |
| 키워드 인코더 | `create_sparse_encoder`, `fit_sparse_encoder`, `load_sparse_encoder` | Kiwi + BM25 학습 후 pkl 저장/로드 |
| 저장 | `upsert_documents`, `upsert_documents_parallel` | Dense + Sparse 벡터와 메타데이터를 namespace에 upsert |
| 관리 | `describe_index_stats`, `delete_namespace`, `delete_by_filter` | 상태 확인, 전체/조건부 삭제 |
| 검색 | `init_pinecone_index`, `PineconeKiwiHybridRetriever`, `invoke` | alpha 가중 하이브리드 검색, 필터, rerank |

### 핵심 체크포인트

1. 인덱스 `dimension` = 임베딩 모델 출력 차원
2. 하이브리드 검색 → `metric="dotproduct"` 필수
3. 저장과 검색에 쓰는 **Sparse 인코더(pkl)**와 **임베딩 모델(passage/query 짝)**이 서로 일치해야 함
