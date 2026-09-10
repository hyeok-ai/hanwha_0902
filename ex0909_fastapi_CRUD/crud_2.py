from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel
from typing import Optional, Dict

app = FastAPI(title="전당포 API", description="전당포 물품 관리 API")

# 인메모리 데이터베이스
# Dict[int, dict]
# 변수 하나에도 타입 힌트를 사용함
# 하지만 이와 다른 타입의 값을 집어넣어도 실행은 됨.
# 강제하려면 필요한 것이 Pydantic
# 각각의 path operation function에서 검증함
pawn_db: Dict[int, dict] = {
    1: {"name": "금목걸이", "loan_amount": 400, "status": "pawned"},
    2: {"name": "롤렉스", "loan_amount": 300000, "status": "pawned"}
}

# Pydantic을 활용한 입력 형식 정의
class Article(BaseModel):
    name: str
    loan_amount: int
    status: str = "pawned"

class ArticleUpdate(BaseModel):
    name: Optional[str] = None
    loan_amount: Optional[int] = None
    status: Optional[str] = None


@app.get("/articles")
async def get_articles():
    return {"inventory": pawn_db}
'''
{
  "inventory": {
    "1": {
      "name": "금목걸이",
      "loan_amount": 400,
      "status": "pawned"
    },
    "2": {
      "name": "롤렉스",
      "loan_amount": 300000,
      "status": "pawned"
    },
    "3": {
      "name": "banana",
      "loan_amount": 20220200202020,
      "status": "pawned"
    }
  }
}
'''

@app.post("/articles")
async def pawn_item(article: Article):
    new_id = max(pawn_db.keys(), default=0) + 1
    pawn_db[new_id] = article.model_dump()
    return {"message": "새로운 물품이 등록됨.", "article_id": new_id, "article": pawn_db[new_id]}


@app.get("/articles/{article_id}")
async def get_article(article_id: int):
    if article_id not in pawn_db:
        raise HTTPException(status_code=404, detail="담보물을 찾을 수 없습니다.")
    return {"article": pawn_db[article_id]}

@app.put("/articles/{article_id}")
async def replace_article(article_id: int, article: Article):
    if article_id not in pawn_db:
        raise HTTPException(status_code=404, detail="담보물을 찾을 수 없습니다.")
    pawn_db[article_id] = article.model_dump()
    return {"message": "담보물 정보가 완전히 교체되었습니다.", "article": pawn_db[article_id]}

@app.patch("/articles/{article_id}")
async def update_article_status(article_id: int, article_update: ArticleUpdate):
    if article_id not in pawn_db:
        raise HTTPException(status_code=404, detail="담보물을 찾을 수 없습니다.")

    stored_article = pawn_db[article_id]
    update_data = article_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        stored_article[key] = value

    pawn_db[article_id] = stored_article
    return {"message": "담보물 정보가 업데이트됨", "article": pawn_db[article_id]}

@app.delete("/articles/{article_id}")
async def delete_article(article_id: int):
    if article_id not in pawn_db:
        raise HTTPException(status_code=404, detail="담보물을 찾을 수 없습니다.")
    del pawn_db[article_id]
    return {"message": "담보물이 장부에서 삭제되었습니다."}

@app.head("/articles")
async def get_articles_headers(response: Response):
    response.headers["X-Total-Articles"] = str(len(pawn_db))
    return response

@app.options("/articles")
async def get_articles_options(response: Response):
    response.headers["Allow"] = "GET, POST, HEAD, OPTIONS, TRACE"
    return {"message": "이 엔드포인트는 GET, POST, HEAD, OPTIONS, TRACE를 지원합니다."}

@app.api_route("/articles", methods=["TRACE"])
async def trace_request(request: Request):
    return {
        "method": request.method,
        "headers": dict(request.headers),
        "url": str(request.url) 
    }