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