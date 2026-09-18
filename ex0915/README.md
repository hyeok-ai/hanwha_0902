# 9월 15일 수업 정리

---

## 1. LLM Tool Calling의 신뢰성

### 보장 층위

| 층위 | 내용 | 보장 가능 여부 |
|---|---|---|
| 문법 | JSON 문법이 깨지지 않음 | 가능 (constrained decoding) |
| 스키마 | 정의된 키/타입만 출력 | 가능 (동일 메커니즘) |
| 의미 | 맞는 툴, 맞는 타이밍, 맞는 값 | 불가능 |

- 파서 오류 방지는 공학적으로 해결됨
- `city="Seoul"` 대신 `city="Busan"`을 넣는 것은 막을 수 없음

### 과거 방식: ReAct (툴 학습 이전 모델)

- 프롬프트로 포맷을 가르치고 정규식으로 추출
- LangChain 초창기 방식

```text
Answer the following questions as best you can. You have access to the following tools:
get_weather: 도시의 현재 날씨를 조회한다. args: city (string)

Use the following format:
Question: the input question
Thought: you should always think about what to do
Action: the action to take, should be one of [get_weather]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer

Question: 서울 날씨 알려줘
Thought:
```

- 모델은 텍스트를 이어서 생성할 뿐
- 프레임워크가 `Action:` / `Action Input:`을 정규식으로 잘라냄
- `Observation:`을 stop sequence로 설정 → 툴 실행 결과를 붙여 프롬프트 전체 재전송

**자주 발생한 파싱 실패 예**

```text
Action: get_weather(city="Seoul")              ← 함수 호출 문법으로 작성
Action: I should use get_weather               ← 툴 이름 대신 문장 작성
Action Input: ```json\n{"city":"Seoul"}```     ← 마크다운 펜스 삽입
Thought: I now know the final answer
Action: get_weather                            ← Final Answer와 Action 동시 출력
```

- 결과: `OutputParserException` 빈발
- 임시 대응책
  - `handle_parsing_errors=True`: 에러 문구를 모델에 다시 넣어 재시도
  - `OutputFixingParser`: 깨진 출력을 다른 LLM 호출로 수정
- 파인튜닝 안 된 모델은 실패율 수십 %, 작은 오픈소스 모델은 사실상 사용 불가

### 현재 방식의 변화

#### (1) 파인튜닝 — 학습된 행동

- 툴 호출 궤적 데이터로 별도 학습한 결과
- OpenAI function calling(2023.06)도 "이 기능을 위해 파인튜닝된 새 모델"로 발표
- 학습 안 된 체크포인트에 `tools` 파라미터를 넣으면 무시하거나 이상한 출력

#### (2) 특수 토큰 — 채널 분리

- 툴 호출이 일반 텍스트와 다른 토큰 공간 사용

```text
# Qwen 계열
<tool_call>
{"name": "get_weather", "arguments": {"city": "Seoul"}}
</tool_call>

# Llama 3.1 계열
<|python_tag|>{"name": "get_weather", "parameters": {"city": "Seoul"}}<|eom_id|>
```

- `<|eom_id|>`(end of message) ≠ `<|eot_id|>`(end of turn)
  - "턴 종료"가 아닌 "툴 결과 대기" 상태를 명시적으로 표현
- 평문 `Action:`에 의존하던 ReAct와 근본적으로 다름
- API 레이어가 해당 토큰 구간을 파싱해 `tool_calls` 필드로 제공

#### (3) Constrained Decoding — 문법 층위의 실제 보장

- OpenAI structured outputs(`strict: true`)
  - JSON Schema → 문맥 자유 문법(CFG)으로 컴파일
  - 디코딩 매 스텝마다 문법상 불가능한 토큰의 logit을 `-inf`로 마스킹

```text
현재까지 생성: {"city": "Seoul"
문법상 가능한 다음 토큰: , 또는 }
→ 나머지 vocabulary는 확률 0
```

- 오타 키(`"cityy"`) 샘플링 불가, 중괄호 미닫힘 종료 불가
- 문법·스키마 위반은 원리적으로 0

