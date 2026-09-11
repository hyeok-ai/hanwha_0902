## 1. LangChain 기본 사용법 및 LCEL
* **LCEL (LangChain Expression Language)**
  * 여러 구성 요소를 하나의 체인으로 엮어 주는 표현 방식.
  * 파이프 연산자(`|`)를 사용하여 구성 요소를 연결함.
  * 구성 예시: `chain = prompt | model | output_parser`
* **메시지 구성 및 프롬프트 템플릿**
  * `SystemMessage`, `HumanMessage`를 통해 시스템과 사용자 역할을 분리함.
  * 변수(예: `{question}`) 반복 사용 시 `ChatPromptTemplate`을 활용함.
  * LLM 객체(`ChatOpenAI`, `ChatGoogleGenerativeAI`)만 교체하면 동일한 프롬프트 및 체인 코드로 여러 모델을 유연하게 사용할 수 있음.

## 2. 환경 변수 및 API 키 관리
* 환경 변수(`.env`)에 API 키(`OPENAI_API_KEY`, `GEMINI_API_KEY` 등)를 저장하여 관리함.
* `python-dotenv` 라이브러리의 `load_dotenv()`를 이용해 키를 로드함.
* 최신 OpenAI 라이브러리는 별도 지정 없이 환경 변수의 키를 자동 인식함.
* **주의:** `.env` 파일은 반드시 `.gitignore`에 추가하여 버전 관리에 포함되지 않도록 설정해야 함.

## 3. 파이썬 패키지 및 환경 관리
* **버전 관리**
  * 라이브러리는 버전업에 따라 사용법이 자주 바뀌므로 버전을 정확히 확인해야 함.
* **requirements.txt**
  * 프로젝트 실행에 필요한 패키지와 버전을 명시하는 파일.
  * 생성: `pip freeze > requirements.txt` (현재 환경 패키지 목록 추출)
  * 설치: `pip install -r requirements.txt` (목록 패키지 일괄 설치)
  * 글로벌 환경이 아닌 **가상환경(Virtual Environment)**과 함께 사용하여 프로젝트별로 격리 관리하는 것이 권장됨.
* **의존성(Dependencies) 관리**
  * 특정 패키지 설치 시 동작에 필요한 다른 패키지들이 자동으로 함께 설치됨.
  * `pip show [패키지명]`: 해당 패키지가 요구하는 의존성 목록 확인
  * `pip list`: 설치된 전체 패키지 목록 확인
  * `pip install [패키지명] --no-deps`: 의존성을 무시하고 단독 설치
* **pip 축약 옵션 (`-qU`)**
  * `-q` (`--quiet`): 설치 과정 로그 숨김 (자동화, CI/CD에서 유용)
  * `-U` (`--upgrade`): 기존 버전을 삭제하고 최신 버전으로 덮어씌움
  * `pip install -qU [패키지명]` 형태로 사용함.

## 4. Git Fork 동기화 (Sync)
* Fork한 레포지토리는 원본(Upstream) 업데이트 시 자동으로 동기화되지 않으므로 직접 동기화가 필요함.
* **동기화 방법:**
  1. **GitHub 웹 UI:** Fork 저장소 페이지에서 'Sync fork' -> 'Update branch' 클릭.
  2. **Git CLI:**
     * 원본 저장소 등록: `git remote add upstream <원본_레포지토리_URL>`
     * 원본 변경 사항 가져오기: `git fetch upstream`
     * 메인 브랜치 병합: `git checkout main` 이동 후 `git merge upstream/main`
     * Fork 저장소에 푸시: `git push origin main`

## 5. 파이썬 디버깅 팁
* **f-string `=` 디버깅 문법 (Python 3.8 이상)**
  * 변수나 식 뒤에 `=`를 붙여 변수명과 결과값을 동시에 출력함.
  * 예시: `print(f"{type(response)=}")` -> `type(response)=<class 'dict'>`
* **icecream 라이브러리**
  * `ic()` 함수를 사용하여 디버깅 출력에 색상을 입혀 가독성을 높임 (`pip install icecream`).

## 6. 하네스 엔지니어링 (Harness Engineering)
* AI 에이전트가 올바르게 동작하도록 환경을 설계하는 기술.
* 에이전트의 능력을 제한하는 것이 아니라, 그 능력이 올바른 방향으로 발휘되도록 구조를 갖추는 데 목적이 있음.

## 7. 기타 기술 참고
* **로컬 LLM:** `ollama`를 설치하고 `qwen2.5` 모델을 활용하여 로컬 환경에서 LLM 테스트가 가능함.
* **파이썬 리스트 주석:** 리스트 내 항목을 주석 처리할 때 문법적 오류가 발생하지 않도록 콤마(`,`) 위치와 구조 배치에 주의해야 함.
