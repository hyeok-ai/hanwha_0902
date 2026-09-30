# 기술 노트 정리 (2026-09-29 수업)

## 목차

1. RAG 실습 과제 (Jupyter + RAGAS)
2. 참고 학습: Python과 MySQL
3. LLM 발전과 활용 기법의 변화 (2020–2026)
4. 상용 AI 모델의 개인정보 가리기 (가명 처리 후 복원)

---

## 1. RAG 실습 과제 (Jupyter + RAGAS)

### 과제 구성

- Jupyter 노트북 코드로 RAG 파이프라인을 만든다.
- 서버 껍데기(FastAPI, Streamlit으로 추정)는 미리 제공된다.
- 제공된 구조에 맞게 연결해 실행되도록 만든 뒤 제출한다.
- 진행 방식: 기존 코드를 조합하고, 노트북을 만들고, 직접 돌려 본다.

### 대상 문서 (PDF)

- 주제: AI 안전성 관련 공개 문서
- 원본 74쪽을 30쪽으로 줄인 버전
- 구조: 목차 없이 `중간제목 → 내용 → 중간제목 → 내용`의 단순 반복
  - 이전 실습 PDF(목차 있음)보다 구조가 단순함
  - 청킹 시 중간제목 단위로 나누고 핵심 내용을 잘 뽑아오는 것이 중요

### 평가: RAGAS

- RAGAS 채점기(서버 형태)가 함께 제공된다.
- RAGAS는 점수를 짜게 주는 편이다.
  - 합성 데이터셋으로 만든 질문·정답 문장이 거시적(포괄적)이어서, 내용상 맞는 답도 70점 정도로 나올 수 있음.
- 전체 RAGAS 점수, 점수 분산, 실제 동작 여부를 함께 본다.

### 확인 포인트

- **디버깅 출력:** 중간 출력을 찍어 볼 때 무엇을 확인하려는 것인지 설명할 수 있어야 한다.
- **버전 관리:** 1차 버전에서는 파이프라인 단계의 **순서**가 가장 중요하다.
- **성능 개선:** 실무에서는 Claude와 협업해 성능을 끌어올리는 과정이 더 중요하다.
- **lambda:** 직접 쓸 필요는 없지만, 남이 작성한 lambda 코드는 읽을 수 있어야 한다.

### 확인 필요

- `.ipynb` 코드를 FastAPI·Streamlit 껍데기에 어떻게 연결하는지. (일반적으로는 노트북의 함수를 `.py` 모듈로 옮겨 서버 코드에서 import하는 방식이 쓰임)
- RAGAS로 채점한다면 서버 껍데기가 어떤 역할을 하는지 (채점기가 서버 API를 호출하는 구조인지).

---

## 2. 참고 학습: Python과 MySQL

- w3schools의 Python MySQL 튜토리얼 부분을 살펴봄 (DB 관리 관련).

---

## 3. LLM 발전과 활용 기법의 변화 (2020–2026)

2020년부터 2026년 9월까지의 흐름은 두 축으로 정리된다.

- **모델 자체:** 크기 확대 → 정렬 → 추론 학습 → 긴 작업 수행 능력
- **활용 방식:** 프롬프트 작성 → RAG → 도구·에이전트 → 컨텍스트 엔지니어링 → 하네스 엔지니어링

### 3-1. 모델 자체의 발전

#### ① 스케일링 법칙의 정교화 (2020–2022)

- GPT-3(2020) 이후 한동안 "모델을 크게"가 기본 전략이었다.
- **Chinchilla (DeepMind, 2022):** 400개 이상의 모델을 학습시킨 결과, 연산량이 고정일 때 모델 크기와 학습 토큰 수를 같은 비율로 늘려야 한다고 결론. 모델 크기를 두 배로 하면 데이터도 두 배. → '파라미터당 약 20토큰' 규칙의 출처.
- 최근 경향: 추론 비용을 줄이기 위해 작은 모델을 권장치보다 훨씬 많은 토큰으로 일부러 과학습(overtraining)시킨다.