```python
llm = ChatOpenAI(model="gpt-4o").bind_tools([get_weather], strict=True)
```

**제약 사항**

- 스키마 서브셋만 지원
  - 모든 프로퍼티가 `required`
  - `additionalProperties: false` 필요
  - 선택 인자는 `Optional[str]` 같은 null 유니온으로 표현
- 새 스키마 첫 호출 시 문법 컴파일 지연 (이후 캐시)
- 병렬 호출과 함께 쓰면 엄격성 완전 보장 안 됨 → `parallel_tool_calls=False` 권장
- 오픈 모델: vLLM(`guided_json`), llama.cpp(GBNF), Outlines 등으로 동일 기능

### 여전히 보장 안 되는 것 (의미 층위)

- **인자 환각**: 사용자가 말하지 않은 값(`"Seoul"`)을 지어냄
  - strict 모드는 모든 필드가 필수 → 빈칸 채우기 압력으로 악화 가능
  - 선택 인자는 반드시 nullable로 열어둘 것
- **툴 미호출**: 호출해야 할 상황에서 아는 척 답변
- **불필요 호출**: "안녕"에도 검색 툴 호출
- **잘못된 툴 선택**: 툴 5개 vs 50개 정확도 차이 큼, 이름/설명 유사하면 급격히 악화
- **무한 루프**: 같은 툴을 같은 인자로 반복 호출
- **타입은 맞지만 값이 틀림**: `date: "2026-13-45"`도 스키마상 valid string
- **생성 중단**: `finish_reason: "length"`로 JSON 잘림, strict 모드로도 못 막음

### 실무 방어선

#### 1차: Pydantic 검증 + 에러 피드백 루프

- 모델은 자기 에러를 보여주면 잘 고침

```python
from pydantic import BaseModel, Field, field_validator
from langchain_core.tools import tool, ToolException

class WeatherArgs(BaseModel):
    city: str = Field(description="도시 이름 (영문)")
    unit: str = Field(default="celsius")

    @field_validator("unit")
    @classmethod
    def check_unit(cls, v):
        if v not in ("celsius", "fahrenheit"):
            raise ValueError(f"unit must be celsius or fahrenheit, got {v!r}")
        return v

@tool(args_schema=WeatherArgs)
def get_weather(city: str, unit: str = "celsius") -> str:
    """도시의 현재 날씨를 조회한다."""
    ...
```

- 핵심: 검증 실패를 예외로 터뜨리지 말고 `ToolMessage`로 반환

```python
for tc in ai_msg.tool_calls:
    try:
        result = tools_by_name[tc["name"]].invoke(tc["args"])
    except KeyError:
        result = f"Error: '{tc['name']}' is not a valid tool. Available: {list(tools_by_name)}"
    except Exception as e:
        result = f"Error: {e}. Please fix the arguments and retry."
    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
```

- LangGraph: `ToolNode(tools, handle_tool_errors=True)`가 동일 역할

#### 설계 차원

- `invalid_tool_calls` 필드 반드시 확인 (조용히 무시되면 디버깅 어려움)
- 반복 횟수 상한(`recursion_limit`)으로 루프 차단
- 반드시 호출해야 하면 `tool_choice="required"` 또는 특정 툴 강제
- 툴 개수 축소 / 라우터로 후보 좁히기 / 설명문 정교화 → 모델 교체보다 효과 큰 경우 많음
- 삭제·결제 등 비가역 동작은 human-in-the-loop 승인 단계
- 툴 호출 정확도 평가셋 별도 구축 → 회귀 감시

### 요약

- 문법 신뢰성: constrained decoding으로 원리적 해결
- 의미 신뢰성: 여전히 확률적 → 검증·재시도·권한 제한으로 보완
- "파서 오류" 문제는 사라졌고 "모델의 잘못된 판단" 문제는 남음 → 에이전트 안정성의 본질적 병목

---

## 2. ChatPromptTemplate 메시지 role

### 튜플 축약 문법의 role은 고정

```python
ChatPromptTemplate.from_messages([
    ("system", "..."),              # SystemMessage
    ("human", "..."),               # HumanMessage ("user"도 동일)
    ("ai", "..."),                  # AIMessage ("assistant"도 동일)
    ("placeholder", "{history}"),   # MessagesPlaceholder
])
```

