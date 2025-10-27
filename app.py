from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Record(BaseModel):
    날짜: str
    카테고리: str
    금액: int

class Payload(BaseModel):
    records: list[Record]

@app.post("/analyze")
def analyze(payload: Payload):
    total = sum(item.금액 for item in payload.records)

    category_sum = {}
    for item in payload.records:
        category_sum[item.카테고리] = category_sum.get(item.카테고리, 0) + item.금액

    return {
        "총지출": total,
        "카테고리별": category_sum
    }
