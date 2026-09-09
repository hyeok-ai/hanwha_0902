from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="All HTTP Methods Example")

fake_db = {}

class Ingredient(BaseModel):
    name: str
    description: Optional[str] = None

@app.get("/ingredients/{ingredient_id}")
async def read_ingredient(ingredient_id: str):
    ingredient = fake_db.get(ingredient_id, "Ingredient not found")
    return {"method": "GET", "ingredient_id": ingredient_id, "data": ingredient}

@app.post("/ingredients/{ingredient_id}")
async def create_ingredient(ingredient_id: str, ingredient: Ingredient):
    fake_db[ingredient_id] = ingredient.model_dump() # 과거에는 ingredient.dict() 사용
    return {"method": "POST", "ingredient_id": ingredient_id, "data": fake_db[ingredient_id]}

@app.patch("/ingredients/{ingredient_id}")
async def update_ingredient(ingredient_id: str, name: str):
    if ingredient_id in fake_db:
        fake_db[ingredient_id]["name"] = name
        return {"method": "PATCH", "ingredient_id": ingredient_id, "message": "Name updated", "data": fake_db[ingredient_id]}
    return {"method": "PATCH", "message": "ingredient not found"}

@app.delete("/ingredients/{ingredient_id}")
async def delete_ingredient(ingredient_id: str):
    deleted_ingredient = fake_db.pop(ingredient_id, None)
    return {"method": "DELETE", "ingredient_id": ingredient_id, "deleted": deleted_ingredient is not None}

@app.options("/ingredients")
async def options_ingredients(response: Response):
    response.headers["Allow"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD, TRACE"
    return {"method": "OPTIONS", "message": "Check headers for allowed methods"}

@app.head("/ingredients/{ingredient_id}")
async def head_ingredient(ingredient_id: str):
    return {"method": "HEAD"}

@app.trace("/ingredients")
async def trace_ingredient(request: Request):
    return {"method": "TRACE", "client_headers": dict(request.headers)}