- 그 외 값(`("referee", "...")`) → `_create_template_from_message_type()`에서 `ValueError` ("Unexpected message type")

### 우회: ChatMessagePromptTemplate

- 챗 모델이 임의 role 메시지를 지원하는 경우에 한해 사용 가능

```python
from langchain_core.prompts import ChatMessagePromptTemplate

tmpl = ChatMessagePromptTemplate.from_template(
    role="Jedi", template="May the {subject} be with you"
)
# -> ChatMessage(content='May the force be with you', role='Jedi')
```

### 실제로는 거의 사용 불가

- LangChain은 프롬프트 객체만 생성, HTTP 요청은 provider 통합 패키지(`langchain-openai`, `langchain-anthropic` 등)가 생성
- OpenAI·Anthropic·Gemini 등 주요 API는 `system` / `user` / `assistant` / `tool` 정도만 허용
- `ChatMessage(role="Jedi")` → 변환 단계 에러 또는 `user`로 뭉개짐
- 결론: 허용 role은 프레임워크가 아닌 **모델 API가 결정**

### 화자를 여러 명 두는 방법

1. **`name` 필드** — 메시지 클래스의 선택 속성, OpenAI 지원

   ```python
   HumanMessage(content="이 안건 반대합니다", name="reviewer_a")
   ```

2. **content 안에 라벨** — 가장 확실, provider 무관

   ```python
   ("human", "[심판] 지금까지의 논쟁을 정리해줘:\n{debate_log}")
   ```

   - 역할 구분을 role 슬롯이 아닌 텍스트 규약으로 처리
   - 실무에서 주로 사용, provider 교체해도 안 깨짐

---

## 3. RunnableParallel

```python
combined = RunnableParallel(capital=chain1, area=chain2)
```

- **키 이름** (`capital`, `area`): 결과 딕셔너리의 키, 자유롭게 지정
- **값** (`chain1`, `chain2`): 실행할 Runnable (체인, 프롬프트, 모델, 함수 등)

### 동작

1. `combined.invoke(입력)` → 같은 입력이 각 체인에 전달
2. 체인들이 병렬 실행
3. 결과를 지정한 키로 묶은 딕셔너리 반환

```python
result = combined.invoke({"country": "대한민국"})
# {'capital': '서울입니다...', 'area': '약 100,210㎢입니다...'}
result["capital"]   # chain1 결과
result["area"]      # chain2 결과
```

### 기타

- 딕셔너리로 전달해도 동일

  ```python
  combined = RunnableParallel({"capital": chain1, "area": chain2})
  ```

- 체인 안의 딕셔너리는 자동으로 `RunnableParallel`로 변환

  ```python
  chain = {"capital": chain1, "area": chain2} | 다음_프롬프트
  ```

  - 다음 프롬프트에서 `{capital}`, `{area}`로 결과 사용 → 여러 결과 결합 시 활용
- 키 이름 오타 주의: 정의한 키와 다른 이름으로 접근하면 `KeyError`

---

## 4. PromptTemplate 입력 자동 변환

### `chain.invoke(5)`가 동작하는 이유

- 정석: `chain.invoke({"num": 5})`
- `langchain-core`의 `_validate_input` 로직
  - 입력이 dict가 아니고
  - 프롬프트 입력 변수가 1개이면
  - 자동으로 `{"num": 5}`로 감쌈

### 주의점

- 구버전에서는 에러: `TypeError: Expected mapping type as input to PromptTemplate`
- 변수가 2개 이상이면 여전히 에러

  ```python
  prompt = PromptTemplate.from_template("{num}의 {times}배는?")
  chain.invoke(5)   # 에러: 어느 변수에 넣을지 알 수 없음
  ```

### 명시적 방식: RunnablePassthrough

```python
chain = {"num": RunnablePassthrough()} | prompt | llm
chain.invoke(5)
```

- "입력값을 그대로 `num` 키에 넣음"이 명시적으로 드러남
- RAG 패턴으로 확장: `{"context": retriever, "question": RunnablePassthrough()}`
- 자동 변환에 의존하지 말고 dict 전달 또는 `RunnablePassthrough` 사용 권장

