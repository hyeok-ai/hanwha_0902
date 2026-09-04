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