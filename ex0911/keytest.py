from openai import OpenAI

# 자동으로 환경 변수의 OPENAI_API_KEY를 인식함
client = OpenAI()

# 질의 요청
response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[
        {"role": "user", "content": "인공지능으로서 포부를 밝히시오."}
    ]
)

# 답변 출력
print(response.choices[0].message.content)