```python
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
```

---

## 5. pip 설치 시 버전 선택 과정

### 1) 인덱스 조회

- 설치 시마다 PyPI Simple API(`https://pypi.org/simple/<패키지>/`)에서 전체 배포 파일 목록 조회
- 별도 업데이트 명령 없이 항상 최신 목록 기준

### 2) 후보 필터링

- **Requires-Python**: 현재 Python 버전 미지원 릴리스 제외
- **wheel 태그**: 플랫폼(`win_amd64`, `cp312` 등) 불일치 wheel 제외 (`py3-none-any`는 순수 파이썬 → 모든 플랫폼 가능)
- **yanked 릴리스**: 버전 미지정 시 철회된 버전 제외
- **프리릴리스**: `--pre` 없으면 알파/베타(`a1`, `b1` 등) 제외

### 3) 버전 정렬 (PEP 440)

- 업로드 날짜가 아닌 **버전 번호** 기준 정렬
- 예: 구버전 계열(0.3.x)에 최근 보안 패치가 올라와도 1.x보다 번호가 낮아 선택 안 됨

### 4) 의존성 해석 (resolver)

- pip 20.3+ 백트래킹 resolver (resolvelib 기반)
- 가장 높은 버전부터 시도 → 의존성 조합이 맞으면 확정, 충돌 시 한 단계 낮춰 재시도
- 기존 설치 패키지: 기본 upgrade 전략 `only-if-needed`
  - 요구 범위 만족 → 유지
  - 불만족 → 업그레이드
- `requirements.txt`의 `==` 고정은 파일 내용일 뿐, 설치 상태에는 강제력 없음

### requirements.txt는 자동 적용 안 됨

```bash
pip install langchain -r requirements.txt   # == 고정이 요구사항으로 포함
pip install langchain -c requirements.txt   # 제약(constraints)으로만 사용
```

- 제약과 충돌 시 resolver가 더 낮은 버전으로 백트래킹
- 만족하는 버전이 없으면 `ResolutionImpossible`
- 최신이 설치되지 않는 가장 흔한 원인

### 기타 최신 미설치 원인

- **HTTP 캐시**: 인덱스 응답이 몇 분 캐시 → 방금 올라온 릴리스 미노출
- **다른 인덱스**: `pip.ini` / `PIP_INDEX_URL`로 사내 미러 사용 시 미러 동기화 상태에 의존
- **옵션**: `--only-binary`, `--no-deps` 등

### 사전 확인

```bash
python -m pip index versions langchain
python -m pip install langchain --dry-run
```

- `--dry-run`: 실제 설치 없이 "Would install ..." 목록 출력
- 업그레이드 대상에 핵심 의존성이 있으면 `-c requirements.txt` 사용 여부 판단
- langchain 1.x는 에이전트 기능이 LangGraph 기반 → langgraph 패키지 함께 설치

---

## 6. RAG 8단계 파이프라인

```text
[LOAD] → [SPLIT] → [EMBED] → [STORE] → [RETRIEVER] → [PROMPT] → [LLM]
                        (전체 흐름 연결: CHAIN)
```

| 단계 | 의미 | 역할 |
|---|---|---|
| 1. LOAD | PDF, 웹, Word, TXT, CSV 등 외부 문서 로드 (Document Loader) | 모델이 학습하지 않은 외부/사내 데이터 확보 |
| 2. SPLIT | 긴 문서를 작은 청크로 분할 (Text Splitter) | 검색 정확도 향상, Context Window 초과 방지 |
| 3. EMBED | 청크를 실수 벡터로 변환 (Embedding Model) | 키워드 매칭이 아닌 의미 기반 검색 가능 |
| 4. STORE | 벡터 DB(Chroma, FAISS, Pinecone 등)에 저장 (Vector Store) | 빠른 조회를 위한 인덱스 구성 |
| 5. RETRIEVER | 질문과 의미상 가장 유사한 청크 검색 | 필요한 관련 정보만 추출 |
| 6. PROMPT | 검색 문맥 + 원본 질문 결합 (Prompt Template) | "검색 결과를 참고해 답변" 지시로 환각 억제 |
| 7. LLM | GPT, Claude, Llama 등으로 답변 생성 | 검색 정보 기반 자연어 답변 작성 |
| 8. CHAIN | 1~7단계를 하나의 워크플로우로 결합 (LangChain / LCEL) | 질문 입력 → 검색 → 답변까지 자동화 |

