
---

### 1. 개발 및 협업 프로세스

* **개발 환경 설정**: 작업 시 자주 사용하는 IDE Extension 종류 목록화 및 기록 권장. Docker 활용 필수.
* **프로젝트 구조화**: 팀 프로젝트 진행 시 전체 시스템을 기능 단위로 분할하여 작업. 환경 설정 파일 등은 매니저(관리자)가 중앙 통제 및 관리.
* **기획 및 문서화**:
* 개발 착수 전 사전 초안 작성 필수 (협업 및 역할 분담의 기준점).
* 실무에서는 API 기획 문서 등을 사전에 전달하고 공유함.


* **이슈 트래킹 및 능동적 대처**: 담당한 역할 내 누락된 기능 발견 시, 담당자가 선제적으로 기능 추가를 제안하고 공식 도큐먼트에 반영. 참고 링크 목록화 유지.

### 2. FastAPI 개요 및 관련 도구

* **FastAPI 특징**: 자체 내장 웹 서버를 포함하지 않는 순수 웹 프레임워크. 작성한 코드를 실행하고 구동할 별도의 '서버 프로그램' 필요.
* **학습 자료**: 공식 자습서 및 사용자 안내서 위주 학습 (참고: [https://fastapi.tiangolo.com/ko/tutorial/](https://fastapi.tiangolo.com/ko/tutorial/))
* **API 문서화 및 테스트 도구**:
* **Swagger**: 개발자가 작성한 API를 웹 브라우저상에서 시각적으로 확인하고 직접 테스트할 수 있도록 지원하는 자동 문서화 도구. (`http://localhost:8000/docs` 경로로 접속 시 확인 가능)
* **Postman**: 개발자들이 API를 전문적으로 테스트하고 관리하기 위해 사용하는 독립적인 소프트웨어.



### 3. 서버 구동 환경 (ASGI 및 Uvicorn)

* **네트워크 기초**: `127.0.0.1`은 `localhost`와 동일한 루프백 IP.
* **ASGI (Asynchronous Server Gateway Interface)**: 파이썬 비동기 웹 프레임워크(FastAPI 등)와 웹 서버 간의 통신을 위한 표준 규격.
* **Uvicorn**: ASGI 규격을 따르는 초고속 웹 서버. FastAPI 코드를 실제로 작동시키고 외부의 인터넷 요청을 수신 및 처리함.
* **패키지 관리 도구 및 설치**:
* `uv`: 파이썬 패키지 및 프로젝트를 관리하는 최신 도구. (명령어: `uv add "fastapi[standard]"`)
* `pip`: 기존 패키지 관리자. (명령어: `pip install "fastapi[standard]"`)


* **서버 실행 명령어**:
* `fastapi dev main.py`: 내부적으로 Uvicorn을 사용하나 사용자에게 복잡한 문법을 감추고 편의성을 제공하는 명령어 ([https://fastapi.tiangolo.com/ko/#create-it](https://www.google.com/search?q=https://fastapi.tiangolo.com/ko/%23create-it)).
* `uvicorn main:app --reload`: FastAPI 초기부터 사용되어 온 가장 표준적인 Uvicorn 직접 실행 명령어.



### 4. 매개변수 처리 및 유효성 검사 (Validation)

* **내부 검증 로직**: FastAPI는 내부적으로 Pydantic 모델을 사용하여 데이터 유효성 검증 수행.
* **경로 매개변수 (Path Parameters)**:
* `Enum` 클래스(열거형)를 상속받아 경로 매개변수로 지정 가능.
* 허용된 열거형 데이터 외의 값(예: `alexnetff`)을 입력할 경우 유효성 검사 에러(ValidationError) 발생.


* **쿼리 매개변수 (Query Parameters)**:
* 엔드포인트 함수의 파라미터 중 경로 매개변수로 지정되지 않은 변수는 자동으로 쿼리 매개변수로 인식됨.
* URL 예시: `[http://127.0.0.1:8000/items/?skip=1&limit=2](http://127.0.0.1:8000/items/?skip=1&limit=2)`


* **API 테스트 방식**: Swagger UI 의존 외에도, URL에 파라미터를 직접 입력하는 방식의 테스트를 병행하여 데이터 구조에 대한 감각을 기르는 것 권장.

### 5. 파이썬 타입 힌팅 (Type Hinting) 유의사항

* **선택적 매개변수(Optional Parameter) 문법**: `q: str | None = None` (Python 3.10+ 기준)
* `(str | None)`: 해당 변수의 타입이 `str` 또는 `None`임을 명시.
* `= None`: 변수의 기본값을 `None`으로 할당.


* **타입 표기 불일치 문제 (`q: str = None`)**:
* 의미: 변수 타입을 `str`로 엄격히 선언해 놓고 기본값으로 `None`을 부여함.
* 문제점: IDE 또는 정적 타입 검사기(Mypy 등)에서 'str 타입 변수에 None을 할당할 수 없음'이라는 타입 불일치 경고 발생 유발.



### 6. 기타 기술 개념

* **자바(Java)의 원시 타입 (Primitive Type)**: 가공되지 않은 순수한 데이터 값 자체를 메모리(Stack) 영역에 직접 저장하는 가장 기본적인 데이터 타입.