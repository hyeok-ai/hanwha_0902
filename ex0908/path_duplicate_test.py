from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


@app.get("/users") # 경로는 앞에서부터 매칭되므로, 해당 함수는 실행되지 않는다.
async def read_users2():
    return ["Bean", "Elfo"]