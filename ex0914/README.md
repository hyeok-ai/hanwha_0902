# 수업 정리 (9월 14일)

## 1. 데이터 기초

### 자료형
- 원시 자료형(primitive): 정수, 실수, 문자열, 불리언
- 컬렉션 자료형: 리스트(순서 있는 가변 시퀀스), 딕셔너리(key-value 매핑)
- 값의 흐름(데이터가 어디서 생성되어 어떻게 변형·전달되는지)을 추적할 수 있어야 코드 해석 가능

### 필드와 데이터 타입
- 테이블의 각 필드는 고유한 특성을 가지며, 특성에 맞는 타입 지정 필요

| 필드 | 적절한 타입 | 비고 |
|---|---|---|
| 번호(ID) | 정수(int) | 연속·정렬 가능 |
| 이름 | 문자열(str) | |
| 전화번호 | 문자열(str) | 앞자리 0 보존, 하이픈 포함 가능 → 숫자형 부적절 |

### 라이브러리별 자료구조
- **Pandas**: DataFrame / Series — 열(column) 단위로 서로 다른 타입 혼합 가능, 라벨 기반 인덱싱
- **NumPy**: ndarray(배열) — 동일 타입 고정, 수치 연산·브로드캐스팅에 최적화
- 도구 선택 기준: 데이터를 바라보는 시선(구조)과 용도(연산 vs 분석·가공)

### 시각화
- 그래프의 형태를 보고 무엇을 표현하려는 그래프인지 판단할 수 있어야 함
- 예: 추세(선), 범주 간 비교(막대), 두 변수 관계(산점도), 분포(히스토그램)

---

## 2. 웹 애플리케이션 구조

### Streamlit + FastAPI 연동
- 프론트엔드: Streamlit — 입력 위젯, submit 버튼
- 백엔드: FastAPI — CRUD 엔드포인트

### 동작 흐름
1. 화면에서 값 입력 후 submit
2. 프론트엔드가 백엔드 API로 HTTP 요청 전송
3. 백엔드 코드가 순차 실행되어 데이터 처리
4. 응답이 프론트엔드로 반환되어 화면 갱신

### CRUD ↔ HTTP 메서드 대응
| 동작 | 메서드 |
|---|---|
| Create | POST |
| Read | GET |
| Update | PUT / PATCH |
| Delete | DELETE |

- 생성뿐 아니라 조회(GET)도 함께 사용됨 — 메서드별 역할 구분 필요
- 참고 코드: `https://github.com/skc4365/hanwha_0902/tree/main/ex0910_all`

---

## 3. LLM 핵심 개념

### 프롬프트(Prompt)
- 모델에게 전달하는 입력 텍스트 전체 — 지시문, 역할 설정, 제약 조건, 예시 포함
- 프롬프트 엔지니어링: 지시문의 표현을 다듬어 원하는 출력을 얻는 작업

### 컨텍스트(Context)
- 모델이 답변을 생성할 때 참고하는 자료 및 대화 이력 전체
- 컨텍스트 윈도우: 한 번에 모델에 넣을 수 있는 토큰 한계
- 컨텍스트 엔지니어링: 특정 시점에 윈도우 안에 무엇을 넣을지 설계하는 작업

### 프롬프트 인젝션(Prompt Injection)
- 외부 입력(사용자 입력, 웹페이지, 문서)에 악의적 지시를 섞어 원래 시스템 지시를 덮어쓰는 공격

**예방 방법**
- 입력 검증 및 필터링 — 지시형 문구 탐지·제거
- 시스템 지시와 사용자 데이터 영역 분리, 구분자(delimiter)로 명시
- 출력 검증 — 모델 응답을 그대로 실행·렌더링하지 않음
- 최소 권한 원칙 — 위험한 도구는 제한적으로만 노출
- 민감 작업에 사람 승인(human-in-the-loop) 절차 삽입
- 외부에서 가져온 텍스트는 항상 '데이터'로 취급, '명령'으로 취급하지 않음

---

## 4. 하네스 엔지니어링 (Harness Engineering)

