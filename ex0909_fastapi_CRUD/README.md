# 파이썬 및 FastAPI 백엔드 프로그래밍 기술 요약 노트

## 1. 파이썬 프로젝트 의존성 및 패키지 관리

### 1.1 `requirements.txt` 및 `uv.lock` 비교
파이썬 프로젝트의 패키지 의존성을 관리하는 두 도구의 주요 특징과 차이점은 다음과 같다.

| 구분 | `requirements.txt` | `uv.lock` |
| :--- | :--- | :--- |
| **사용 도구** | `pip` (파이썬 기본 패키지 매니저) | `uv` (Astral 개발 초고속 패키지 매니저) |
| **주요 목적** | 설치할 패키지 목록 명시 | 재현 가능한 의존성 상태 잠금(Lock) |
| **파일 형식** | 단문 텍스트 (Plain Text) | 구조화된 포맷 (TOML) |
| **관리 주체** | 수동 작성 또는 `pip freeze`로 생성 | `uv` 도구가 자동 생성 및 업데이트 |
| **보안 및 해시** | 기본 미지원 (별도 옵션 필요) | 모든 패키지의 정확한 버전 및 무결성 해시 포함 |
| **크로스 플랫폼** | OS별 패키지 충돌 방지 어려움 | Windows, macOS, Linux 동시 지원 |

* **`requirements.txt`**: 최상위 패키지 위주로 기록되며, 하위 의존성 버전의 변동으로 인해 설치 시점마다 환경이 불일치할 위험 존재.
* **`uv.lock`**: 모든 하위 의존성의 정확한 버전과 해시값을 기록하여 실행 환경 간 100% 동일한 의존성을 보장.

### 1.2 두 파일의 프로젝트 내 공존 이유
1. **배포 환경 호환성**: 개발 환경에서는 `uv.lock`을 통해 엄격한 의존성을 관리하고, `pip` 기반의 CI/CD 파이프라인이나 클라우드 배포 환경(AWS Elastic Beanstalk 등)을 위해 `requirements.txt`로 내보내기(Export)를 진행함.
2. **마이그레이션 및 하위 호환성**: 기존 `pip` 중심 프로젝트를 `uv`로 전환하는 과정에서 `uv`를 사용하지 않는 기여자를 위한 보조 파일로 유지함.
3. **입력과 출력의 분리**: `requirements.txt`에 상위 의존성을 입력(Input)으로 정의하고, `uv`를 통해 해석된 정교한 의존성을 `uv.lock`(Output)으로 관리함.

---

## 2. RESTful API 설계 및 FastAPI 파라미터 처리

### 2.1 HTTP 메소드 정의 및 활용
웹 애플리케이션에서 자원(Resource)을 조작하기 위해 사용하는 주요 HTTP 메소드의 역할은 다음과 같다.

* **GET**: 데이터 조회 (Read)
* **POST**: 새로운 데이터 생성 (Create)
* **PUT**: 데이터 전체 수정 및 교체 (Update)
* **PATCH**: 데이터 일부 수정 (Update)
* **DELETE**: 데이터 삭제 (Delete)
* **OPTIONS**: 서버가 지원하는 통신 옵션 및 허용 메소드 확인 (`Allow` 헤더 활용)
* **HEAD**: GET과 동일하나 응답 본문(Body)을 제외하고 헤더만 반환
* **TRACE**: 클라이언트가 전송한 요청 헤더를 에코(Echo) 형태로 반환 (디버깅 용도)

### 2.2 FastAPI 파라미터 자동 분류 기준
FastAPI는 함수 매개변수의 선언 형태 및 타입 힌트에 따라 요청 데이터 위치를 자동으로 인식함.

* **Path Parameter (경로 매개변수)**: URL 경로에 선언된 변수 (예: `/items/{item_id}`)
* **Query Parameter (쿼리 매개변수)**: URL 쿼리스트링에 포함된 단일 기본 타입 변수 (예: `q: str | None = None`)
* **Request Body (요청 본문)**: Pydantic `BaseModel`을 상속받은 객체 타입 선언 시 JSON Body로 처리

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,       # Path Parameter (URL 경로)
    is_admin: bool,     # Query Parameter (URL 쿼리스트링 ?is_admin=true)
    item: Item          # Request Body (JSON 데이터)
):
    pass