---

## 7. Jupyter 커널과 상태 유지

- 상태(변수, import 모듈, 로드 데이터)는 `.ipynb` 파일이 아닌 **커널 프로세스 메모리**에 존재
- 커널이 살아 있는 동안만 유지

### 유지되는 경우

- 브라우저 탭 닫기 (커널은 계속 실행)
- 다른 노트북으로 이동 후 복귀

### 사라지는 경우

- Restart Kernel
- Shutdown Kernel 또는 Jupyter 서버 종료
- 컴퓨터 종료/재부팅
- 메모리 부족 등으로 커널 종료 ("Kernel died")
- 유휴 시간 자동 종료
  - 로컬: 기본 제한 없음
  - JupyterHub/기관 서버: idle culling 설정 가능
  - Google Colab: 약 90분 비활성 또는 최대 약 12시간(무료) 후 런타임 종료

### 혼동 주의

- 노트북 저장 시 셀 코드와 **출력 결과**는 파일에 남음
- **변수는 저장 안 됨** → 재오픈 후 출력은 보이지만 변수 사용 시 `NameError`
- 셀을 처음부터 재실행 필요

### 결과 보존 방법

- `pickle`, `joblib`, `df.to_parquet()` / `to_csv()`로 파일 저장
- IPython 매직: `%store 변수명` → 재시작 후 `%store -r`로 복원

---

## 8. LangSmith

- LangChain 팀의 LLM 애플리케이션 개발·운영 플랫폼
- 프로토타입 → 프로덕션 수준 전환 과정의 문제 해결 목적

### 주요 기능

1. **트레이싱/디버깅 (Observability)**
   - 프롬프트, 체인, 에이전트, 도구 호출, RAG 등 각 단계의 입력·출력·지연·토큰·비용 기록 및 시각화
   - 잘못된 도구 호출 원인, 답변을 망친 검색 결과 추적
2. **평가 (Evaluation)**
   - 데이터셋 기반으로 프롬프트/모델 변경 전후 품질 비교
   - 정답 비교, 사용자 정의 평가 함수, LLM-as-a-judge, 사람 피드백 지원
3. **프롬프트 관리/실험**
   - 프롬프트 버전 관리, 플레이그라운드에서 모델·설정별 테스트
4. **프로덕션 모니터링**
   - 오류율, 지연, 비용, 사용자 피드백 대시보드
   - 실제 트래픽의 문제 사례를 평가 데이터셋에 추가 → 개선 루프

### 기타

- LangChain/LangGraph 없이도 사용 가능 (OpenAI SDK, 직접 작성 코드)
- 유사 도구: Langfuse, Arize Phoenix, W&B Weave

---

## 9. langchain-classic

- LangChain v1.0 전환 시 기존 `langchain`에서 분리한 **레거시 호환성 패키지**
- 핵심 `langchain`은 현대적 에이전트 개발 필수 요소에만 집중
- 새 프로젝트는 langchain v1 사용 권장

### 패키지 구성

**langchain (v1)**

- `langchain.agents` (`create_agent`, `AgentState`)
- `langchain.messages` (메시지 타입, content blocks)
- `langchain.tools` (`@tool`, `BaseTool`)
- `langchain.chat_models` (`init_chat_model`)
- `langchain.embeddings`

**langchain-classic**

- 레거시 체인: `LLMChain`, `ConversationChain` 등
- 기존 retrievers: `MultiQueryRetriever` 등
- 인덱싱 API, `hub` 모듈
- `CacheBackedEmbeddings` 등 임베딩 모듈
- `langchain-community` 재수출, 기타 deprecated 기능

### 마이그레이션 코드