### 정의
- 어원: 소프트웨어 테스트 하네스, 평가 하네스(eval harness)
- AI 에이전트 맥락 — 모델 가중치 바깥에 있는 모든 실행 계층
- 원칙, 규칙, 사용 방법 등을 묶어서 지칭
- 같은 모델이라도 하네스 구성에 따라 에이전트 성능이 크게 달라짐

### 구성 요소
- **에이전트 루프**: 모델 호출 → 도구 실행 → 결과 반환 → 재호출. 종료 조건, 최대 턴 수, 재시도 정책
- **도구 표면(tool surface)**: 도구 개수, 설명 작성 방식, 입출력 포맷, 에러 메시지 문구
- **컨텍스트 관리**: 압축(compaction), 요약, 파일 기반 외부 메모리, 검색, 윈도우 예산 배분
- **실행 환경**: 샌드박스, 파일시스템, 네트워크 권한, 상태 복원, 재현성
- **피드백 루프**: 테스트, 린터, 컴파일러, 검증기 등 객관적 근거를 되돌려주는 장치
- **오케스트레이션**: 서브에이전트, 병렬 실행, 작업 분해와 핸드오프
- **관측과 평가**: 트레이싱, 리플레이, 회귀 테스트 스위트
- **안전 장치**: 권한 승인, 허용목록, 사람 개입 지점, 롤백

### 계층 비교
| 구분 | 다루는 범위 |
|---|---|
| 프롬프트 엔지니어링 | 지시문의 표현 |
| 컨텍스트 엔지니어링 | 특정 시점에 윈도우에 들어가는 내용 |
| 하네스 엔지니어링 | 위 둘을 포함한 런타임 시스템 전체 |

### 실무 통찰
- 도구가 돌려주는 결과와 에러 메시지도 사실상 프롬프트 — 긴 세션에서 모델이 보는 토큰의 절반 이상은 하네스가 생성한 텍스트
- 복구 가능한 에러 설계가 성능에 직결 — "파일 없음" 대신 "경로가 틀림, 상위 디렉터리에 유사 이름 X 존재"
- 도구는 사람이 아니라 모델이 쓰기 좋게 설계 — 사람용 CLI를 그대로 노출하는 것과는 결과가 다름
- 하네스에는 두 종류가 혼재
  - 현재 모델의 약점을 메우는 임시 보조 장치 → 다음 모델 출시 시 대부분 폐기
  - 모델이 강해질수록 가치가 커지는 인프라(샌드박스, 검증기, 관측 도구)
- 평가 스위트 없이는 하네스 개선 불가 — 측정 수단이 없으면 감에 의존하게 됨. 실제 업무 시간의 상당 부분이 태스크 세트·회귀 테스트 작성에 투입

---

## 5. RAG (Retrieval-Augmented Generation)

LLM이 답변 생성 시 외부 지식을 검색해 활용하는 방법. 색인 단계와 검색-생성 단계로 구분.

### 1단계: 색인(Indexing) — 사전 준비
1. **문서 수집** — PDF, 웹페이지, DB, 사내 문서 등 참조 자료 확보
2. **청킹(Chunking)** — 문단·수백 토큰 단위로 분할. 너무 크면 검색 정확도 하락, 너무 작으면 문맥 손실 → 적절한 크기와 겹침(overlap) 설정이 관건
3. **임베딩(Embedding)** — 각 청크를 임베딩 모델로 벡터화. 의미가 유사한 텍스트는 벡터 공간에서 근접
4. **벡터 저장** — 벡터 DB(Pinecone, Chroma, Weaviate, FAISS 등)에 저장·인덱싱

### 2단계: 검색 및 생성 — 질의응답 시점
1. **질의 임베딩** — 사용자 질문을 동일한 임베딩 모델로 벡터화
2. **유사도 검색(Retrieval)** — 질의 벡터와 가장 유사한 상위 k개 청크 탐색(코사인 유사도 등). 키워드 검색(BM25)과 결합한 하이브리드 검색도 활용
3. **재순위화(Reranking, 선택)** — 검색 후보를 더 정교한 모델로 재평가해 순서 재조정
4. **프롬프트 구성(Augmentation)** — 검색된 청크를 원 질문과 함께 프롬프트에 삽입
   - 예: "다음 문서를 참고해서 질문에 답하세요: [검색된 내용] 질문: [사용자 질문]"
