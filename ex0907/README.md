# 수업 내용 정리

## 1. Git 및 GitHub 기본 개념

* Git은 코드 버전을 관리하는 도구이다.
* GitHub 서버가 항상 기준이며, 서버의 코드를 최신 상태로 간주한다.
* 작업 시 기본 순서는 `pull`을 먼저 진행한 후 `push`를 해야 한다.
* 로컬 파일이 심하게 꼬였을 경우 `.git` 폴더를 삭제하여 초기화할 수 있다.

## 2. 백엔드 및 데이터 검증

* Streamlit은 데이터 시각화 및 UI 구성에 쓰이며, 데이터베이스(DB) 처리 등 백엔드 로직 구축을 위해 FastAPI를 함께 사용한다.
* Pydantic을 활용하면 복잡하고 많은 양의 데이터 입력 검증을 `if`문 없이 처리할 수 있다.

## 3. Git 실습 과정 (충돌 및 병합)

1. 로컬 레포지토리 생성 후 GitHub에 `push`
2. GitHub 웹에서 `README.md` 파일 생성
3. GitHub Desktop에서 `fetch` 및 `pull` 실행
* `fetch`: 서버의 변경 사항을 확인하는 작업
* `pull`: 서버의 변경 사항을 로컬로 가져와 합치는 작업


4. 로컬에서 `README.md` 수정 후 `push`
5. GitHub 웹에서 `README.md` 파일 수정
6. 로컬에서도 `README.md` 파일을 수정 (서버와 로컬의 파일 내용이 불일치하는 상태)
7. 로컬에서 `commit` 및 `push` 시도
8. `pull origin`을 수행하여 충돌(Merge) 발생 확인 및 내용 수정
9. `push origin`을 통해 최종 반영


# ex0907 실습 코드 정리

## 파일: `ex0907.ipynb`

```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt

class User(BaseModel):
  # type hint(annotation)
  id: int
  name: str = 'John Doe'
  signup_ts: datetime | None
  tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'name': 'Kevin',
    'signup_ts': '2026-09-07 12:34',
    'tastes': {
        'wine': 9,
        b'cheese': 7, # pydantic이 자동으로 bin 타입을 str으로 변환해줌.
        'cabbage': '1',
    },
}

# User 오브젝트 생성
user = User(**external_data) # **은 딕셔너리 언패킹

print(user.id)
print(user.model_dump())
```

* external_data를 검증 및 변환하여 User 오브젝트를 생성한다.

<br>

```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError

class User(BaseModel):
  id: int
  name: str = 'John Doe'
  signup_ts: datetime | None
  tastes: dict[str, PositiveInt]

external_data = {'id': 'not an int', 'tastes': {}}

try:
  User(**external_data)
except ValidationError as e:
  print(e.errors())
```

* 변환이 불가능한 값이 넘어오자 ValidationError가 발생하는 모습

<br>

```python
from typing import Annotated, Literal

from annotated_types import Gt

from pydantic import BaseModel


class Fruit(BaseModel):
  name: str
  color: Literal['red', 'green']
  weight: Annotated[float, Gt(0)]
  bazam: dict[str, list[tuple[int, bool, float]]]


print(
    Fruit(
        name='Apple',
        color='red',
        weight=4.2,
        bazam={'footbar': [(1, True, 0.1)]}
    )
)
```

* 객체 만들기
* 가능한 값 범위
* Gt(0) == Greater than 0

<br>

```python
from datetime import datetime
from pydantic import BaseModel

class Meeting(BaseModel):
  when: datetime
  where: bytes
  why: str = 'No idea'

m = Meeting(when='2020-01-01T12:00', where='home')
print(m.model_dump(exclude_unset=True))
print(m.model_dump(exclude={'where'}, mode='json'))
print(m.model_dump_json(exclude_defaults=True))
```

* pydantic 객체 Serialize

<br>

```python
from datetime import datetime
from pydantic import BaseModel

class Address(BaseModel):
  street: str
  city: str
  zipcode: str


class Meeting(BaseModel):
  when: datetime
  where: Address
  why: str = 'No idea'

print(Meeting.model_json_schema())
```

*  Pydantic 모델(Meeting)의 데이터 구조와 제약 조건을 JSON 스키마(JSON Schema)라는 표준 형식으로 추출하여 출력하는 코드

<br>

