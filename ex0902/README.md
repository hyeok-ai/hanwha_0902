# ex0902 실습 코드 정리

## 파일: `0902_1.ipynb`

```python
def myfunc():
  print("hello")

myfunc()
```

* 함수의 정의와 실행

<br>

```python
def cel(f):
  return f+100

print(cel(77))

def f1(su):
  return su+100

def f2(su):
  return su-100

def f3(su):
  return su*100

def f4(su):
  return su/100

print( f1(5) )
print( f2(5) )
print( f3(5) )
print( f4(5) )
```

* 함수의 정의와 호출, 반환 값 출력

<br>

```python
print(list(range(5, 20, 6)))
```

* list와 range의 사용

<br>

```python
import numpy as np

arr = np.array([1,2,3,4,5])

print(arr)

print(type(arr))
```

* numpy 배열

<br>

```python
import pandas
mydataset = {
    'cars': ["BMW", "Volvo", "Ford"],
    'passings': [3, 7, 2]
}

myvar = pandas.DataFrame(mydataset)

print(myvar)
```

* pandas의 데이터 프레임 (엑셀 시트, csv 같은거)

<br>


---

## 파일: `ctrlcv.py`

```python
title = "AI 서비스 백엔드 프로그래밍 실무"
line = "="*10
time = 8
myList = ["파이썬 기본 문법", "클래스", "데코레이터", "예외 처리", "로깅"]
print(title)
print(line)
print(myList[0], time)
print(myList[1], time)
print(myList[2], time)
print(myList[3], time)
print(myList[4], time)
```

* 변수, 배열, 인덱싱을 통한 중복 출력 처리

<br>

---

## 파일: `ctrlcv2.py`

```python
title = "AI 서비스 백엔드 프로그래밍 실무"
line = "="*10
time = 8
myList = ["파이썬 기본 문법", "클래스", "데코레이터", "예외 처리", "로깅"]
print(title)
print(line)

for lecture in myList:
    print(lecture, ", 시간: ", time, sep='')
```

* for 문을 사용한 중복 출력 처리

<br>

---

## 파일: `ctrlcv3.py`

```python
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit-32)*5/9


print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))
```

* 함수를 통한 화씨와 섭씨의 변환

<br>

---

## 파일: `ex1_0902.ipynb`

```python
print("테스트")
x="John"
y='John'
print(x,y)
x=10
y=20
print(x+y)
x=5
y="John"
print(x+y)
```

* 변수의 수사, 문자열 대입과 값 출력

<br>

---


## 파일: `test.py`

```python
title = "AI 서비스 백엔드 프로그래밍 실무"
lectures = [("파이썬 기본 문법", 8), ("클래스", 8), ("데코레이터", 8), ("예외 처리", 8), ("로깅", 8)]

line = "="*10

print(title)
print(line)

format_string = "{}, 시간:{}"

for lecture in lectures:
    print(format_string.format(*lecture))
```

* 튜플로 이루어진 배열과 for 문을 통한 출력
* 배열 언패킹(*)을 통해 포맷 스트링 채우기

<br>

---