5. **답변 생성(Generation)** — LLM이 확장된 프롬프트를 바탕으로 최종 답변 생성

### 도입 이유
- 지식 컷오프 이후 정보나 비공개 데이터 활용 가능
- 환각(hallucination) 감소 — 근거 문서 기반 답변
- 재학습(fine-tuning) 없이 최신·전문 지식 반영
- 출처 표시를 통한 신뢰성 확보

### 벡터 DB
- 최근 실무에서 PostgreSQL 사용 비중이 높음
- `pgvector` 확장을 통해 임베딩 벡터 전용 타입·인덱스 지원 → 별도 벡터 DB 없이 통합 운영 가능
- 전체 흐름(수집 → 청킹 → 임베딩 → 저장 → 검색 → 생성)을 먼저 파악해야 개별 기술 학습이 가능

---

## 6. Tool Calling (함수 호출)

### 핵심 요약
- LLM은 여전히 텍스트만 출력. 함수를 실제로 실행하는 주체는 LLM이 아니라 파이썬 프로세스
- 모델이 한 일은 `{"name": "get_weather", "arguments": "{\"city\": \"천안\"}"}` 형태의 텍스트 생성뿐
- 이를 파싱해 `get_weather(city="천안")`를 호출한 것은 프레임워크 코드(CPU)
- "문장 in, 문장 out"이라는 이해는 유효. 그 문장이 '함수 호출 요청서' 형식일 뿐

### 층위 1 — 코드 표면

```python
@tool
def get_weather(city: str) -> str:
    """특정 도시의 날씨 가져오기"""
    return f"It's always sunny in {city}!"
```

`@tool` 데코레이터는 함수를 '파이썬 함수인 동시에 LLM에게 설명 가능한 객체'로 변환.

| 파이썬 코드 요소 | 변환 결과 | LLM이 보는가 |
|---|---|---|
| 함수 이름 `get_weather` | 툴 이름 | O |
| docstring | 툴 설명 | O |
| 타입 힌트 `city: str` | JSON Schema `"type": "string"` | O |
| 함수 본문 `return ...` | — | X |

- docstring이 없으면 에러 발생 — 주석이 아니라 LLM에게 주는 사용설명서이기 때문
- 한글 docstring도 그대로 전달되므로 사용 가능

```python
agent = create_agent(model=llm, tools=[get_weather])
```
- LLM을 감싸는 루프(loop) 생성. 실체는 LangGraph 상태 그래프
- LangChain 1.0에서 도입된 API (이전에는 `langgraph.prebuilt.create_react_agent`)

### 층위 2 — 실제 네트워크 통신
`agent.invoke()` 한 번에 API 호출이 **2회** 발생.

**1차 요청** — 메시지와 함께 `tools` 배열 전송. `@tool`이 생성한 JSON Schema가 프롬프트에 실려 감

```json
"tools": [{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "특정 도시의 날씨 가져오기",
    "parameters": {
      "type": "object",
      "properties": {"city": {"type": "string"}},
      "required": ["city"]
    }
  }
}]
```

**1차 응답**

```json
{
  "finish_reason": "tool_calls",
  "message": {
    "role": "assistant",
    "content": null,
    "tool_calls": [{
      "id": "call_x7Kp2mQ",
      "function": {"name": "get_weather", "arguments": "{\"city\":\"천안\"}"}
    }]
  }
}
```

주목할 점
1. `content`가 `null` — 사람에게 할 말은 생성하지 않음
2. `arguments`가 객체가 아니라 **문자열** — 이스케이프된 따옴표가 보임. 모델이 글자 단위로 생성한 텍스트라는 직접적 증거
3. `finish_reason`이 `"stop"`이 아니라 `"tool_calls"` — 실행 요청 신호

