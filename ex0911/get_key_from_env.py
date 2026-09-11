import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
# .gitignore에 .env 파일 반드시 추가해야 함.
load_dotenv()

# API 키 불러오기
api_key = os.getenv("OPENAI_API_KEY")

# 키가 제대로 불러와졌는지 확인
if not api_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# OpenAI 클라이언트 생성
client = OpenAI(api_key=api_key)

# 모델에 질문
response = client.responses.create(
    model="gpt-5.6-luna",
    input="챗지피티 모델로서 1분 자기소개 해줘."
)

# 답변 출력
print(response.output_text)