#### ② 정렬(RLHF)과 ChatGPT (2022)

- **InstructGPT:** 평가자들이 13억 파라미터 InstructGPT의 출력을 1,750억 파라미터 GPT-3보다 선호. → 크기보다 사용자 의도를 따르게 하는 것이 중요.
- 이 RLHF 방법론이 2022년 11월 ChatGPT의 기반이 되었다.

#### ③ 추론 모델과 테스트 타임 컴퓨트 (2024–2025)

- **OpenAI o1 (2024.9):** 성능이 두 축 모두에 따라 좋아진다고 발표.
  - 강화학습에 쓰는 학습 연산량
  - 답하기 전 생각하는 시간(추론 시 연산량)
- **DeepSeek-R1 (2025.1, 이후 Nature 게재):** 사람이 작성한 추론 과정 데이터 없이 순수 강화학습만으로 추론 능력을 끌어낼 수 있음을 보임. 수학·코딩·논리 영역에서 규칙 기반 보상 사용.
- 이후 **검증 가능한 보상으로 RL을 돌리는 방식**이 업계 표준이 되었다.

#### ④ 비용 급락과 모델 간 격차 축소

- **Stanford AI Index 2025:** GPT-3.5 수준 성능의 추론 비용이 2022.11~2024.10 사이 280배 이상 하락. 하드웨어 비용은 연 30% 감소, 에너지 효율은 연 40% 개선.
- **AI Index 2026:** 역량 향상이 가속되는 중. SWE-bench Verified 점수가 1년 만에 60%에서 거의 100%로 상승. 미국·중국 모델 간 성능 격차는 사실상 사라짐.

#### ⑤ 에이전트 능력의 지수적 성장

- **METR 타임 호라이즌:** 사람 전문가 기준 몇 분~몇 시간 걸리는 작업을 AI 에이전트가 50% 신뢰도로 자율 완수할 수 있는 길이.
  - 지난 6년간 약 7개월마다 두 배.
  - 2026.1 개정판(TH1.1): 2024년 이후 배증 기간이 TH1 기준 109일, TH1.1 기준 89일로 단축.
- **반론:**
  - 데이터가 장기 예측을 뒷받침할 만큼 조밀하지 않다는 통계적 비판.
  - 50% 성공률 기준과 80% 성공률 기준 사이 격차가 크다는 지적.

### 3-2. 활용 방식의 발전

#### ① 프롬프팅에서 추론+행동 루프로 (2022)

- 초기: few-shot 예시, Chain-of-Thought 등 프롬프트 문구 자체를 다듬는 기법.
- **ReAct (2022.10):** 추론과 행동을 번갈아 생성.
  - 추론: 계획 수립·수정, 예외 처리
  - 행동: 외부 정보원에 접근해 정보 수집
- 오늘날 에이전트 루프(생각 → 도구 호출 → 관찰의 반복)의 원형.

#### ② RAG의 진화

| 단계 | 내용 |
| --- | --- |
| **출발점 (2020)** | Lewis 등의 원래 RAG 논문. 모델 파라미터에 저장된 지식에 외부 검색을 결합. 동기: 출처 추적, 검증 가능성, 지식 갱신 용이성. |
| **GraphRAG (2024)** | Microsoft Research. "이 데이터셋의 주요 주제는?" 같은 말뭉치 전체 대상 질문에서 기존 RAG가 실패함을 지적(검색보다 질의 중심 요약에 가까운 문제). LLM으로 지식 그래프를 만들고 엔티티 묶음별 요약 → 요약별 부분 답 → 최종 답 생성. |
| **긴 컨텍스트의 한계** | 컨텍스트 창은 수백만 토큰까지 늘었지만, Chroma가 18개 모델을 평가한 결과 모델은 컨텍스트를 균일하게 활용하지 못하고 입력이 길수록 성능이 불안정해짐 → **context rot**. |
| **에이전트형 검색 (2025~)** | 미리 임베딩해 두는 대신 필요할 때 찾아보는 방식. 에이전트가 파일 경로·링크 같은 가벼운 참조만 들고 있다가 실행 중 도구로 데이터를 불러오는 **적시(just-in-time)** 방식. Claude Code가 이 방식을 사용. |

