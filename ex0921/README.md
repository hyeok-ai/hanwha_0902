# 9월 21일 수업 정리

## 목차

1. [RAG 기초: 문서 분할(Split)](#1-rag-기초-문서-분할split)
2. [LangChain PDF 로더](#2-langchain-pdf-로더)
3. [지식 그래프와 ConversationKGMemory](#3-지식-그래프와-conversationkgmemory)
4. [LangGraph](#4-langgraph)
5. [uv와 venv 함께 사용하기](#5-uv와-venv-함께-사용하기)
6. [이미 push한 커밋 되돌리기 (Git)](#6-이미-push한-커밋-되돌리기-git)
7. [DevOps 개요](#7-devops-개요)

---

## 1. RAG 기초: 문서 분할(Split)

### 문서를 split 하는 이유

원본 문서가 너무 길기 때문이다. 구체적으로는 다음과 같다.

- **컨텍스트 윈도우 한계**: LLM이 한 번에 처리할 수 있는 토큰 수에는 제한이 있다.
- **검색 정확도**: 긴 문서를 통째로 임베딩하면 의미가 희석된다. 작은 청크(chunk) 단위로 나눠야 질문과 관련된 부분만 정확히 찾아올 수 있다.
- **비용 절감**: 필요한 청크만 프롬프트에 넣으므로 토큰 비용이 줄어든다.

### 참고

- 이미 `invoke`한 결과를 재시도(retry)하여 더 나은 결과로 교정하는 기법도 있다.

---

## 2. LangChain PDF 로더

LangChain은 PDF 파서를 직접 만들지 않았다. 기존 PDF 라이브러리들을 **같은 인터페이스로 감싼 래퍼(wrapper)** 를 제공한다.

### 로더별 내부 라이브러리

| LangChain 로더 | 내부 라이브러리 | 특징 |
|---|---|---|
| `PyPDFLoader` | pypdf | 순수 파이썬, 가볍고 설치가 쉬움 |
| `PyMuPDFLoader` | PyMuPDF (fitz) | 빠르고 메타데이터가 풍부함 (단, AGPL 라이선스) |
| `UnstructuredPDFLoader` | unstructured | Title, NarrativeText 같은 요소 단위로 분류 가능, 의존성이 무거움 |
| `PyPDFium2Loader` | pypdfium2 | 크롬의 PDF 엔진(PDFium) 기반, 빠르고 품질이 괜찮음 |
| `PDFMinerLoader` / `PDFMinerPDFasHTMLLoader` | pdfminer.six | 폰트 크기·위치 같은 레이아웃 정보를 자세히 제공 |
| `PDFPlumberLoader` | pdfplumber | pdfminer 기반, 표 추출과 글자 단위 정보에 강함 |

> `PyPDFDirectoryLoader`는 새로운 파서가 아니라, pypdf로 폴더 안의 PDF를 한꺼번에 읽는 편의 기능이다.

### 파서가 여러 개인 이유

PDF에는 "문단"이나 "문장"이 저장되어 있지 않고, **"이 좌표에 이 글자를 그려라"** 라는 그리기 명령이 들어 있다. 파서마다 글자 조각을 텍스트로 재조립하는 방식이 달라 결과도 달라진다.

- **띄어쓰기와 읽는 순서**: 한글 띄어쓰기가 사라지거나, 2단 레이아웃에서 좌우 문단이 섞일 수 있다.
- **표**: 표를 한 줄로 뭉개는 파서도 있고, 구조를 살려주는 파서도 있다.
- **속도와 무게**: 대량 처리 시 속도, 배포 환경에서는 의존성 크기가 중요하다.
- **부가 정보**: 폰트 크기, 요소 종류(제목/본문) 등을 주는 파서가 따로 있다. (예: `PDFMinerPDFasHTMLLoader`로 폰트 크기를 읽어 제목 기준으로 문서 분할)
- **라이선스**: PyMuPDF는 AGPL이라 상업 서비스에서 부담이 될 수 있다.

### LangChain이 실제로 해준 일: 통일된 출력 형식

어떤 로더를 쓰든 결과는 `Document(page_content=..., metadata=...)` 리스트로 나온다.

```python
loader = PyPDFLoader("file.pdf")
# 한 줄만 바꿔도 이후 코드(분할, 임베딩, 벡터DB)는 그대로 사용 가능
loader = PyMuPDFLoader("file.pdf")
```

이 로더들은 `langchain_community` 패키지에 있다. 커뮤니티가 외부 도구 연동을 계속 추가하는 구조이기 때문이다.

### 로더 선택 가이드

실제 다룰 PDF에 여러 로더를 돌려보고 결과를 비교하는 것이 가장 확실하다. 한글 문서라면 띄어쓰기와 표를 꼭 확인한다.

- 빠르고 무난한 기본값 → **PyMuPDF** 또는 **PyPDFium2**
- 표가 중요 → **PDFPlumber**
- 제목/본문 구분하여 구조적으로 분할 → **Unstructured** 또는 **PDFMiner(HTML)**
- 스캔본(이미지 PDF) → 위 로더로는 텍스트가 거의 안 나옴. **OCR** 기반 방식이나 문서 파싱 전용 서비스 검토

---

## 3. 지식 그래프와 ConversationKGMemory

흩어진 정보나 대화 내역을 단순 텍스트가 아닌 **관계망** 형태로 구조화해, LLM이 더 정확하게 기억하고 활용하도록 돕는 기술이다.

### 3.1 지식 그래프 (Knowledge Graph)

정보를 **노드(Node, 개체)** 와 **엣지(Edge, 관계)** 로 연결한 네트워크 형태의 데이터베이스.

- **구조**: `(주어) -[관계]-> (목적어)` 형태의 **트리플(Triple)** 로 저장
- **LangChain에서의 역할**: LLM으로 문서에서 개체와 관계를 자동 추출하고, Neo4j, NetworkX 등의 그래프 DB에 저장
- **장점**: 벡터 검색이 놓치기 쉬운 **복잡한 관계 추론** 가능 → **Graph RAG**
  - 예: "A 회사의 CEO인 B가 투자한 C 스타트업" 같은 연결 고리를 추적

### 3.2 ConversationKGMemory

지식 그래프 원리를 챗봇의 메모리에 적용한 LangChain 메모리 모듈.

- **동작 방식**: 전체 대화를 통째로 저장하는 대신, 대화 속 주요 개체(Entity)와 관계를 실시간 추출하여 작은 지식 그래프로 저장

**예시**

```
사용자: "내 여동생 이름은 지수고, 그녀는 고양이 '나비'를 키워."

메모리 저장 형태:
(사용자) -[가족 관계]-> (여동생: 지수)
(지수)   -[반려동물 소유]-> (고양이: 나비)

후속 질문: "지수가 키우는 동물 이름이 뭐지?"
→ 대화 기록 전체가 아닌 그래프에서 '지수'와 연결된 '나비' 노드를 즉시 찾아 답변
```

**주요 장점**

1. **컨텍스트 윈도우 절약**: 과거 대화 전체를 프롬프트에 넣을 필요가 없어 토큰 비용 절약
2. **정확한 팩트 기억**: 인물·장소·사건 간 사실 관계를 그래프로 유지 → 할루시네이션 감소, 일관된 답변
3. **복잡한 정보 연결**: 파편적으로 제공된 정보를 연결하여 새로운 사실 추론

> 지식 그래프 + KG 메모리를 결합하면 사용자의 배경이나 복잡한 업무 지식을 이해·기억하는 맞춤형 AI 에이전트를 구축할 수 있다.
>
> ※ 참고: 최신 LangChain 버전에서는 `ConversationKGMemory` 등 기존 메모리 클래스가 deprecated 되는 추세이며, LangGraph의 상태/체크포인트 기반 메모리로 이동하고 있다.

---

## 4. LangGraph

LangChain 팀이 개발한 오픈소스 라이브러리. **상태 유지(Stateful)**, **루프(Loop)**, **다중 에이전트(Multi-Agent)** 구조를 갖춘 LLM 애플리케이션 구축용 프레임워크.

기존 체인이 단방향(DAG) 흐름에 적합했다면, LangGraph는 **반복 실행(Cycle)** 과 **전역 상태 관리(State)** 를 핵심으로 지원하여 자율형 AI 에이전트 제작에 최적화되어 있다.

### 핵심 요소

| 요소 | 설명 |
|---|---|
| **State** | 그래프 전체에서 공유되는 작업 데이터. 각 단계가 State를 읽고 업데이트 |
| **Node** | 실제 작업(LLM 호출, API 실행, 데이터 처리 함수 등) 수행 단위 |
| **Edge** | 노드 간 이동 경로. **조건부 엣지(Conditional Edge)** 로 LLM 판단에 따라 다음 노드를 동적으로 결정 |

### 주요 특징

- **순환 구조(Cyclic Flow)**: "계획 수립 → 실행 → 결과 평가 → 수정 및 재시도"를 목표 달성까지 반복
- **체크포인트(Checkpointing)**: 실행 중간 상태를 DB 등에 기록
- **Human-in-the-Loop**: 민감한 작업 전 일시 중단(Pause) → 사람의 승인/피드백으로 상태 수정 → 재개
- **타임 트래블(Time Travel)**: 이전 시점으로 상태를 되돌려 다른 입력으로 재실행하는 디버깅 기능
- **다중 에이전트(Multi-Agent)**: 정보 수집, 코드 작성, 검수 등 전문 에이전트들이 메시지를 주고받으며 협업

### LangChain(LCEL) vs LangGraph

| 구분 | LangChain (LCEL) | LangGraph |
|---|---|---|
| 흐름 구조 | 단방향 순차 흐름 (DAG) | 순환 구조(Cyclic Graph), 루프 가능 |
| 주요 사용처 | RAG, 데이터 변환 파이프라인 | 자율형 에이전트, 복잡한 판단 루프, Multi-Agent |
| 상태 관리 | 체인 단계를 거치며 인자 전달 | 전역 State 스키마 기반, 세밀한 체크포인트 |
| 제어력 | 높은 수준의 추상화 (빠른 개발) | 세밀한 제어 및 디버깅 가능 |

---

## 5. uv와 venv 함께 사용하기

`uv`는 venv를 대체하는 도구이면서, 기존 venv와 함께 쓸 수도 있다.

### 시나리오 1: uv가 venv를 대체 (권장)

```bash
# python -m venv .venv 대신
uv venv

# 가상환경 활성화 (동일)
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# pip install 대신
uv pip install requests
```

### 시나리오 2: 기존 venv 안에서 uv 사용

```bash
python -m venv .venv
source .venv/bin/activate
uv pip install requests     # 활성화된 가상환경을 자동 감지하여 설치
```

### 주의사항

1. **pip와 uv pip를 섞어 설치하지 말 것**: 의존성 해석(resolver) 방식이 달라 버전 충돌이 생길 수 있다. 한 프로젝트에서는 하나로 통일.
2. **uv.lock과 requirements.txt는 별개 시스템**
   - uv: `pyproject.toml` + `uv.lock` 기반 (`uv add`, `uv sync`)
   - venv + pip: 보통 `requirements.txt` 기반
   - 섞으면 무엇이 "진짜 소스"인지 헷갈린다.
3. **`uv venv`로 만든 환경에는 기본적으로 pip가 없음**: `uv pip install pip`로 설치하거나 계속 `uv pip install` 사용. (`uv venv --seed` 옵션으로 pip 포함 생성 가능)
4. **Python 버전 관리 차이**: uv는 자체적으로 인터프리터를 관리(`uv python install 3.12`)하므로, 시스템 Python/pyenv와 경로가 달라 IDE(VS Code 등)가 잘못된 인터프리터를 잡는 경우가 있다. 특히 WSL이나 여러 Python 버전이 공존하는 환경에서 주의.
5. **`.venv` 폴더 이름/위치는 호환됨**: `uv venv`도 `.venv`를 만들고 activate 방식도 동일.
6. **팀 작업 시 도구 통일**: README에 설치 방법을 명확히 적어 "내 환경에서는 되는데" 문제 예방.

> **요약**: 기술적으로는 섞어 쓸 수 있지만, **한 프로젝트 = 한 가지 도구**가 가장 편하다. 신규 프로젝트라면 `uv venv` + `uv pip` (또는 `uv add` / `uv sync`)로 통일 추천.

---

## 6. 이미 push한 커밋 되돌리기 (Git)

### 핵심 차이

| 방법 | 동작 | 사용처 |
|---|---|---|
| `git revert` | 기존 기록은 두고, **되돌리는 새 커밋을 추가** | 공유 브랜치 (가장 안전) |
| `git reset` + `git push --force-with-lease` | 원격에 올라간 커밋 자체를 **히스토리에서 제거** | 혼자 쓰는 브랜치 |

```
revert:           A -- B -- C  →  A -- B -- C -- Revert-C   (기록 보존)
reset + force:    A -- B -- C  →  A -- B                     (기록 재작성)
```

### 6.1 가장 안전한 방법: `git revert`

```bash
git log --oneline
# a82fd91 로그인 API 수정   ← 취소하고 싶은 커밋
# 79c21ab README 수정
# 3b4a881 프로젝트 초기 설정

git revert a82fd91
git push origin main
```

결과: `A --- B --- C --- D` (D = C를 취소하는 커밋)

revert는 커밋을 삭제하는 것이 아니라 **반대 변경사항을 새 커밋으로 만든다.**

```diff
# C 커밋의 변경
- timeout = 30
+ timeout = 60

# revert 커밋의 변경
- timeout = 60
+ timeout = 30
```

### 6.2 마지막 커밋을 기록에서 완전히 제거

```bash
git reset --hard HEAD~1                    # 로컬: A --- B
git push                                   # 거절됨 (rejected, non-fast-forward)
git push --force-with-lease origin main    # 원격도 A --- B
```

원격에는 C가 있는데 로컬에는 없으므로 일반 push는 거절된다.

### `--force` vs `--force-with-lease`

- `--force`: "원격 상태가 어떻든 내 로컬 기록으로 덮어써."
- `--force-with-lease`: "내가 마지막으로 확인한 원격 상태에서 아무도 변경하지 않았다면 덮어써."

동료가 그 사이 새 커밋 D를 push했다면 `--force`는 D까지 날려버리지만, `--force-with-lease`는 push를 거부한다. **항상 `--force-with-lease`를 우선 사용.**

### 6.3 reset 옵션 비교 (`--soft` / `--mixed` / `--hard`)

| 명령 | 커밋 | 파일 변경 | staging |
|---|---|---|---|
| `git reset --soft HEAD~1` | 삭제 | 유지 | 유지 |
| `git reset HEAD~1` (= `--mixed`, 기본값) | 삭제 | 유지 | 취소 |
| `git reset --hard HEAD~1` | 삭제 | **삭제** | 삭제 |

- `--soft`: 커밋 메시지를 잘못 썼거나 파일을 더 넣어 다시 커밋할 때 유용 (`git status` → `Changes to be committed`)
- `--mixed`: 수정 내용은 남고 `git add` 상태만 풀림 (`git status` → `Changes not staged for commit`)
- `--hard`: 작업 내용까지 사라지므로 확실하지 않으면 사용하지 말 것

### 6.4 여러 개의 push된 커밋 되돌리기 (공유 브랜치)

`A --- B --- C --- D --- E`에서 C, D, E를 취소하여 B 상태로 돌아가려면:

```bash
git revert B..E          # B는 제외, C·D·E를 revert (= C^..E)
git revert HEAD~3..HEAD  # 최근 3개 커밋
```

> ⚠️ 범위 표기 `X..Y`는 **X를 포함하지 않는다.** `git revert C..E`는 D, E만 되돌린다.

헷갈리면 하나씩 명시하는 것이 더 명확하다 (최신 커밋부터).

```bash
git revert e123456
git revert d123456
git revert c123456
git push
```

### 6.5 여러 커밋을 기록에서 완전히 삭제 (개인 브랜치)

```bash
git reset --hard 79c21ab                   # B의 커밋 해시
git push --force-with-lease origin main    # 결과: A --- B
```

### 6.6 커밋은 취소하되 작업 내용은 다시 수정

```bash
git reset --soft HEAD~1      # 또는 git reset HEAD~1
# 코드 수정
git add .
git commit -m "올바른 커밋"
git push --force-with-lease
```

결과: `A --- B --- C` → `A --- B --- C'`

C와 C'는 내용이 비슷해도 **서로 다른 커밋**이다. 내용·부모·메시지 등이 바뀌면 커밋 해시도 달라진다.

### 6.7 특정 파일만 되돌리기

```bash
git restore --source=HEAD~1 README.md
git add README.md
git commit -m "README 변경 되돌리기"
git push
```

기존 히스토리를 건드리지 않는다.

### 6.8 실수로 `reset --hard` 했을 때: `git reflog`

```bash
git reflog
# 79c21ab HEAD@{0}: reset: moving to HEAD~3
# fa891bc HEAD@{1}: commit: 로그인 기능 완료
# d82193a HEAD@{2}: commit: API 수정

git reset --hard fa891bc     # 원래 HEAD로 복구
```

### 실무 판단 기준

| 상황 | 방법 |
|---|---|
| main에 잘못 push | `git revert` |
| 여러 사람이 쓰는 브랜치 | `git revert` |
| PR이 이미 merge됨 | `git revert` |
| 내 개인 feature 브랜치 | `git reset` 가능 |
| 마지막 커밋만 다시 만들고 싶음 | `git reset --soft HEAD~1` |
| 커밋도 코드 변경도 전부 버림 | `git reset --hard HEAD~1` |
| push된 기록 자체를 변경 | `git push --force-with-lease` |
| 실수로 reset함 | `git reflog` |

> **핵심 원칙**: 공유된 Git 히스토리를 다시 쓰느냐?
> - main/develop 등 공유 브랜치 → `git revert <commit>` + `git push`
> - 아무도 안 쓰는 개인 feature 브랜치 → `reset --soft` → 수정 → commit → `push --force-with-lease`

---

## 7. DevOps 개요

**DevOps = Development(개발) + Operations(운영)**

개발한 서비스를 더 빠르고 안정적으로 배포·운영하기 위해 개발팀과 운영팀이 협업하는 **문화와 방법론**, 그리고 이를 위한 **자동화 기술**.

- 과거: 개발자가 코드를 만든 뒤 운영팀에 "서버에 올려주세요"라고 넘김
- DevOps: 코드가 Git에 올라가는 순간 **테스트 → 빌드 → 배포**가 자동 진행. 장애 시 모니터링 시스템이 즉시 알리고, 필요하면 서버가 자동으로 확장(오토스케일링)

### CI/CD

- **CI (Continuous Integration)**: 코드를 올릴 때 자동으로 테스트하고 통합
- **CD (Continuous Delivery/Deployment)**: 테스트를 통과한 코드를 개발·스테이징·운영 서버에 자동 배포

### 주요 기술 스택

| 분야 | 도구 |
|---|---|
| 코드 관리 | Git / GitHub / GitLab |
| CI/CD 자동화 | Jenkins / GitHub Actions / GitLab CI |
| 컨테이너 | Docker |
| 컨테이너 오케스트레이션 | Kubernetes |
| 클라우드 인프라 | AWS / Azure / GCP |
| IaC (Infrastructure as Code) | Terraform |
| 모니터링 | Prometheus / Grafana |

> **DevOps 엔지니어**: 개발자가 만든 코드가 안전하게 서버까지 가고, 서비스가 계속 안정적으로 돌아가도록 시스템을 자동화하는 사람. 원래 DevOps는 직업명보다는 문화·방법론에 가까운 개념이다.
