# RAG · RAGAS · uv 수업 정리

## 목차
1. [Python: for 루프와 객체 참조](#1-python-for-루프와-객체-참조)
2. [RAG 파이프라인](#2-rag-파이프라인)
   - 2.1 프롬프트에 Document 객체가 그대로 들어가는 문제
   - 2.2 청킹과 검색 설정
   - 2.3 리랭커(Reranker)
   - 2.4 RAG vs 전체 주입(Long Context)
3. [RAGAS로 RAG 평가하기](#3-ragas로-rag-평가하기)
4. [uv 패키지 관리](#4-uv-패키지-관리)
   - 4.1 `uv add -r requirements.txt` 실패 원인
   - 4.2 uv가 Python 버전을 고르는 방식
   - 4.3 requirements.txt 사용 팁
   - 4.4 팀 협업: 브랜치와 uv.lock 충돌

---

## 1. Python: for 루프와 객체 참조

`for doc in docs:`의 `doc`은 복사본이 아니라 **리스트 안의 같은 객체를 가리키는 이름(참조)** 이다.

- **객체 내부를 수정(mutation)** → 원본 리스트에 반영됨
- **변수에 다른 객체를 대입** → 이름만 바뀌고 원본은 그대로

```python
# 반영됨: 객체 내부의 딕셔너리를 직접 변경
for doc in docs:
    doc.metadata["filename"] = doc.metadata["source"]
print(docs[0].metadata["filename"])  # 값이 들어가 있음

# 반영 안 됨: doc이라는 이름만 새 객체를 가리킴
for doc in docs:
    doc = "다른 값"

# 요소 자체를 교체하려면 새 리스트를 만든다
docs = [transform(doc) for doc in docs]
```

---

## 2. RAG 파이프라인

### 2.1 프롬프트에 Document 객체가 그대로 들어가는 문제

retriever가 반환한 `Document` 리스트를 그대로 `{context}`에 넣으면, 프롬프트에 다음과 같은 문자열이 통째로 들어간다.

```
[Document(id='40c34eea-...', metadata={'source': 'https://...'}, page_content="..."), Document(...)]
```

→ id, 메타데이터(파일 경로, URL 등)까지 섞여 토큰이 낭비되고 노이즈가 된다.
보통은 `format_docs` 함수로 `page_content`만 이어 붙여 넣는다.

```python
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
```

### 2.2 청킹과 검색 설정

**로더와 청크 수**
- `PyMuPDFLoader`는 PDF를 **페이지 단위 Document**로 불러온다.
- `split_documents`는 각 Document 안에서만 자르고 **페이지 경계를 넘어 합치지 않는다.**
- 따라서 페이지가 `chunk_size`보다 짧으면 페이지 1개 = 청크 1개가 된다. (9페이지 PDF, `chunk_size=1000` → 9청크)

**retriever 기본값**
- `as_retriever()` 기본값: 유사도 검색, `k=4`

| 설정 | 전체 청크 수 | 질문마다 LLM에 들어가는 양 |
|---|---|---|
| `chunk_size=500` | 약 18개 | 약 2,000자 (문서의 ~20%) |
| `chunk_size=1000` | 9개 | 4페이지 (문서의 ~44%) |

→ 청크를 키워서 답이 좋아진 건 "RAG 개선"이라기보다 **전체 주입 쪽으로 다가간 것**에 가깝다.

**조항이 잘리는 문제**
- 단서 조항(예: "팀장 승인(혹은 팀과 협의)")이 청크 경계에서 잘리거나 섹션 제목과 다른 청크로 떨어지면 의미가 깨진다.
- `chunk_overlap=50`은 이를 막기에 작다.
- **Contextual Retrieval**(Anthropic): 각 청크에 그 청크를 설명하는 맥락을 덧붙인 뒤 임베딩 → 상위 20개 검색 실패율 35% 감소 보고.

**검색된 청크 직접 확인하기** (LangSmith 추적으로 봐도 됨)
```python
for d in retriever.invoke("연차를 사용하려면 최소 며칠 전에 신청해야 하나요?"):
    print(d.metadata.get("page"), "|", d.page_content[:150], "\n---")
```

**청킹 개선 방향**
- 사내 규정처럼 구조가 명확한 문서는 글자 수보다 **조항·섹션 단위 분할**이 효과적이다.
- 청크마다 섹션 제목을 붙이면 Contextual Retrieval의 간이 버전이 된다.
- 청크 **크기**보다 청크 **경계**를 먼저 고친다.

### 2.3 리랭커(Reranker)

검색으로 가져온 후보 문서를 **질문과의 관련도 기준으로 다시 정밀하게 순위를 매기는 단계**. 검색과 LLM 생성 사이의 필터.

**필요한 이유**
1차 검색(벡터 검색, BM25)은 속도 우선이다. 임베딩 검색은 질문과 문서를 각각 벡터로 압축해 유사도만 비교(**바이인코더**)하기 때문에:
- 주제는 비슷하지만 답은 없는 문서가 상위에 올라옴
- 부정어·조건 같은 미묘한 의미 차이를 놓침
- 정답 문서가 10~30위에 묻힘

**동작 흐름**
1. **1차 검색**: 후보를 넉넉히 가져옴 (예: 50~100개)
2. **리랭킹**: 각 후보를 질문과 함께 보고 관련도 재채점
3. **선별**: 상위 3~5개만 LLM에 전달

**크로스인코더(Cross-encoder)**: 질문과 문서를 한 입력으로 합쳐 모델에 넣어 단어 단위로 세밀하게 비교. 정확하지만 문서마다 모델을 돌려야 해서 느림 → 1차 후보에만 적용.

> 비유: 1차 검색 = 제목·키워드로 책을 한 수레 가져오기, 리랭커 = 사서가 책을 펼쳐보고 진짜 답이 있는 책만 고르기

**리랭커 종류**

| 종류 | 특징 |
|---|---|
| 크로스인코더 | 가장 흔함. 오픈소스 모델, 상용 Rerank API 대부분 |
| LLM 기반 | pointwise(문서별 점수) / listwise(목록 순서 결정). 정확하지만 비용·지연 큼 |
| Late interaction (ColBERT) | 토큰 단위 벡터를 미리 저장해 두고 세밀 비교. 바이인코더와 크로스인코더의 절충 |

**트레이드오프**
- 장점: 검색 정확도 상승, LLM 입력 문서 수 감소 → 토큰 비용 절감
- 단점: 요청마다 지연 증가
- 튜닝 포인트: 후보 수 → **재현율(recall)**, 남기는 수 → **정밀도(precision)**

### 2.4 RAG vs 전체 주입(Long Context)

**결론**: "모델이 좋아지면 RAG는 필요 없다"는 무조건 참은 아니다. 다만 문서가 작으면(수십 페이지) 전체 주입이 합리적일 수 있다.

**"많이 넣을수록 좋다" 쪽 근거**
- Li et al. (EMNLP 2024): 자원이 충분하면 Long Context가 평균 성능에서 RAG를 일관되게 앞섬
- Anthropic 권고: 지식 베이스가 약 20만 토큰(~500페이지) 미만이면 RAG 없이 전체를 넣어도 됨

**반대 근거**
| 연구 | 내용 |
|---|---|
| Lost in the Middle (Liu et al., TACL 2024) | 관련 정보가 입력의 앞·끝에 있을 때 성능 최고, 중간이면 크게 하락 |
| Context Rot (Chroma, 2025) | 18개 최신 모델 모두 입력이 길수록 성능이 불안정 (벡터DB 회사 연구라는 점은 감안) |
| OP-RAG (NVIDIA, 2024) | 청크 수를 늘리면 품질이 올라가다 떨어지는 **역U자 곡선**. 최적점에서 LC보다 적은 토큰으로 더 높은 품질 |
| LaRA (ICML 2025) | 만능 해법 없음. 모델·길이·과제·검색 특성에 따라 달라지며, 컨텍스트가 길수록 RAG 이점이 커짐 |
| 비용·속도 | 매 질문마다 전체 문서를 보내면 토큰 비용과 지연이 질문 수만큼 곱해짐 |

**에이전트 관점: 컨텍스트 엔지니어링**
- 에이전트는 시스템 프롬프트, 도구 정의, 도구 결과, 대화 이력이 턴마다 누적된다. 문서를 통째로 넣으면 그 공간을 처음부터 차지한다.
- LLM에도 **주의 예산(attention budget)** 이 있어서 컨텍스트가 길어질수록 집중력이 분산된다.
- 좋은 컨텍스트 엔지니어링 = 원하는 결과 가능성을 최대화하는 **신호가 강한 최소한의 토큰 집합** 찾기
- 방향: 검색을 도구로 주고 에이전트가 필요할 때 스스로 찾게 하는 **Agentic RAG**

**실천 가이드**
1. 수십 페이지 수준이면 전체 주입을 **기준선(baseline)** 으로 먼저 만든다. 문서가 커지거나 자주 바뀌거나 컨텍스트가 빠듯하면 RAG로 간다.
   ```python
   full_text = "\n\n".join(d.page_content for d in docs)
   chain_full = (
       {"context": lambda _: full_text, "question": RunnablePassthrough()}
       | prompt | llm | StrOutputParser()
   )
   ```
2. "한 번 맞았다"는 개선의 증거가 아니다. 질문에 정답 라벨을 붙여 평가셋을 만들고, chunk 500/1000, k 값, 전체 주입을 여러 번 돌려 비교한다.
3. 청크 크기보다 청크 경계를 먼저 고친다 (2.2 참고).
4. **Self-Route** (Li et al.): 먼저 RAG로 답해 보고, 모델이 "검색 내용으로 부족하다"고 판단하면 전체 문서로 넘김 → LC급 성능, 비용은 크게 절감.

> **한 줄 정리**: 청크를 키워 답이 좋아진 건 정답 조항이 잘리지 않고 들어갈 확률이 올라간 결과다. 문서가 커지고 컨텍스트가 누적될수록 "무엇을 넣을지 고르는 능력"이 곧 성능이다.

---

## 3. RAGAS로 RAG 평가하기

**RAGAS**: LLM이 채점관이 되어 RAG 시스템을 지표별로 0~1점으로 채점하는 평가 도구. 원 논문에서 사람 평가와의 일치율은 Faithfulness 95%, Answer Relevance 78%, Context Relevance 70%.

### 입력 데이터 (질문마다)

| 필드 | 내용 | 보통 누가 제공 |
|---|---|---|
| `user_input` | 질문 | 채점하는 쪽 |
| `retrieved_contexts` | 검색기가 찾아온 청크 텍스트 리스트 | 내 RAG |
| `response` | LLM이 생성한 답변 | 내 RAG |
| `reference` | 모범 정답 | 채점하는 쪽 |

⚠️ 답변만이 아니라 **검색된 컨텍스트도 함께 반환**하도록 코드를 짜야 한다. 검색 품질도 채점 대상이다.

⚠️ 버전별 컬럼명 차이
- 구버전(0.1): `question` / `answer` / `contexts` / `ground_truth`
- 최신: `user_input` / `response` / `retrieved_contexts` / `reference`

### 핵심 지표

| 지표 | 평가 대상 | 무엇을 보나 | 점수가 낮으면 |
|---|---|---|---|
| **Faithfulness** | 생성 | 답변의 각 주장이 컨텍스트에 근거하는지 (환각 여부) | 문서에 없는 내용을 지어냄 |
| **Answer Relevancy** | 생성 | 답변이 질문에 딱 맞게 답했는지 | 동문서답, 군더더기, 회피성 답변 |
| **Context Precision** | 검색 | 관련 청크가 검색 결과 상위에 있는지 | 쓸모없는 청크가 많이 섞임 |
| **Context Recall** | 검색 | 정답에 필요한 정보를 다 가져왔는지 | 필요한 문서를 놓침 |

- 네 지표를 함께 보면 문제가 **검색 실패인지 생성 실패인지** 구분할 수 있다.
- Faithfulness는 문서에 충실한지만 볼 뿐 **정답 여부는 모른다** → Answer Correctness, Factual Correctness 같은 정답 비교 지표를 추가로 쓰기도 한다.

### 평가 코드

```python
from ragas import EvaluationDataset, evaluate
from ragas.metrics import (Faithfulness, ResponseRelevancy,
                           LLMContextPrecisionWithReference, LLMContextRecall)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

samples = []
for q, ref in zip(questions, references):
    docs = my_retrieve(q)        # 검색된 청크 텍스트 리스트
    ans = my_generate(q, docs)   # 내 RAG의 답변
    samples.append({"user_input": q, "retrieved_contexts": docs,
                    "response": ans, "reference": ref})

result = evaluate(
    EvaluationDataset.from_list(samples),
    metrics=[Faithfulness(), ResponseRelevancy(),
             LLMContextPrecisionWithReference(), LLMContextRecall()],
    llm=LangchainLLMWrapper(ChatOpenAI(model="수업에서 쓰는 모델")),
    embeddings=LangchainEmbeddingsWrapper(OpenAIEmbeddings()),
)
print(result)
result.to_pandas()  # 문항별 점수 → 낮은 문항부터 원인 분석
```

### 지표별 개선 방법

- **Faithfulness**: 시스템 프롬프트에 "주어진 문서의 내용만으로 답하고, 없으면 추측하지 마라"를 명확히 넣는다. 효과가 가장 크다.
- **Answer Relevancy**: 질문에 바로 답하고 서론은 뺀다. 질문과 같은 언어로 답한다. 회피성 답변도 감점될 수 있다.
- **Context Precision**: top-k를 너무 크게 잡지 않는다. 리랭커를 붙인다. (재현율은 높은데 정밀도가 낮으면 노이즈가 섞이는 것 → 리랭킹이 효과적)
- **Context Recall**: 청크 크기·오버랩 조정, BM25 + 벡터 **하이브리드 검색**, 더 큰 top-k, 더 좋은 임베딩. 한국어 문서면 다국어 임베딩(예: `bge-m3`)만으로도 차이가 크다.

### 준비 순서
1. 평가 형식 확인: 사용 지표, 질문셋·정답 제공 여부, 제출 형식(함수/API/CSV), RAGAS 버전
2. 질문 10~20개와 정답을 만들어 위 코드로 **기준 점수** 뽑기
3. 가장 낮은 지표 하나를 골라 개선 → 재실행 반복 (보통 Faithfulness(프롬프트), Context Recall(청킹·임베딩)부터가 가성비 좋음)
4. 채점관이 LLM이라 **점수가 매번 조금씩 흔들린다**. 한 번의 결과보다 경향을 본다.

---

## 4. uv 패키지 관리

### 4.1 `uv add -r requirements.txt` 실패 원인

**증상**: `.venv`에서 `import dotenv` → `ModuleNotFoundError`, `pyproject.toml`의 `dependencies = []`, `uv.lock` 없음

**원인**
- `uv add`는 **원자적(all-or-nothing)** 으로 동작한다. 패키지 하나만 실패해도 `pyproject.toml`을 되돌리고 아무것도 설치하지 않는다.
- 실제 에러:
  ```
  error: Microsoft Visual C++ 14.0 or greater is required.
  hint: `scikit-network` (v0.33.5) was included because `rag-two-branch` depends on `scikit-network`
  ```
- 프로젝트가 **Python 3.14**를 사용 중인데, `scikit-network==0.33.5`의 Windows wheel은 **cp310~cp313까지만** 존재
- → uv가 소스(`.tar.gz`)에서 빌드 시도 → C++ 컴파일러(MSVC) 없음 → 빌드 실패 → 전체 롤백

**해결 (추천: Python 3.13으로 내리기)**
```powershell
uv python pin 3.13
# pyproject.toml: requires-python = ">=3.14" → ">=3.13"
uv add -r requirements.txt
```
대안: Visual C++ Build Tools를 설치해 3.14에서 소스 빌드 (번거로움)

**노트북 커널**: 설치 후에도 `.ipynb`에서 import가 안 되면 VS Code 커널 선택에서 `.venv\Scripts\python.exe`를 고른다.

### 4.2 uv가 Python 버전을 고르는 방식

uv는 PATH의 `python`이 아니라 **uv가 직접 설치한(managed) Python을 우선** 사용한다.

```
cpython-3.14.7   ...\AppData\Roaming\uv\python\...          ← uv managed
cpython-3.12.10  ...\AppData\Local\Programs\Python\...      ← system (python.org 설치)
```

- 기본 설정 `python-preference = "managed"` → managed Python 중 **가장 최신 버전** 선택
- 그래서 `uv init` 시 3.14가 선택되어 `.python-version`, `requires-python`, `.venv/pyvenv.cfg`에 기록됨
- 가상환경 활성화 상태의 `python`(3.14)과 `deactivate` 후의 `python`(3.12)은 **완전히 다른 Python**

```powershell
uv init --python 3.13      # 생성 시 버전 지정
uv python pin 3.13         # 기존 프로젝트의 .python-version 변경
uv python list             # uv가 볼 수 있는 Python 목록
```
- 시스템 Python 우선: `--python-preference system` 또는 `UV_PYTHON_PREFERENCE=system`
- 해당 버전이 없으면 uv가 자동으로 다운로드한다.

### 4.3 requirements.txt 사용 팁

`pip freeze` 결과처럼 **간접 의존성까지 전부** 들어 있는 requirements.txt를 `uv add -r`하면 100개 넘는 패키지가 모두 직접 의존성으로 등록된다.
→ 실제로 import하는 패키지만 추가하고 간접 의존성은 `uv.lock`에 맡기는 게 깔끔하다.

```powershell
uv add langchain langchain-openai langgraph ragas python-dotenv ipykernel
```

### 4.4 팀 협업: 브랜치와 uv.lock 충돌

`.venv`는 각자 PC에만 있고 git에 올리지 않으므로 충돌 대상이 아니다. 문제는 **의존성 정의 파일**(`pyproject.toml`, `uv.lock`)과 **로컬 환경이 그 파일과 맞는지**에서 생긴다.

**① 두 브랜치가 각각 패키지를 추가 → uv.lock 머지 충돌**
lock 파일은 손으로 합치지 말고 재생성한다. `pyproject.toml`이 기준, `uv.lock`은 계산 결과물.
```bash
# 1) pyproject.toml 충돌은 직접 해결 (두 패키지 모두 남기기)
# 2) uv.lock은 한쪽을 택한 뒤 재생성
git checkout --theirs uv.lock
uv lock
git add pyproject.toml uv.lock
```

**② `uv pip install` / `pip install`로 설치 → "내 PC에서는 되는데요"**
자기 `.venv`에만 설치되고 `pyproject.toml`에 기록되지 않는다.
- 규칙: 패키지는 반드시 `uv add`로
- CI에서 `uv sync --locked` (lock과 pyproject가 안 맞으면 실패)

**③ 브랜치를 바꿨는데 `.venv`는 이전 브랜치 상태**
- 브랜치 이동 후 `uv sync` 습관화 (lock에 없는 패키지 제거, 버전 맞춤)
- `uv run python ...`으로 실행하면 실행 전 자동 동기화
- git 훅으로 자동화:
  ```sh
  # .git/hooks/post-checkout
  #!/bin/sh
  uv sync --quiet
  ```

**④ 텍스트 충돌 없이 머지됐지만 의존성이 서로 안 맞음**
예: A는 `numpy>=2`, B는 `numpy<2`만 지원하는 라이브러리 추가 → `uv lock`이 resolution 실패
- 사람이 결정해야 함 (버전 업그레이드 또는 대체재)
- 예방: 의존성 변경은 작은 PR로 먼저 main에 머지, PR마다 CI에서 `uv lock --locked` / `uv sync --locked`

**⑤ 팀원마다 Python·uv 버전이 다름**
```bash
uv python pin 3.12   # .python-version 생성 → 커밋
```
```toml
[project]
requires-python = ">=3.12,<3.13"

[tool.uv]
required-version = ">=0.8"   # 팀 공통 uv 버전 범위 강제
```

**⑥ `.venv`를 실수로 커밋**
절대 경로와 OS 전용 바이너리가 들어 있어 다른 환경에서 깨진다.
```bash
echo ".venv/" >> .gitignore
git rm -r --cached .venv   # 이미 올라간 경우 추적 해제
```

**팀 규칙 요약**

| 커밋함 | 커밋 안 함 |
|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version` | `.venv/` |

1. 패키지 추가·삭제는 `uv add` / `uv remove`만 사용
2. pull, checkout, merge 후에는 `uv sync` (또는 항상 `uv run`으로 실행)
3. `uv.lock` 충돌은 손으로 고치지 말고 `uv lock`으로 재생성
4. CI에서 `uv sync --locked`로 lock 불일치 차단
5. 의존성 변경은 별도의 작은 PR로 먼저 머지

---

## 참고 자료
- Ragas 공식 문서: List of available metrics / Evaluate a simple RAG system / Evaluation Dataset
- Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL 2024)
- Chroma, *Context Rot: How Increasing Input Tokens Impacts LLM Performance* (2025)
- Li et al., *Retrieval Augmented Generation or Long-Context LLMs?* (EMNLP 2024)
- Yu et al. (NVIDIA), *In Defense of RAG in the Era of Long-Context Language Models* (2024)
- Li et al., *LaRA: No Silver Bullet for LC or RAG Routing* (ICML 2025)
- Anthropic, *Contextual Retrieval* (2024)
- Anthropic, *Effective context engineering for AI agents* (2025)
- LangChain API Reference: `as_retriever`
