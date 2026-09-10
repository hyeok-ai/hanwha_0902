import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.title("Streamlit & FastAPI 연결 해제")

with st.form("user_form"):
    name = st.text_input("이름", value="홍길동")
    age = st.number_input("나이", min_value=1, max_value=120, value=20)
    submit_button = st.form_submit_button("백엔드로 전송")

if submit_button:
    payload = {
        "name": name,
        "age": age
    }

    try:
        response = requests.post(f"{FASTAPI_URL}/predict", json=payload)
        print(type(response)) # <class 'requests.models.Response'>

        if response.status_code == 200:
            result = response.json() # https://requests.readthedocs.io/en/latest/api/#requests.Response.json
            print(type(result)) # <class 'dict'>

            st.success("FastAPI 응답 성공!")
            st.write(f"**결과:** {result['result_message']}")

        else:
            st.error(f"오류 발생 (상태 코드: {response.status_code})")

    except requests.exceptions.ConnectionError:
        st.error("FastAPI 서버에 연결할 수 없습니다. 백엔드 서버를 확인하세요.")