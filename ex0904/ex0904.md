# ex0904 실습 코드 정리

## 파일: `0904-1.ipynb`

```python
age=26
txt=f"I'm {age} years old....."
print(txt)
```

* f-string 을 사용한 포멧 스트링

<br>

```python
price = 59
txt = f"The price is {price:.2f} dollars"
print(txt)
```

* 포멧 스트링 소수 두 자리만 표기

<br>

```python
txt = "banana"
x = txt.center(20)
print(txt.find("an"))
```

* 문자열의 중앙 정렬, 특정 문자열 인덱스 찾기

<br>

```python
thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
}
print(type(thisdict))
```

* 딕셔너리 타입

<br>

---

## 파일: `0904-2.ipynb`

```python
def changecase(func):
    def myinner():
        return func().upper()
    return myinner

@changecase
def myfunction():
    return "Hello Sally"

@changecase
def otherfunction():
    return "I am speed!"

print(myfunction())
print(otherfunction())
```

* 데코레이터

<br>

```python
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the printname method:

x = Person("John", "Doe")
x.printname()
```

* 클래스와 객체

<br>

```python
import numpy

arr = numpy.array([1, 2, 3, 4, 5])

print(arr)
```

* numpy 배열

<br>

```python
import numpy as np

arr = np.array([[1,2,3,4,5], [6,7,8,9,10]])

print('5th element on 2nd row: ', arr[1, 4])
```

* numpy 2차원 배열과 인덱싱

<br>

```python
import numpy as np

arr = np.array([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])

print(arr[0, 1, 2])
```

* numpy 3차원 배열과 인덱싱

<br>

```python
import numpy as np

arr = np.array([[1,2,3,4,5], [6,7,8,9,10]])

print('Last element from 2nd dim: ', arr[1, -1])
```

* 음수 인덱싱 (마지막 원소로부터 카운트)

<br>

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5, 6, 7])

print(arr[1:5])
```

* 슬라이싱 (첫 번째 인덱스는 포함, 마지막 인덱스는 포함하지 않음)

<br>

```python
import numpy as np

arr = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])

print(arr[0:2, 2])
```

* [0, 2], [1, 2], [2, 2]

<br>

```python
import numpy as np

arr = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])

print(arr[0:2, 1:4])
```

* 2차원 슬라이싱

<br>

```python
import numpy as np

arr = np.array([1, 2, 3, 4])

print(arr.dtype)
```

* int64 (배열의 데이터의 타입)

<br>

```python
import numpy as np

arr = np.array(['apple', 'banana', 'cherry'])

print(arr.dtype)
```

* numpy 배열에서는 타입이 같은 원소만 포함할 수 있음 (파이썬에서는 원소간의 타입이 달라도 가능)

<br>

```python
import numpy as np

arr = np.array([1.1, 2.1, 3.1])

newarr = arr.astype('i')

print(newarr)
print(newarr.dtype)


arr = np.array([1.1, 2.1, 3.1])

newarr = arr.astype(int)

print(newarr)
print(newarr.dtype)


arr = np.array([1, 0, 3])

newarr = arr.astype(bool)

print(newarr)
print(newarr.dtype)
```

* 넘파이 배열 형변환

<br>

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
x = arr.copy()
arr[0] = 42

print(arr)
print(x)
```

* 넘파이 배열 복사

<br>

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
x = arr.view()
arr[0] = 42

print(arr)
print(x)
```

* view는 값을 복사하는 것이 아니라 참조, 포인터 같은 개념

<br>

```python
import numpy as np

arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])

print(arr.shape)
```

* 다차원 넘파이 어레이의 모양

<br>

```python
import numpy as np

arr = np.array([1, 2, 3, 4], ndmin=5)

print(arr)
print('shape of array :', arr.shape)
```

* 1차원 배열을 5차원으로 만들기

<br>

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

newarr = arr.reshape(4, 3)

print(newarr)
```

* 모양 변환

<br>


---
