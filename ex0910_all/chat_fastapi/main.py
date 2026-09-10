from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserMessage(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"response": "FastAPI 서버가 정상 동작 중입니다."}

@app.post("/chat")
def process_chat(message: UserMessage):
    prompt = message.prompt

    if "안녕" in prompt:
        response = "안녕하세요~"

    elif "종료" in prompt:
        response = "종료 기능 구현중..."

    elif "도움말" in prompt:
        response = "도움말을 출력합니다."

    elif "잘가" in prompt:
        response = "안녕히가세요."

    else:
        response = "저도 그렇게 생각합니다."

    return {ㄴ
        "response": response
    }
        
