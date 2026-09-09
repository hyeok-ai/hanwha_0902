import json

# str 타입의 json 문자열
x =  '{ "name":"John", "age":30, "city":"New York"}'

# json 문자열을 딕셔너리로 import
y = json.loads(x)

# <class 'dict'>
print(type(y))

# 30
print(y["age"])