```python
# pip install langchain-classic

# 이전 (v0.x)
from langchain.chains import LLMChain
from langchain.retrievers import MultiQueryRetriever
from langchain import hub

# v1 이후
from langchain_classic.chains import LLMChain
from langchain_classic.retrievers import MultiQueryRetriever
from langchain_classic import hub
```

- JavaScript: `langchain/chains` → `@langchain/classic/chains`

### 설계 철학 차이

| v0.x | v1 |
|---|---|
| 체인, 다양한 에이전트, 여러 retriever 등 폭넓은 패턴 | `create_agent`를 표준 에이전트 생성 방식으로 |
| `langgraph.prebuilt.create_react_agent` 권장 | `langchain.agents.create_agent` 권장 |
| — | provider 간 일관된 `content_blocks` |
| — | 구조화 출력, 미들웨어(승인, PII 마스킹 등) |

- 업그레이드 시 Python 3.10+ 필요

### 정리

- 기존 v0.x 코드(`LLMChain`, `RetrievalQA` 등) 유지보수 → `langchain-classic` 설치 + import 경로 변경
- 신규 프로젝트 → v1 `create_agent` + LCEL/LangGraph 기반

---

## 10. with_structured_output 작동 원리

### 전체 흐름

```text
Pydantic 클래스 ──(스키마 변환)──▶ JSON Schema
        │
        ▼
llm.bind_tools(...) 또는 llm.bind(response_format=...)   ← 호출 방식 결정
        │
        ▼
Provider API (OpenAI / Anthropic / Gemini ...)           ← 서버 측 제약/강제
        │
        ▼
모델 토큰 생성 (tool call 또는 JSON 텍스트)
        │
        ▼
Output Parser → Pydantic 검증 → EmailSummary 인스턴스
```

- provider SDK·LangChain 버전별 세부 동작이 계속 바뀜 → 설치 버전 문서 확인

### 1) 인터페이스 층위: 문자열 대신 객체를 반환하는 Runnable

- `llm.with_structured_output(EmailSummary)`는 모델을 바꾸지 않음
- 모델 호출 + 파싱을 묶은 새 Runnable 반환
- `chain.invoke(...)` 결과는 `AIMessage`가 아닌 `EmailSummary` 인스턴스

```python
result = chain.invoke({"question": "...", "email_conversation": "..."})
result.person   # "김철수"
result.date     # "2026년 9월 20일 오후 3시"
```

- `prompt | structured_llm` 형태로 일반 LLM과 동일하게 조합

### 2) LangChain 내부 층위: 바인딩 + 파서

```python
# OpenAI 계열 기준 단순화한 의사코드
def with_structured_output(self, schema, method=..., include_raw=False, strict=None):
    if method == "function_calling":
        tool = convert_to_openai_tool(schema)                  # Pydantic → tool 정의
        llm = self.bind_tools([tool], tool_choice=tool_name)   # 해당 도구 호출 강제
        parser = PydanticToolsParser(tools=[schema], first_tool_only=True)
    elif method == "json_schema":
        llm = self.bind(response_format={... JSON Schema ..., "strict": True})
        parser = PydanticOutputParser 계열
    elif method == "json_mode":
        llm = self.bind(response_format={"type": "json_object"})
        parser = JSON 파싱 후 Pydantic 변환
    return llm | parser   # RunnableSequence
```

- **method별 전략 차이**
  - 최근 `langchain-openai` 기본값: 네이티브 structured output인 `json_schema` (과거 `function_calling`)
  - `ChatAnthropic`: 전통적으로 tool calling 강제 방식, 네이티브 structured outputs 도입 후 선택 가능
- **반환은 `llm | parser` 시퀀스** → 스트리밍, 배치, 콜백, 트레이싱 모두 동작
- **`include_raw=True`** → 예외 대신 `{"raw": AIMessage, "parsed": EmailSummary | None, "parsing_error": ...}` 반환 (디버깅·재시도 로직에 유용)

### 3) 스키마 변환 층위: Pydantic 정의 = 프롬프트

