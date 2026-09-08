from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{items_id}")
async def read_user_item(item_id: str, needy: str): # 쿼리 매개변수를 필수로 만들려면 기본값을 선언하지 않으면 된다.
    item = {"item_id": item_id, "needy": needy}
    return item