```

### 2.3 데이터 전달 위치 차이에 따른 보안 및 작동 구조
* **POST 연산에서 Request Body 사용 필수성**:
  * 로그인 등 민감 데이터 전송 시 Query Parameter(URL)를 사용할 경우, 브라우저 방문 기록, 웹 서버 접근 로그(Access Log)에 평문으로 기록되는 보안 위험이 발생함.
  * Request Body 데이터는 HTTPS 통신 시 완전 암호화되어 전송되므로 보안성이 확보됨.
* **타입/위치 불일치 처리**:
  * 클라이언트가 Request Body에 전달해야 할 데이터를 Query Parameter로 보낼 경우, FastAPI는 서버 내부 오류를 발생시키지 않고 `422 Unprocessable Entity` 에러를 자동 반환하여 요청을 차단함.

### 2.4 Pydantic V2 주요 변경 사항
FastAPI의 데이터 검증 라이브러리인 Pydantic 버전 업데이트(V1 $\rightarrow$ V2)에 따른 메서드 변경 사항은 다음과 같다.

* **`model.dict()` $\rightarrow$ `model.model_dump()`**: 모델 객체를 파이썬 딕셔너리로 변환
* **`model.json()` $\rightarrow$ `model.model_dump_json()`**: 모델 객체를 JSON 문자열로 변환

---

## 3. 파이썬 문법 및 API 개발 실무 기술

### 3.1 수치 연산 및 자동 형변환
* **일반 나눗셈 (`/`)**: 정수끼리의 연산이라도 결과는 항상 실수(`float`) 타입을 반환함. (C언어와 달리 명시적 캐스팅 불필요)
* **몫 나눗셈 (`//`)**: 소수점을 버리고 정수 몫만 반환함.
* **자동 형변환 (Implicit Casting)**: 수식 내 `float` 타입이 하나라도 포함될 경우 연산 결과는 `float`로 자동 변환됨.

### 3.2 딕셔너리 조작 방식 비교

| 구분 | 직접 키 대입 (`d[key] = value`) | `update()` 메서드 (`d.update(...)`) |
| :--- | :--- | :--- |
| **주요 목적** | 단일 항목 추가 및 수정 | 다중 항목 추가, 수정 및 병합 |
| **입력 형태** | `d['a'] = 1` | 딕셔너리, 키워드 인자(`a=1`), 튜플 리스트 |
| **키 제약 조건** | 모든 Hashable 타입 가능 | 키워드 인자 사용 시 문자열 키만 가능 |
| **성능 특징** | 단일 처리 시 메서드 호출 오버헤드가 없어 빠름 | 다중 항목 처리 시 반복문 대입보다 효율적 |

### 3.3 Enum 활용 및 API 계산기 구현 패턴
* **Enum 클래스 설계**:
  * 파이썬 표준 규격(PEP 8)에 따라 Enum 멤버 변수명은 상수를 의미하므로 대문자로 명명함 (`PLUS`, `MINUS` 등).
  * `str`과 `Enum`을 다중 상속하여 문자열 비교 및 Serialization 편의성을 확보함.
* **전역 객체 재사용**:
  * 매핑 딕셔너리나 연산 람다 함수 테이블은 요청 함수 내부가 아닌 전역(Global) 공간에 선언하여, 매 요청 시 객체가 재생성되는 오버헤드를 방지함.
* **예외 처리 구조화**:
  * 0으로 나누기 연산 발생 시 파이썬 기본 `ZeroDivisionError`(500 Internal Server Error)가 발생하지 않도록 `HTTPException(status_code=400)`을 명시적으로 제어함.

```python
from enum import Enum
from fastapi import FastAPI, HTTPException

app = FastAPI()

class Operator(str, Enum):
    PLUS = "plus"
    MINUS = "minus"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

# 전역 연산 매핑 테이블
CALCULATOR_MAP = {
    Operator.PLUS: lambda x, y: x + y,
    Operator.MINUS: lambda x, y: x - y,
    Operator.MULTIPLY: lambda x, y: x * y,
    Operator.DIVIDE: lambda x, y: x / y,
}

@app.get("/calculator/{operator}")
async def calculator(operator: Operator, operand1: float, operand2: float):
    if operator == Operator.DIVIDE and operand2 == 0:
        raise HTTPException(status_code=400, detail="0으로 나눌 수 없습니다.")
    
    result = CALCULATOR_MAP[operator](operand1, operand2)
    return {"result": result}
```

