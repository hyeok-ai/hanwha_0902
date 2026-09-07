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