#### ③ 스캐폴딩: 인터페이스가 성능을 좌우함

- **SWE-agent (2024):** LM 에이전트를 고유한 요구를 가진 새로운 사용자층으로 보고 전용 인터페이스(**ACI**, Agent-Computer Interface)를 설계 → 파일 편집, 저장소 탐색, 테스트 실행 능력이 크게 향상.
- **o1 시스템 카드:** 단순한 기본 스캐폴딩에서는 o1이 공개 모델보다 낮은 성능. 단계마다 여러 후보 중 고르게 하는 식으로 바꾸자 Claude 3.5 Sonnet을 넘어 2시간 제한 인간과 비슷한 수준.
- → 같은 모델이라도 무엇으로 감싸느냐에 따라 평가가 뒤집힐 수 있다.

#### ④ 에이전트 설계 원칙 (2024년 말)

- **Anthropic 'Building effective agents' (2024.12):**
  - **워크플로우:** 미리 정해진 코드 경로로 LLM과 도구를 조율하는 시스템
  - **에이전트:** 워크플로우와 구분되는 개념
  - 에이전트 시스템은 지연과 비용을 대가로 성능을 얻는 것이므로, 아예 만들지 않는 편이 나을 수도 있다.

#### ⑤ 도구 연결의 표준화

- **MCP (2024.11):** Anthropic이 AI 어시스턴트를 콘텐츠 저장소·업무 도구·개발 환경 등에 연결하는 표준으로 오픈소스 공개. 2025.9 OpenAI도 ChatGPT 앱에 MCP 지원 추가.
- **Agentic AI Foundation (2025.12):** Anthropic이 MCP를 리눅스 재단 산하 재단에 기증. Anthropic·Block·OpenAI 공동 설립, Google·Microsoft·AWS 등 지원. OpenAI의 AGENTS.md, Block의 goose도 창립 프로젝트로 합류.
- **Agent Skills (2025.12 개방형 표준화):** 점진적 공개(progressive disclosure) 방식.
  1. 시작 시 각 스킬의 이름과 설명만 로드
  2. 작업이 맞아떨어지면 전체 지침을 읽음
  3. 필요하면 참조 파일·스크립트를 추가로 사용
  - 컨텍스트를 아끼는 설계가 표준 수준까지 올라옴.

#### ⑥ 프롬프트 엔지니어링 → 컨텍스트 엔지니어링 (2025)

- Anthropic(2025.9.29)이 컨텍스트 엔지니어링을 프롬프트 엔지니어링의 다음 단계로 규정.
- 프롬프트뿐 아니라 컨텍스트 창에 들어가는 **모든 토큰**을 관리 대상으로 봄.
- 핵심 차이: 프롬프트는 한 번 쓰지만, 컨텍스트는 매 턴마다 관리해야 한다.
- 긴 작업을 위한 기법 세 가지:
  1. 대화 이력 요약 (compaction)
  2. 외부 메모 파일에 기록
  3. 깨끗한 컨텍스트를 가진 하위 에이전트로 일을 분할

#### ⑦ 하네스 엔지니어링 (2025년 말~2026)

모델을 둘러싼 실행 시스템 전체(하네스)가 초점.

- **Anthropic (2025.11):** 여러 컨텍스트 창에 걸친 장기 작업용 두 에이전트 구조.
  - 초기화 에이전트: 기능 목록, git 저장소, 진행 기록 파일 준비
  - 코딩 에이전트: 한 번에 하나씩 기능 구현, 커밋과 문서로 상태 기록
