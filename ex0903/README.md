# ex0903 실습 코드 정리

## 파일: `0903-1.ipynb`

```python
x=5
y="John"
print(x)
print(type(x))
```

* 변수 출력과 type 연산자

<br>

```python
print(type(type(1)))
```

* type 연산자의 반환 값의 type은 type이다.

<br>

```python
def myfunc():
  global x
  x="fantastic"

myfunc()

print("Python is " + x)
```

* 전역 변수 global 키워드와 문자열 덧셈

<br>

```python
a=str(1)
print(a)

'''
str="Hello, World!"
print(len(a))

for x in str:
  print(x)
'''
```

* 정수를 문자열(str)으로 캐스팅

<br>

---

## 파일: `0903-2.ipynb`

```python
a="Hellu, World!"
print(a.replace("H", "J"))
```

* replace 메소드 통해 문자열 치환

<br>

---

## 파일: `0903-3.ipynb`

```python
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("홍길동", 16)
p2 = Person("벤자민", 22)
p3 = Person("세종대왕", 30)
```

* \_\_init\_\_ 생성자 메소드를 통한 인스턴스 변수 초기화

<br>

```python
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

  def greet(self):
    print("Hello, my name is " + self.name)

  def display_info(self):
    print(f"이름: {self.name}, 나이: {self.age}")

p1 = Person("Emile Jong", 25)
p1.greet()
p1.display_info()

a=p1.display_info
a()
```

* 메소드를 통한 인스턴스 변수 값 접근

<br>

---

## 파일: `global_variable.py`

```python
def myfunc():
    global x
    x = "fantastic"

myfunc()

print(x)
```

* 전역 변수 키워드 global (전역 변수 x의 값이 fantastic이 됨)

<br>

---

## 파일: `plt_line_plot.py`

```python
import matplotlib.pyplot as plt
import numpy as np

xpoints = np.array([1, 2, 6, 8])
ypoints = np.array([3, 8, 1, 10])

plt.plot(xpoints, ypoints)
plt.show()
```

* 좌표를 잇는 선 그래프(Line Plot)

<br>

---

## 파일: `st_pyplot.py`

```python
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 페이지 제목
st.title("일차함수 그래프 그리기")

# 사이드바에 슬라이더 배치
st.sidebar.header("변수 조절")
a = st.sidebar.slider("기울기 (a)", min_value=-10.0, max_value=10.0, value=1.0, step=0.1)
b = st.sidebar.slider("y절편 (b)", min_value=-10.0, max_value=10.0, value=0.0, step=0.1)

# 현재 수식 출력
st.write(f"### 수식: $y = {a}x + {b}$")

# x 값 생성 (-10 부터 10까지 400개 구간)
x = np.linspace(-10, 10, 400)
# y 값 계산
y = a * x + b

# 그래프 초기화 및 설정
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x, y, color='blue', linewidth=2)

# 중심 축(x=0, y=0) 그리기
ax.axhline(0, color='black', linewidth=1.2)
ax.axvline(0, color='black', linewidth=1.2)

# 눈금선 및 그래프 범위 설정
ax.grid(color='gray', linestyle='--', linewidth=0.5)
ax.set_xlim([-10, 10])
ax.set_ylim([-20, 20])
ax.set_xlabel("x")
ax.set_ylabel("y")

# 스트림릿 화면에 그래프 출력
st.pyplot(fig)
```

* y=ax+b 그래프 그리기

<br>

---

## 파일: `st_line_chart.py`

```python
import streamlit as st
import numpy as np
import pandas as pd

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)
```

* streamlit에서 라인 차트 그리기.

<br>

---

## 파일: `matplotlib_version.py`

```python
import matplotlib

print(matplotlib.__version__)
```

* matplotlib 버전 확인

<br>

---

## 파일: `st_dataframe.py`

```python
import pandas as pd
import streamlit as st

df = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
)
edited_df = st.data_editor(df)

favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
st.markdown(f"Your favorite command is **{favorite_command}** 🎈")
```

* data editor (엑셀 시트와 같은 모양)

<br>

---
