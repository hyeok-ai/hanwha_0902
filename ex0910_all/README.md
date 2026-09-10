# 기술 노트 정리

## 1. 데이터 분석 라이브러리

* **NumPy (np)**: 복잡한 수학 연산 및 배열 처리 담당.


* **Pandas (pd)**: 표(Table) 형태의 데이터 처리에 특화.


* **Matplotlib (plt)**: 완성된 데이터를 시각화.



## 2. 서버 실행 및 배포

* 프론트엔드와 백엔드 폴더를 각각 분리하여 두 개의 서버를 실행하는 방식 사용 가능.


* FastAPI 서버 실행 명령어: `uvicorn main:app --reload` (또는 `--released`).


* Streamlit 서버 실행 명령어: `streamlit run app.py`.



## 3. Python 주요 개념 및 문법

### 동기와 비동기

* 두 방식 자체의 처리 속도는 동일함.


* **동기**: 주어진 일을 끝까지 해결하며, 해당 작업이 끝날 때까지 다른 작업을 수행하지 않음.


* **비동기**: 작업이 몰릴 때 효율적인 처리를 위해 사용함.



### Pydantic 사용 목적

* 타입 검증(Type validation/check), 자동 형변환, dict 형 덤프(dump) 기능 제공.


* 복잡한 `if` 조건문 없이 편리하게 데이터를 검증함.


* 잘못된 데이터 실행으로 인한 위험을 방지하고 즉각적인 오류 발생을 유도함.



### 기본 문법 특징

* `match` 문: C언어의 `switch` 문과 유사한 기능.


* 다중 변수 할당: `num1, num2, num3 = 1, 2, 3` 형태로 여러 변수에 동시에 값 할당 가능.


* **바다코끼리 연산자 (`:=`)**: 표현식(Expression) 안에서 변수 할당과 반환을 동시에 처리 (Python 3.8+ 도입).


* 조건문(`if`), 반복문(`while`), 리스트 컴프리헨션에서 중복 연산을 방지하고 코드 구조를 간소화함.


* 우선순위가 낮으므로 조건 판단 시 전체를 괄호 `()`로 감싸야 함.





### 파이썬에서의 상수(Constant)

* 문법적으로 값을 변경하지 못하게 막는 상수 키워드(`const`, `final` 등)가 존재하지 않음.


* **대문자 네이밍 관례 (PEP 8)**: 변수명을 모두 대문자와 밑줄(`_`)로 작성하여 상수로 취급하자는 암묵적 규칙 사용.


* **`typing.Final`**: 정적 타입 체커에서 경고를 띄워 실수를 방지하는 용도이며, 런타임 실행 시점에는 여전히 값 변경 가능 (Python 3.8+).



### 다중 루프 탈출 기법

* 기본 `break` 문은 가장 안쪽에 있는 루프 하나만 탈출함.


* 중첩 루프에서 한 번에 탈출하기 위한 4가지 방법:
1. **함수로 분리하여 `return` 사용 (가장 추천)**: 복잡한 루프를 함수로 묶고 `return`으로 즉시 종료.


2. **`itertools.product` 사용**: 중첩 `for` 문을 단일 루프로 평탄화하여 단일 `break`로 탈출.


3. **플래그(Flag) 변수 사용**: 루프 진행 상태 변수를 확인하여 연쇄적으로 `break` 호출.


4. **커스텀 예외(Exception) 발생**: 다중 루프를 `try-except`로 감싸고 `raise`를 통해 단번에 점프.





## 4. Git 명령어

* `git clone`: 원격 저장소의 전체 코드와 히스토리를 로컬 컴퓨터로 최초 다운로드할 때 사용.


* `git pull`: 이미 복사된 로컬 저장소에 원격 저장소의 최신 변경 사항만 가져와 병합할 때 사용.



## 5. HTTP 통신 및 파일 송수신

### `requests.post()` 요청 바디 포맷

* `json=`: JSON 문자열 전송, `Content-Type: application/json` 자동 설정.


* `data=` (dict 형태): Form 인코딩 전송, `Content-Type: application/x-www-form-urlencoded` 자동 설정.


* `data=` (문자열/바이트): 원본 그대로 전송, `Content-Type` 직접 지정 필요.


* `files=`: 바이너리 멀티파트 전송, `Content-Type: multipart/form-data` 자동 설정.



### 파일 업로드 / 다운로드 표준

* **업로드 (Upload)**:
* 메소드: `POST` (또는 `PUT`).


* Content-Type: `multipart/form-data` (파일과 일반 데이터 동시 전송) 또는 `application/octet-stream` (순수 바이너리).




* **다운로드 (Download)**:
* 메소드: `GET`.


* 전송 형태: 바이너리 스트림 (Binary Stream).


* 필수 헤더: `Content-Type` (파일 종류 명시), `Content-Disposition: attachment; filename="..."` (브라우저 다운로드 창 유도).





### Python 및 FastAPI 파일 처리 실무

* **`requests` 파일 송수신**:
* 업로드: `POST` 요청 시 `files` 파라미터로 파일 객체 전달.


* 다운로드: `GET` 요청에 `stream=True` 옵션을 주고 `iter_content`를 통해 청크(Chunk) 단위로 메모리에 나누어 저장 권장.




* **FastAPI의 파일 처리**:
* 클라이언트로부터 파일 수신 시 `UploadFile` 객체 활용 (대용량 파일 업로드 시 서버 메모리 고갈 방지를 위해 디스크 임시 저장 기능 제공).


* 클라이언트로 파일 송신 시 `FileResponse` 활용 (다운로드 헤더 자동 구성 및 응답).