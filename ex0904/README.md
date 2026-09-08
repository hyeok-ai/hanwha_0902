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


# navigation-test 실습 코드 정리


## 파일: `streamlit_app.py`

```python
import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Requester", "Responder", "Admin"]


def login():

    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
request_1 = st.Page(
    "request/request_1.py",
    title="Request 1",
    icon=":material/help:",
    default=(role == "Requester"),
)
request_2 = st.Page(
    "request/request_2.py", title="Request 2", icon=":material/bug_report:"
)
respond_1 = st.Page(
    "respond/respond_1.py",
    title="Respond 1",
    icon=":material/healing:",
    default=(role == "Responder"),
)
respond_2 = st.Page(
    "respond/respond_2.py", title="Respond 2", icon=":material/handyman:"
)
admin_1 = st.Page(
    "admin/admin_1.py",
    title="Admin 1",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")

account_pages = [logout_page, settings]
request_pages = [request_1, request_2]
respond_pages = [respond_1, respond_2]
admin_pages = [admin_1, admin_2]

st.title("Request manager")
st.logo("images/icon_hanwha.png", icon_image="images/icon_hanwha.png")

page_dict = {}
if st.session_state.role in ["Requester", "Admin"]:
    page_dict["Request"] = request_pages
if st.session_state.role in ["Responder", "Admin"]:
    page_dict["Respond"] = respond_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
```

**코드 개요**
Streamlit을 사용하여 사용자 역할(Role)에 따라 접근 가능한 메뉴가 동적으로 바뀌는 멀티 페이지 네비게이션 앱을 구현한 코드이다.

**핵심 기능 설명**

* **세션 상태 관리:** `st.session_state.role`을 사용하여 사용자의 로그인 상태와 역할(Requester, Responder, Admin 등)을 저장하고 유지한다.
* **로그인 및 로그아웃:** `login()`, `logout()` 함수에서 선택된 역할을 세션에 할당하거나 해제한 후, `st.rerun()`을 호출해 앱을 즉시 새로고침한다.
* **페이지 객체 정의:** `st.Page()`를 사용해 실행할 파일 경로, 제목, 아이콘을 지정한다. 역할에 따라 로그인 직후 처음 보여줄 화면을 `default` 옵션으로 설정한다.
* **권한별 메뉴 분기:** 조건문(`if st.session_state.role...`)을 통해 현재 역할이 접근할 수 있는 페이지 묶음만 `page_dict`에 추가한다. Admin은 모든 영역을, Requester와 Responder는 각자의 영역만 볼 수 있다.
* **네비게이션 렌더링:** 역할이 지정되어 있으면 구성된 `page_dict`를 기반으로 `st.navigation()`을 통해 사이드바 메뉴를 만들고, 역할이 없으면 로그인 페이지만 노출한 뒤 `pg.run()`으로 실행한다.

**검색 키워드 (Ctrl+F용)**

* Streamlit 멀티 페이지 (Multi-page)
* 세션 상태 (st.session_state)
* 페이지 객체 (st.Page)
* 네비게이션 라우팅 (st.navigation)
* 화면 새로고침 (st.rerun)
* 역할 기반 접근 제어 (RBAC)
* 조건부 동적 메뉴 구성
* 로그인 로그아웃 구현

<br>

---
