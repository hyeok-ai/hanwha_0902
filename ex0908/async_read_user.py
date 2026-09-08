from fastapi import FastAPI

app = FastAPI()


@app.get("/users/me") # /users/me가 먼저 와야지 제대로 처리가 된다.
async def read_user_me(): # 비동기 사용
    return {"user_id": "the current user"}


@app.get("/users/{user_id}") # 만약 해당 함수에 대한 정의가 먼저 온다면 사용자는 /users/me에 접근할 수 없게 된다.
async def read_user(user_id: str):
    return {"user_id": user_id}