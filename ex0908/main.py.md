**파이썬 문법 측면 (Python Syntax)**

* **`from fastapi import FastAPI`**: 외부 패키지 모듈을 가져옵니다. `fastapi` 라이브러리에서 `FastAPI` 클래스를 현재 스크립트로 불러옵니다.
* **`app = FastAPI()`**: 클래스 인스턴스화입니다. 메모리에 `FastAPI` 객체를 생성하고 `app`이라는 변수에 할당합니다.
* **`@app.get(...)`**: **데코레이터(Decorator)** 문법입니다. 기호 `@`를 사용하여 바로 아래에 정의된 함수(`read_root`, `read_item`)를 감싸며, 원본 함수 코드를 수정하지 않고 외부 로직(여기서는 URL 매핑 기능)을 덧붙입니다.
* **`item_id: int`**: 타입 힌트(Type Hint)입니다. 해당 변수가 정수형 객체임을 코드 상에 명시하여 가독성을 높이고 정적 분석기가 오류를 찾을 수 있게 돕습니다.
* **`str | None`**: 파이썬 3.10부터 도입된 **유니온(Union) 타입 연산자**입니다. 변수 `q`가 문자열(`str`) 자료형일 수도 있고, 값이 없을 수도(`None`) 있다는 뜻입니다. (이전 버전의 `typing.Optional[str]`과 동일합니다.)
* **`q ... = None`**: 파이썬 함수의 **기본 인자값(Default Argument)** 설정입니다. 함수가 호출될 때 `q`에 대한 값이 전달되지 않으면 자동으로 `None`을 할당합니다.
* **`return {"Hello": "World"}`**: 중괄호 `{}`를 사용해 키(Key)와 값(Value)으로 이루어진 파이썬 고유 자료구조인 딕셔너리(Dictionary)를 생성하여 반환합니다.

---

**FastAPI 프레임워크 측면 (Framework Features)**

* **라우팅 (Routing):** `@app.get("/")`는 클라이언트가 웹 서버의 최상위 주소(`/`)로 HTTP `GET` 요청을 보낼 때, 이를 `read_root()` 함수가 처리하도록 길을 연결해 줍니다.
* **자동 JSON 직렬화:** 프레임워크는 함수가 반환한 파이썬 딕셔너리를 자동으로 JSON 형식(`application/json`)으로 변환하여 클라이언트 브라우저나 앱으로 응답합니다. 개발자가 별도로 `json.dumps()`를 호출할 필요가 없습니다.
* **경로 매개변수 (Path Parameters):** URL 경로 내의 `{item_id}`는 동적인 값입니다. 클라이언트가 `/items/5`로 접속하면, 프레임워크가 숫자 `5`를 추출하여 `read_item` 함수의 `item_id` 인자로 꽂아줍니다.
* **데이터 검증 및 형변환 (Data Validation):** 파이썬의 타입 힌트(`int`)를 단순히 읽기용으로 쓰지 않고, 프레임워크가 능동적으로 활용합니다. URL을 통해 들어온 데이터는 기본적으로 문자열이지만, FastAPI가 이를 정수로 자동 변환합니다. 만약 클라이언트가 숫자가 아닌 값(예: `/items/apple`)을 요청하면, 코드가 실행되기도 전에 프레임워크가 알아서 **HTTP 422 (Unprocessable Entity) 에러**를 반환합니다.
* **쿼리 매개변수 (Query Parameters):** 함수 인자인 `q`는 URL 경로에 `{q}` 형태로 존재하지 않습니다. 이 경우 FastAPI는 자동으로 이를 쿼리 스트링(예: `/items/5?q=keyword`)으로 인식하여 처리합니다.