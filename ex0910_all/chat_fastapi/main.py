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
        response = "종료는 불가합니다."

    elif "도움말" in prompt:
        response = "네?"

    elif "잘가" in prompt:
        response = "잘가요"

    else:
        response = "나도"

    return {
        "response": response
    }
        
