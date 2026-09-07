# Pydantic

## json

----

* 예시 코드


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