- **용어 확산 (2026.2):** Mitchell Hashimoto(HashiCorp 공동창업자)가 에이전트가 같은 실수를 반복하지 않게 하는 장치를 만드는 일을 '하네스 엔지니어링'이라 부름. 며칠 뒤 OpenAI의 Codex 관련 글로 확산.
  - 합의된 정의: **에이전트 = 모델 + 하네스**
  - 하네스를 잘 만드는 방법은 아직 열린 문제
- **연구 동향:** 프롬프트 → 컨텍스트 → 하네스 엔지니어링으로 이어지는 패러다임 전환. 목표는 에이전트를 통제 가능하고, 감사 가능하며, 실서비스에서 믿을 수 있게 만드는 것.

### 3-3. 종합

| 시기 | 모델 쪽 핵심 변화 | 활용 쪽 핵심 변화 |
| --- | --- | --- |
| 2020–2021 | GPT-3, 스케일링 법칙 | few-shot 프롬프팅, 초기 RAG |
| 2022 | Chinchilla, RLHF, ChatGPT | Chain-of-Thought, ReAct |
| 2023–2024 | 멀티모달, 긴 컨텍스트, 오픈 모델 추격 | 벡터DB RAG, 함수 호출, GraphRAG, SWE-agent(ACI), MCP |
| 2024 말–2025 | 추론 모델(o1, R1), 검증 가능한 보상 기반 RL | 워크플로우/에이전트 구분, 코딩 에이전트, 컨텍스트 엔지니어링, Skills |
| 2026 | 벤치마크 포화, 타임 호라이즌 급증 | 하네스 엔지니어링, 표준의 재단 이관 |

- 무게중심 이동: **"모델이 무엇을 아는가"** → **"모델이 어떤 환경에서 얼마나 오래, 믿을 만하게 일하는가"**
- RAG는 초기에 지식 공백을 메우는 핵심 도구였으나, 지금은 에이전트가 쓰는 여러 도구 중 하나. 성능 차이는 컨텍스트 관리, 상태 보존, 검증 루프 같은 하네스 설계에서 갈린다.
- 유의점:
  - AI Index 2026: 책임 있는 AI 평가가 역량 발전을 따라가지 못함. 기록된 AI 사고가 2024년 233건 → 362건으로 증가.
  - 벤치마크 점수가 곧 실제 신뢰성은 아니다.
  - 분야가 몇 달 단위로 바뀌므로 최신 모델명·수치는 발표 시점에 재확인 필요.

### 3-4. 출처