```python
from datetime import datetime
from pydantic import BaseModel, ValidationError
class Meeting(BaseModel):
    when: datetime
    where: bytes
m = Meeting.model_validate({'when': '2020-01-01T12:00', 'where': 'home'})
print(m)
#> when=datetime.datetime(2020, 1, 1, 12, 0) where=b'home'
try:
    m = Meeting.model_validate(
        {'when': '2020-01-01T12:00', 'where': 'home'}, strict=True
    )
except ValidationError as e:
    print(e)
    """
    2 validation errors for Meeting
    when
      Input should be a valid datetime [type=datetime_type, input_value='2020-01-01T12:00', input_type=str]
    where
      Input should be a valid bytes [type=bytes_type, input_value='home', input_type=str]
    """
m_json = Meeting.model_validate_json(
    '{"when": "2020-01-01T12:00", "where": "home"}'
)
print(m_json)
#> when=datetime.datetime(2020, 1, 1, 12, 0) where=b'home'
```

* 예외 처리

<br>

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: int
    name: str = 'Jane Doe'

    model_config = ConfigDict(str_max_length=10)


user = User(id='123')
print(user)
print(type(user))
print(type(user.id), user.id)
print(type(user.name), user.name)
```

* User 객체의 멤버 변수들과 타입

<br>

---


## 파일: `pydantic_validation.py`

```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt

class User(BaseModel):
  # type hint(annotation)
  id: int
  name: str = 'John Doe'
  signup_ts: datetime | None
  tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'name': 'Kevin',
    'signup_ts': '2026-09-07 12:34',
    'tastes': {
        'wine': 9,
        b'cheese': 7, # pydantic이 자동으로 bin 타입을 str으로 변환해줌.
        'cabbage': '1',
    },
}

# User 오브젝트 생성
user = User(**external_data) # **은 딕셔너리 언패킹

print(user.id)
print(user.model_dump())
```

* pydantic 검증 및 자동 변환 예시

<br>

---


**오늘 배운 내용: Pydantic 기초**

**1. 모델 생성 & 타입 지정**

```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt

class User(BaseModel):
  # type hint(annotation)
  id: int
  name: str = 'John Doe'
  signup_ts: datetime | None
  tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'name': 'Kevin',
    'signup_ts': '2026-09-07 12:34',
    'tastes': {
        'wine': 9,
        b'cheese': 7, # pydantic이 자동으로 bin 타입을 str으로 변환해줌.
        'cabbage': '1',
    },
}

# User 오브젝트 생성
user = User(**external_data) # **은 딕셔너리 언패킹

print(user.id)
print(user.model_dump())
```

* `BaseModel` 상속받아 데이터 모델(클래스) 정의


* `int`, `str`, `datetime` 등 타입 힌트로 자료형 명시


* `**` (딕셔너리 언패킹) 써서 딕셔너리 데이터를 객체에 바로 넣음



**2. 데이터 검증(Validation)**
```
from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError

class User(BaseModel):
  id: int
  name: str = 'John Doe'
  signup_ts: datetime | None
  tastes: dict[str, PositiveInt]

external_data = {'id': 'not an int', 'tastes': {}}

try:
  User(**external_data)
except ValidationError as e:
  print(e.errors())
```

* 데이터 타입이 달라도 Pydantic이 알아서 자동 형변환 시도함 (ex. 텍스트형 숫자 -> int)


* 실패하거나 필수값 없으면 `ValidationError` 에러 발생


* `strict=True` 주면 자동 변환 없이 엄격하게 타입 검사함


* `ConfigDict`로 `str_max_length` 같은 세부 규칙 추가 가능



**3. 중첩 모델 & 스키마**
```
from datetime import datetime
from pydantic import BaseModel

class Address(BaseModel):
  street: str
  city: str
  zipcode: str


class Meeting(BaseModel):
  when: datetime
  where: Address
  why: str = 'No idea'

print(Meeting.model_json_schema())
```
* 모델 안에 또 다른 모델 넣어서 중첩 구조 만들기 가능 (ex. `Meeting` 안에 `Address`)


* `model_json_schema()` 호출하면 모델 구조를 JSON 스키마로 뽑아줌



**4. 변환(Serialization)**
```
from datetime import datetime
from pydantic import BaseModel

class Meeting(BaseModel):
  when: datetime
  where: bytes
  why: str = 'No idea'

m = Meeting(when='2020-01-01T12:00', where='home')
print(m.model_dump(exclude_unset=True))
print(m.model_dump(exclude={'where'}, mode='json'))
print(m.model_dump_json(exclude_defaults=True))
```
* `model_dump()`: 모델 객체를 딕셔너리로 변환


* `model_dump_json()`: JSON 텍스트로 변환


* `exclude_unset=True`, `exclude_defaults=True` 옵션 쓰면 세팅 안 한 값이나 기본값 빼고 추출 가능