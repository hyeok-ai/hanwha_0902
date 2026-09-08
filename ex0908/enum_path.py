from enum import Enum

from fastapi import FastAPI


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet: # ModelName Enum 클래스의 멤버 변수명으로 입력값과 비교하거나
        return {"model_name": model_name, "message": f"Deep Learning FTW!, type(model_name)={str(type(model_name))}, type(ModelName.alexnet)={str(type(ModelName.alexnet))}"}
        # {"model_name":"alexnet","message":"Deep Learning FTW!, type(model_name)=<enum 'ModelName'>, type(ModelName.alexnet)=<enum 'ModelName'>"}

    if model_name.value == "lenet": # 입력된 모델의 value 멤버 변수를 문자열과 비교할 수 있다.
        return {"model_name": model_name, "message": f"LeCNN all the images, type(model_name.value)={str(type(model_name.value))}, type(\"lenet\")={str(type("lenet"))}"}
        # {"model_name":"lenet","message":"LeCNN all the images, type(model_name.value)=<class 'str'>, type(\"lenet\")=<class 'str'>"}

    return {"model_name": model_name, "messages": "Have some residuals"}