**중간 처리 (LLM 아님, 파이썬 영역)**

```python
tool_map = {"get_weather": get_weather}
for call in ai_message.tool_calls:
    fn = tool_map[call["name"]]        # 이름으로 함수 조회
    output = fn.invoke(call["args"])   # 실제 실행 지점
    results.append(ToolMessage(
        content=str(output),
        tool_call_id=call["id"]        # 짝 맞추기용 id
    ))
```
- 'LLM이 함수를 실행한다'고 느껴지는 지점의 실체 — 평범한 딕셔너리 조회와 함수 호출

**2차 요청** — 대화 기록에 `"role": "tool"` 메시지 추가 후 재전송. 툴 스키마도 매번 재전송(API는 stateless이므로 모델은 직전 턴을 기억하지 못함)

**2차 응답** — `finish_reason: "stop"`, `tool_calls` 없음 → 루프 종료. 이 값이 `result["messages"][-1].content`

### 층위 3 — 에이전트 루프

```
START
 ↓
┌→ [model] ──────────┐
│     ↓              │
│  tool_calls 있나?   │ 없으면
│     ↓ 있으면        │
└─ [tools]           ↓ END
```

```python
def should_continue(state):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END
```
- if문 한 줄이 '에이전트' 자율성의 전부
- 상태(state)는 메시지 리스트 하나. `add_messages` 리듀서가 붙어 있어 각 노드 반환값이 덮어쓰기가 아니라 누적(append)
- `for m in result["messages"]: m.pretty_print()`로 Human / Ai(Tool Calls) / Tool / Ai 4개 메시지 확인 가능 → `[-1]`을 쓰는 이유

### 층위 4 — 모델이 툴 호출을 아는 원리
1. **학습된 행동** — 파인튜닝 단계에서 "툴 스키마가 주어지면 적절한 호출을 생성"하는 데이터를 대량 학습. 창발적 능력이 아니라 의도적으로 주입된 포맷 준수 능력
2. **내부적으로는 특수 토큰** — `<|tool_call|>get_weather<|args|>{"city": "천안"}<|end|>` 형태를 출력하고, API 서버가 이를 파싱해 `tool_calls` JSON 필드로 가공. 구조화된 응답은 API 계층의 가공품
3. **제약 디코딩(constrained decoding)** — JSON Schema를 문법으로 변환해 스키마상 불가능한 토큰의 확률을 0으로 만듦. 깨진 JSON이 거의 나오지 않는 이유
4. **`temperature=0`** — 툴 선택을 결정론적으로 만들기 위함. 온도가 높으면 툴을 호출하지 않거나 도시명을 "Cheonan"으로 쓰는 등 흔들림 발생

### 층위 5 — 프레임워크 없이 직접 구현

```python
import json
from openai import OpenAI

client = OpenAI()

def get_weather(city: str) -> str:
    return f"It's always sunny in {city}!"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "특정 도시의 날씨 가져오기",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]
REGISTRY = {"get_weather": get_weather}

messages = [{"role": "user", "content": "천안 날씨 어때?"}]

while True:                                   # 에이전트 루프
    res = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=messages, tools=TOOLS,
    )
    msg = res.choices[0].message
    messages.append(msg)

    if not msg.tool_calls:                    # 종료 조건
        print(msg.content)
        break

    for call in msg.tool_calls:               # 실행 주체는 내 코드
        fn = REGISTRY[call.function.name]
        args = json.loads(call.function.arguments)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(fn(**args)),
        })
```
- 약 35줄. `create_agent`는 이 while 루프에 재시도, 스트리밍, 체크포인팅, 미들웨어, 다중 모델 지원을 얹은 것
- 미들웨어가 `create_agent`의 핵심 — 동적 프롬프트, 대화 요약, 선택적 툴 접근, 상태 관리, 가드레일 제어