- [Training Compute-Optimal Large Language Models (Hoffmann et al., NeurIPS 2022)](https://proceedings.neurips.cc/paper_files/paper/2022/file/c1e2faff6f588870935f114ebe04a3e5-Paper-Conference.pdf)
- [Chinchilla scaling: A replication attempt (Epoch AI)](https://epoch.ai/publications/chinchilla-scaling-a-replication-attempt)
- [Test-Time Scaling Makes Overtraining Compute-Optimal (arXiv 2604.01411)](https://arxiv.org/pdf/2604.01411)
- [Training language models to follow instructions with human feedback (Ouyang et al., NeurIPS 2022)](https://proceedings.neurips.cc/paper_files/paper/2022/file/b1efde53be364a73914f58805a001731-Paper-Conference.pdf)
- [Learning to reason with LLMs (OpenAI, 2024)](https://openai.com/index/learning-to-reason-with-llms/)
- [OpenAI o1 System Card](https://openai.com/index/openai-o1-system-card/)
- [DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning (Nature 645, 2025)](https://www.nature.com/articles/s41586-025-09422-z)
- [The 2025 AI Index Report (Stanford HAI)](https://hai.stanford.edu/ai-index/2025-ai-index-report)
- [The 2026 AI Index Report (Stanford HAI)](https://hai.stanford.edu/ai-index/2026-ai-index-report)
- [Measuring AI Ability to Complete Long Software Tasks (METR, 2025)](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- [Time Horizon 1.1 (METR, 2026)](https://metr.org/blog/2026-1-29-time-horizon-1-1/)
- [Is there a half-life for the success rates of AI agents? (arXiv 2505.05115)](https://arxiv.org/pdf/2505.05115)
- [Are AI time horizon doubling every seven months? (비판적 리뷰)](https://medium.com/@AIchats/are-ai-time-horizon-doubling-every-seven-months-e337162eec83)
- [ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al.)](https://www.semanticscholar.org/paper/ReAct:-Synergizing-Reasoning-and-Acting-in-Language-Yao-Zhao/99832586d55f540f603637e458a292406a0ed75d)
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)](https://www.researchgate.net/publication/341639856_Retrieval-Augmented_Generation_for_Knowledge-Intensive_NLP_Tasks)
- [From Local to Global: A Graph RAG Approach (Microsoft Research)](https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/)
- [GraphRAG 요약 해설](https://ssawant.github.io/posts/GraphRAG%20/GraphRAG.html)
- [Context Rot (Chroma, 2025)](https://www.trychroma.com/research/context-rot)
- [SWE-agent: Agent-Computer Interfaces (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)
- [Building effective agents (Anthropic, 2024)](https://www.anthropic.com/engineering/building-effective-agents)
- [Introducing the Model Context Protocol (Anthropic, 2024)](https://www.anthropic.com/news/model-context-protocol)
- [Model Context Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Model_Context_Protocol)
- [Donating the MCP and establishing the Agentic AI Foundation (Anthropic, 2025)](https://anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- [Knowledge Activation: AI Skills… (arXiv 2603.14805)](https://arxiv.org/pdf/2603.14805)
- [Effective context engineering for AI agents (Anthropic, 2025)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Effective context engineering 해설 (BERI)](https://www.beri.net/learning/anthropic-effective-context-engineering-agents)
- [Context Engineering: AI Agent Optimization Guide](https://howaiworks.ai/blog/anthropic-context-engineering-for-agents)
- [Effective harnesses for long-running agents 요약 (daily.dev)](https://daily.dev/posts/effective-harnesses-for-long-running-agents-7clzunmmu)
- [Beyond Prompts and Context: Harness Engineering for AI Agents](https://madplay.github.io/en/post/harness-engineering)
- [The State Of AI Harness Engineering 2026 (marmelab)](https://marmelab.com/blog/2026/09/24/the-state-of-ai-harness-engineering-2026.html)
- [SemaClaw: Harness Engineering (arXiv 2604.11548)](https://arxiv.org/pdf/2604.11548)

---

## 4. 상용 AI 모델의 개인정보 가리기 (가명 처리 후 복원)

ChatGPT, Claude 같은 상용 모델을 그대로 쓰면서 개인정보를 보호하려면, 보내기 전에 개인정보를 가리고 답에서 되돌리는 **중간 계층**을 둔다. 아래 서비스별 기능은 대부분 각 회사가 스스로 밝힌 내용이며 독립적으로 검증된 것은 아니다.

### 4-1. 원리

모델 제공사는 개인정보 대신 자리표시자만 받는다.

1. **가리기:** 요청에서 개인정보를 찾아 `<EMAIL_ADDRESS_1>`, `<PERSON_2>` 같은 자리표시자로 바꾼 뒤 전송
2. **생성:** 모델은 자리표시자가 든 글을 처리하고, 자리표시자를 그대로 둔 답을 반환
3. **복원:** 사용자에게 돌려주기 전에 자리표시자를 원래 값으로 치환

예시:

| 단계 | 내용 |
| --- | --- |
| 입력 | 김철수(010-1234-5678) 고객에게 환불 안내 메일 써줘 |
| 모델이 받는 것 | `<PERSON_1>`(`<PHONE_1>`) 고객에게 환불 안내 메일 써줘 |
| 모델의 답 | `<PERSON_1>`님, 안녕하세요… |
| 사용자가 보는 것 | 김철수님, 안녕하세요… |

### 4-2. 제공 서비스

| 서비스 | 대상 | 확인된 내용 |
| --- | --- | --- |
| [NanoGPT](https://docs.nano-gpt.com/api-reference/miscellaneous/pii-redaction) | 개인·개발자 | 옵션을 켜면 요청이 Grepture를 거쳐 개인정보가 가려진 뒤 모델로 전달, 응답에서 가능한 경우 복원. 가리기 실패 시 요청을 보내지 않음(fail-closed). |
| [PrivateGPT (Private AI)](https://www.prnewswire.com/news-releases/introducing-privategpt-a-private-ai-solution-301812286.html) | 기업 | 50가지 이상의 개인정보를 지우고 ChatGPT에 보낸 뒤 답에 다시 채움. 항목별 on/off 가능. 고객사 자체 환경에 설치되어 Private AI에도 개인정보가 전달되지 않는다고 밝힘. 현재 회사명은 [Limina](https://www.private-ai.com/en). 2023년 출시 자료 기준. |
| [Skyflow](https://www.skyflow.com/post/private-llms-data-protection-potential-and-limitations) | 기업 | 민감정보를 토큰으로 바꿔 모델에 입력. 복원 권한을 엄격히 통제해, 권한 없는 사용자는 답에 나온 민감정보를 볼 수 없음. |
| [ChatGPT Privacy Shield](https://www.redact.tools/) | 개인 (브라우저 확장) | 전송 전 프롬프트를 가로채 개인정보를 자리표시자로 가림. 처리가 모두 기기 안에서 이루어진다고 밝힘. |
| [orq.ai](https://docs.orq.ai/docs/ai-gateway/plugins/pii-redaction.md) | 개발자 (AI 게이트웨이) | 플러그인 형태. 제공사는 자리표시자만 받고, 원래 값은 응답에서 복원. |
| [llm-redactor](https://github.com/jayluxferro/llm-redactor) | 개발자 (GitHub 오픈소스) | 기기에서 요청을 가로채 가린 뒤 클라우드 API로 보내고 답에서 복원. 기존 API 주소만 바꾸면 적용. |

### 4-3. 한계

가리기는 개인정보 노출을 **줄이는** 것이지 완전한 익명화가 아니다.

- **되돌릴 수 있음:** 자리표시자는 원래 값으로 되돌릴 수 있도록 설계된 것이므로 익명화가 아니다. ([DEV Community](https://dev.to/mukundakatta/pii-in-your-prompt-logs-is-a-liability-redact-before-you-send-12c2))
- **감소일 뿐 차단이 아님:** NanoGPT 문서도 가리기는 제공사로 가는 정보를 줄이기 위한 것이며, 불필요한 개인정보나 인증 정보는 애초에 보내지 말라고 안내한다. ([NanoGPT 문서](https://docs.nano-gpt.com/api-reference/miscellaneous/pii-redaction))

### 4-4. 출처

- [PII Redaction - NanoGPT Docs](https://docs.nano-gpt.com/api-reference/miscellaneous/pii-redaction)
- [PII Redaction - orq.ai Docs](https://docs.orq.ai/docs/ai-gateway/plugins/pii-redaction.md)
- [Introducing PrivateGPT - PR Newswire (2023)](https://www.prnewswire.com/news-releases/introducing-privategpt-a-private-ai-solution-301812286.html)
- [PrivateGPT - Help Net Security (2023)](https://www.helpnetsecurity.com/2023/05/02/private-ai-privategpt/)
- [Limina (Private AI)](https://www.private-ai.com/en)
- [Private LLMs: Data Protection - Skyflow](https://www.skyflow.com/post/private-llms-data-protection-potential-and-limitations)
- [ChatGPT Privacy Shield](https://www.redact.tools/)
- [llm-redactor - GitHub](https://github.com/jayluxferro/llm-redactor)
- [PII in Your Prompt Logs Is a Liability - DEV Community](https://dev.to/mukundakatta/pii-in-your-prompt-logs-is-a-liability-redact-before-you-send-12c2)
