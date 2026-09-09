from enum import Enum
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "안녕~"}

@app.get("/bye") # 맨 뒤에 슬래시는 붙이지 않는 것이 관례
async def bye():
    return {"message": "Bye~"}

class Operator(str, Enum): # 연산자 목록 enum 클래스
    PLUS = "plus"
    MINUS = "minus"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

calculator_lambda_dict = {
    Operator.PLUS: lambda x, y: x+y,
    Operator.MINUS: lambda x, y: x-y,
    Operator.MULTIPLY: lambda x, y: x*y,
    Operator.DIVIDE: lambda x, y: x/y
}

@app.get("/calculator/{operator}")
async def calculator(operator: Operator, operand1: float, operand2: float): # 정수, 소수 모두 처리하기 위해 float 사용
    # 만약 operator가 enum 값에 없을 경우 에러 메시지 반환
    if operator == Operator.DIVIDE and operand2 == 0:
        raise HTTPException(status_code=400, detail="0으로 나눌 수 없습니다.")

    # 계산
    result = calculator_lambda_dict[operator](operand1, operand2)

    # operator 연산 및 반환
    return result