### 층위 6 — 실전 함의
1. **보안은 개발자 책임** — 실행 주체가 자신의 프로세스이므로 `run_sql(query: str)` 같은 툴을 주면 LLM이 생성한 문자열이 DB에서 실행됨. 위험한 툴에는 human-in-the-loop 승인 필요
2. **인자는 환각될 수 있음** — `city="천안시 동남구"`처럼 임의 정규화하거나 애매하면 지어냄. 툴 함수 내부에서 입력 검증 필수. Pydantic 모델을 `args_schema`로 주면 실행 전 필터링 가능
3. **툴 이름과 docstring이 성능을 좌우** — 사실상 프롬프트 엔지니어링. `def f(x: str) + """처리"""`와 `def get_current_weather(city: str) + """도시명(한글 가능)을 받아 현재 날씨를 반환. 미래 예보는 불가."""`의 정확도 차이가 큼
4. **토큰 비용 증가** — 툴 스키마는 매 호출마다 전송되고, 대화 누적으로 이전 메시지도 계속 재전송. 툴 20개면 매 턴 수천 토큰이 고정비
5. **무한 루프 가능** — 툴이 계속 실패하면 모델이 계속 재시도. LangGraph의 `recursion_limit`(기본 25)이 안전장치

### 검증 실험

```python
# 실험 1: LLM은 함수 본문을 모름
result = llm.bind_tools([get_weather]).invoke("천안 날씨 어때?")
print(result.content)     # '' ← 빈 문자열
print(result.tool_calls)  # [{'name': 'get_weather', 'args': {'city': '천안'}, ...}]
# 아무 함수도 실행되지 않음. "이거 불러줘"라는 텍스트만 생성됨

# 실험 2: docstring이 판단 기준
@tool
def get_weather(city: str) -> str:
    """주가를 조회한다"""          # ← 설명만 거짓으로 변경
    return f"It's always sunny in {city}!"
# → 날씨 질문에 이 툴을 호출하지 않게 됨. 본문은 그대로인데도 결과가 달라짐
```
- `bind_tools`는 스키마만 붙인 것이고 루프가 없으므로 실행이 일어나지 않음
- `create_agent`가 추가한 것은 출력을 읽고 실제로 호출해주는 while 루프뿐

---

## 7. Tool 관련 용어 정리

### 층위별 명칭
| 대상 | 공식 용어 | 코드상 위치 |
|---|---|---|
| 파이썬 함수 본문 | tool implementation / tool handler | `def get_weather(city): ...` |
| LLM에 보내는 JSON 스키마 | tool definition / tool schema (Google: function declaration) | `{"name": ..., "parameters": {...}}` |
| 모델이 쓸 수 있는 툴 전체 집합 | tool space / toolset (묶음은 toolkit) | `tools=[get_weather]` |
| 모델이 뱉은 호출 요청 | tool call | `{"name": "get_weather", "args": {...}}` |
| 실행 결과 반환 메시지 | tool result / tool message (학술: observation) | `{"role": "tool", ...}` |
| 메커니즘 전체 | tool calling / tool use | — |

- 엄밀히는 `get_weather`가 tool implementation, 모델이 보는 것은 tool definition. 일상적으로는 둘 다 "tool"

### 벤더별 용어 차이
| 주체 | 명칭 | 비고 |
|---|---|---|
| OpenAI | function → tool | 2023년 `functions` 파라미터를 `tools`로 교체. Responses API에서 function tool(직접 정의) vs built-in tool(웹 검색 등) 구분 |
| Anthropic | tool use | client-side tool(내 코드 실행) vs server tool(Anthropic 실행) 구분 |
| Google | function calling / function declaration | 스키마 명칭이 독특 |
| LangChain | Tool (BaseTool), toolkit | |
| MCP | Tool | Resources / Prompts / Tools 3분류 중, '모델이 능동적으로 호출하는 것' |

### function calling과 tool calling
- 역사적으로 동일한 것이며, 현재는 tool calling이 상위 개념
- 2023년 OpenAI가 `function_call`로 출시 → "function calling"이 널리 사용됨
- 이후 코드 실행기, 웹 검색 등 함수가 아닌 도구가 등장하며 `tools`로 확장
- 관계: function calling ⊂ tool calling