### 3.4 FastAPI 실행 및 디버깅 가이드
* **`Could not find FastAPI app in module` 오류 발생 원인**:
  1. 소스코드 내 `app = FastAPI()` 인스턴스가 선언되지 않았거나 변수명이 다른 경우 (`--app` 옵션 필요).
  2. 에디터에서 코드 수정 후 파일 저장이 누락된 경우.
  3. 모듈명 또는 변수명 대소문자 오타.
* **KeyError 발생 원인**:
  * Enum 객체를 키로 사용하는 딕셔너리에 `str(operator)` 형태의 문자열로 접근할 경우 Key 불일치로 인한 `KeyError`가 발생하므로 Enum 객체 자체를 키로 참조해야 함.
* **URL 엔드포인트 경로 관례**:
  * `@app.get("/bye")`와 같이 URL 끝의 슬래시(`/`)를 제거하는 것이 표준적이며, 슬래시가 포함될 경우 불필요한 HTTP 리다이렉트 통신이 발생할 수 있음.

---

## 4. 개발 도구 활용 (VS Code)

* **찾기/바꾸기 단축키**:
  * Windows/Linux: `Ctrl + H`
  * macOS: `Cmd + Option + F`
* **일괄 변경 실행**: `Ctrl + Alt + Enter` (macOS: `Cmd + Enter`)
* **검색 옵션**: 대소문자 구분(`Aa`), 전체 단어 일치(`ab`), 정규식 사용(`.*`)


## 비동기 및 멀티태스킹 기술 요약

참고 문서: async와멀티태스킹_temp.pdf

### 비동기 처리의 한계 및 지연 발생 원인
비동기 기술은 대기 시간(I/O Wait)을 버리지 않고 활용하는 방식일 뿐, CPU 실제 연산 시간이나 시스템 전체 한계 용량을 물리적으로 늘려주지 않음.
FastAPI의 비동기 이벤트 루프는 기본적으로 단일 스레드(Single Thread)로 작동하므로, 다음과 같은 상황에서 지연이 발생함.

1. CPU 연산 병목 (CPU-bound Operations)
- 이미지 변환, 암호화, 대용량 JSON 파싱, AI 모델 추론 등 CPU를 100% 점유하는 연산 수행 시 이벤트 루프 자체가 정지함.
- 연산 중 유입된 다른 사용자들의 요청은 대기열(Queue)에 적재되며 지연이 발생함.

2. 하위 자원(I/O Resource)의 한계
- 비동기 서버가 다수의 동시 요청을 수용하더라도, DB의 커넥션 풀(Connection Pool) 등 하위 자원이 제한적일 경우 초과한 요청은 응답을 얻기 위해 순차적으로 대기해야 함.

### 동기(Sync) vs 비동기(Async) 특성 비교

| 구분 | 동기 (Sync Multi-Thread) | 비동기 (Async Event-Loop) |
| :--- | :--- | :--- |
| **지연 원인** | 스레드 개수 부족 및 스레드 교체(Context Switching) 과부하 | CPU 연산 독점 및 하위 시스템(DB/네트워크) 병목 |
| **대기 처리** | 요청마다 스레드를 할당하며, 스레드 고갈 시 접속 거부 및 타임아웃 발생 | 단일 스레드가 적은 메모리로 대량 접속(Socket)을 유지하며 대기열 생성 |
| **효율성** | 단순 대기(I/O) 상황에서도 메모리 자원을 크게 소모함 | 단순 대기 상황에서는 자원 소모가 거의 없이 순차 처리됨 |

### 운영 환경에서의 구조
- 실제 운영 환경에서는 대량 접속 시 지연을 방지하기 위해 비동기 방식 단독으로 운용하지 않음.
- 반드시 멀티프로세싱 및 구조적 확장 기술을 결합하여 시스템을 설계함.
