from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 식재료 데이터 구조 정의
class Ingredient(BaseModel):
    name: str
    quantity: int
    category: str | None = None
    expiration_date: str | None = None

@app.post("/fridge/ingredients")
async def add_ingredient(ingredient: Ingredient):
    return {
        "status": "success",
        "message": f"냉장고에 '{ingredient.name}' {ingredient.quantity}개가 추가되었습니다.",
        "added_ingredient": ingredient
    }