### 학술 용어
- **Action** — ReAct 논문(Yao et al., 2022)의 Thought → Action → Observation 사이클. 툴 집합은 action space
- **API call** — Toolformer 논문(Schick et al., 2023). 모델이 스스로 API 호출 시점을 학습
- **Tool-augmented LLM / tool learning** — 연구 분야 전체 명칭
- **Grounding** — LLM을 외부 실제 정보에 연결하는 것 일반. 툴 사용은 그 수단 중 하나
- `create_agent`가 "ReAct 패턴"으로 설명되는 이유 — 루프가 Action(tool_call) → Observation(tool result) → Action 사이클이기 때문

### 혼동하기 쉬운 인접 용어
- **Plugin** — 2023년 ChatGPT Plugins의 명칭. 현재는 사실상 폐기
- **Action (GPTs)** — OpenAPI 스펙으로 연결한 외부 API를 부르는 UI 용어. 학술적 action과 철자만 같고 맥락이 다름
- **Skill / Agent Skill** — 툴이 아니라 지시문 묶음. 호출 가능한 함수가 아니라 "이 작업은 이렇게 해라"를 알려주는 문서
- **Structured output / JSON mode** — 스키마에 맞는 JSON을 출력하게 하는 기능. 기술적 뿌리(제약 디코딩)는 같으나 실행할 함수가 없음
- **RAG** — 검색 결과를 개발자가 먼저 넣어주는 방식. 툴은 모델이 필요할 때 직접 요청하는 방식. 최근에는 검색을 툴로 제공해 둘이 통합되는 추세

---

## 8. 병렬 실행과 비동기

### LangChain `batch()`
- 입력 하나하나를 독립적으로 `invoke()` 한 것과 동일하며, 이를 병렬로 실행할 뿐
- 내부 동작: `chain.invoke({"topic": "ChatGPT"})`와 `chain.invoke({"topic": "Instagram"})`를 스레드풀(비동기면 `asyncio.gather`)로 동시 실행 후, 입력 순서 그대로 리스트 반환
- API 호출이 2번 나가는 것이지 두 topic이 한 프롬프트에 들어가는 것이 아님 → 서로 결과에 영향 없음

```python
chain.batch(
    [{"topic": "ChatGPT"}, {"topic": "Instagram"}],
    config={"max_concurrency": 5}
)
```

**예외: 공유 가변 상태(mutable state)**
- `ConversationBufferMemory` 같은 메모리 객체를 물려둔 경우 → 동일 히스토리 버퍼에 동시 쓰기로 내용이 섞이거나 순서가 꼬임
- 모듈 레벨 전역 변수나 리스트에 결과를 append 하는 커스텀 함수
- 스레드 세이프하지 않은 커스텀 콜백 핸들러
- 정리: 체인이 stateless면 완전 독립, 상태를 들고 있으면 위험. 프롬프트 → LLM → 파서 형태의 일반적 LCEL 체인은 stateless

**에러 처리**
- 기본값은 하나라도 실패하면 전체 예외 발생
- `chain.batch(inputs, return_exceptions=True)` — 실패 항목 자리에 예외 객체가 담긴 리스트 반환
- `batch_as_completed()` — 먼저 끝난 것부터 처리. 순서 보장 없음, (인덱스, 결과) 튜플 반환

### async / await
핵심은 "누가 기다리느냐".
- 동기 코드에서 대기 → 스레드 전체가 멈춤. CPU는 유휴 상태로 낭비
- `await`으로 대기 → 멈추는 것은 해당 함수 하나뿐. 제어권이 이벤트 루프로 반환되어 그동안 다른 작업 실행

```javascript
async function handler(req) {
  const data = await db.query(...);  // 1초
  return data;
}
```
- 함수 하나만 보면 동기와 동일하게 1초 소요
- 요청 100개 기준
  - 동기: 스레드가 점유되어 100초 (혹은 스레드 100개 필요)
  - 비동기: 대기 중 서로 양보하므로 약 1초
