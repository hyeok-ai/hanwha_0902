import json

# a Python object (dict):
x = {
  "name": "John",
  "age": 30,
  "city": "New York"
}

# convert into JSON:
y = json.dumps(x)

# <class 'str'>
print(type(y))

# the result is a JSON string:
print(y)