```json
{
  "name": "EmailSummary",
  "description": "이메일에서 추출한 핵심 정보",
  "parameters": {
    "type": "object",
    "properties": {
      "person":  {"type": "string", "description": "메일을 보낸 사람"},
      "email":   {"type": "string", "description": "메일을 보낸 사람의 이메일 주소"},
      "subject": {"type": "string", "description": "메일 제목"},
      "summary": {"type": "string", "description": "메일 본문을 요약한 텍스트"},
      "date":    {"type": "string", "description": "메일 본문에 언급된 미팅 날짜와 시간"}
    },
    "required": ["person", "email", "subject", "summary", "date"]
  }
}
```

| Pydantic | JSON Schema / Tool |
|---|---|
| 클래스 이름 | 도구 이름 |
| docstring | 도구 설명 |
| `Field(description=...)` | 필드 설명 |

- 설명문은 주석이 아닌 **모델이 읽는 지시문**
- 추출 품질 개선 시 시스템 프롬프트보다 필드 설명을 먼저 다듬는 편이 효과적 (예: "YYYY-MM-DD HH:MM 형식")
- 기본값 없는 필드는 모두 `required`

### 4) Provider API 층위: 보장 수준

| 방식 | 요청 형태 | 보장 수준 |
|---|---|---|
| Tool/Function calling | `tools` + `tool_choice` | strict 없으면 대부분 준수, 100% 보장 아님 |
| JSON Schema (strict) | `response_format` + `strict: true` | 스키마 준수 보장, 단 스키마 제약 있음 |
| JSON mode | `{"type": "json_object"}` | 유효한 JSON만 보장, 스키마 준수 미보장 (비권장) |

- OpenAI strict 제약: 모든 필드 required, `additionalProperties: false`, 일부 JSON Schema 키워드 미지원

### 5) 모델/디코딩 층위: 토큰 강제 방식

- **학습된 행동**: tool calling 형식으로 파인튜닝 → 스키마·설명을 확률적으로 따름, 드물게 틀림
- **제약 디코딩**: strict 모드에서 JSON Schema → 문법(상태 기계) 컴파일 → 매 토큰마다 불가능한 토큰 확률 0으로 마스킹
  - 예: `{"person":` 다음에는 따옴표로 시작하는 문자열 토큰만 허용
  - 구조적으로 틀린 출력 원천 차단
- 보장은 **형식**까지, **내용 정확성**은 미보장 (email 필드가 실제 발신자 주소인지는 모름)

### 6) 검증 층위와 실무 포인트

- 파서 → `EmailSummary(**args)` Pydantic 검증
- 타입 불일치/필드 누락 → `OutputParserException` 또는 `ValidationError` (`include_raw=True`면 `parsing_error`에 저장)

**date 필드 환각 위험**

- 전 필드 required → 메일에 일정이 없어도 날짜를 지어내거나 "없음" 등 임의 문자열 삽입
- null 허용으로 해결

```python
from typing import Optional

date: Optional[str] = Field(
    description="메일 본문에 언급된 미팅 날짜와 시간. 언급이 없으면 null"
)
```

- strict 모드에서는 기본값(`= None`)보다 "required이지만 nullable" 형태가 호환성 좋음

**언어 지시의 적용 범위**

- 시스템 프롬프트의 "KOREAN" 지시는 **값(value)**에만 영향
- 키 이름(`person`, `email` 등)은 스키마로 고정
- 이름 등 원문 유지가 필요하면 필드 설명에 "원문 표기 그대로" 명시

**question 변수의 역할**

- 출력 형태는 스키마로 고정 → `question`은 추출 방식 보조 지시 역할
- 스키마와 어긋나는 요청("답장 초안 작성")은 억지로 스키마에 끼워 맞춰짐

**LangChain 1.0 에이전트**

- `create_agent`의 `response_format` (`ToolStrategy` / `ProviderStrategy`)도 동일 원리
- 도구 방식 vs provider 네이티브 방식 선택 구조

### 요약

- `with_structured_output` = Pydantic 스키마를 provider별 강제 메커니즘(tool calling 또는 JSON Schema 제약 디코딩)으로 번역 → 응답을 Pydantic 객체로 파싱·검증하는 어댑터
- 형식 보장은 점점 강해짐, 내용 정확성은 필드 설명과 프롬프트 설계에 의존