- 이득은 "함수가 빨라진다"가 아니라 "기다리는 동안 다른 일을 할 수 있다"

**한 함수 안에서 이득을 보려면**

```javascript
// 3초 — 순차 실행이라 동기와 차이 없음 (흔한 실수)
const a = await fetchA();
const b = await fetchB();
const c = await fetchC();

// 1초 — 동시에 출발시키고 나중에 수거
const [a, b, c] = await Promise.all([fetchA(), fetchB(), fetchC()]);
```
- `fetchA()`를 호출하는 순간 작업은 이미 시작됨
- `await`은 "시작해라"가 아니라 "결과가 나올 때까지 여기서 양보하겠다"는 의미 → 출발 시점과 수거 시점을 분리 가능

**`async`의 역할**
1. 함수가 중간에 멈췄다 재개될 수 있음을 표시 (컴파일러가 상태 머신으로 변환)
2. 반환값을 Promise로 감싸 호출자가 언제 기다릴지 선택할 수 있게 함
   - 값을 그대로 반환하면 호출자는 무조건 기다려야 함
   - Promise 반환이므로 "일단 받아두고 나중에 await" 또는 "여러 개 모아서 Promise.all"이 가능

- 정리: `await`은 기다림을 없애는 도구가 아니라, 기다림을 협조적으로 만드는 도구

---

## 9. CI/CD

코드를 자동으로 빌드, 테스트, 배포하는 방법론. 두 개념으로 구분.

### CI (Continuous Integration, 지속적 통합)
- 개발자들이 코드를 자주(하루에도 여러 번) 공유 저장소에 병합
- 병합 시마다 자동으로 빌드 성공 여부 확인, 테스트 실행으로 문제 검증
- 여러 명이 동시에 작업해도 충돌과 버그를 조기 발견 가능

### CD (Continuous Delivery / Deployment)
- CI 이후 단계. 테스트를 통과한 코드를 실제 서비스 환경으로 내보내는 과정을 자동화
- **Continuous Delivery(지속적 전달)**: 배포 직전 단계까지 자동화, 실제 배포는 사람이 최종 승인
- **Continuous Deployment(지속적 배포)**: 사람 개입 없이 테스트 통과 시 자동 배포 완료

### 도입 이유
- 수동 작업 감소로 실수 축소
- 작은 단위로 자주 통합하므로 버그 조기 발견
- 배포 속도 향상 → 새 기능을 더 자주, 안정적으로 출시

### 주요 도구
GitHub Actions, GitLab CI/CD, Jenkins, CircleCI, Travis CI

- 요약: "코드 변경 → 자동 테스트 → 자동 배포"로 이어지는 파이프라인 구성

---

## 10. 개발 환경 및 운영

### API 키 관리
- 키를 코드에 하드코딩하지 않고 환경변수로 등록 후 참조

```bash
# .env
OPENAI_API_KEY=${OPENAI_API_KEY}
```

- `.env`는 반드시 `.gitignore`에 포함 — 저장소 커밋 시 키 유출
- 키 유출 의심 시 즉시 재발급(rotate)
- 사용량 대시보드로 비정상 과금 여부 확인

### 모델 선택과 비용
- 예제 코드를 그대로 따라 하면 고성능·고가 모델이 기본값인 경우가 있으므로 모델명 확인 필요
- 호출 횟수, 입력 토큰 길이(툴 스키마·대화 누적 포함)가 비용에 직결
- 개발·학습 단계에서는 저가 모델(mini 계열)로 검증 후 전환

### 도구
- VS Code 명령 팔레트: `Ctrl + Shift + P` — 확장, 인터프리터 선택, 설정 등 대부분의 기능에 접근

### 레거시 대응
- 신입 업무는 대체로 유지보수부터 시작 → 기존 자료·코드를 읽는 능력이 중요
- 교재·예제의 라이브러리 버전이 구형인 경우가 많으므로, 공식 문서에서 현재 버전의 변경점(deprecated API 등)을 대조하는 습관 필요
- 수업 중에도 '지금 무엇을 하고 있는지'를 항상 인지하며 진행
