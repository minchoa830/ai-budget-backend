# app.py  (type / ttype 둘 다 허용 · Pydantic v1/v2 모두 동작)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional

app = FastAPI(title="ai-budget-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 배포 후 러버블 도메인만 허용 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Record(BaseModel):
    date: str
    # 둘 중 하나로 와도 됨 (둘 다 없으면 무시되어 합계에만 영향)
    type: Optional[Literal["expense", "income"]] = None
    ttype: Optional[Literal["expense", "income"]] = None
    category: Optional[str] = ""
    memo: Optional[str] = ""
    amount: float

class Payload(BaseModel):
    records: List[Record]

class AnalyzeResponse(BaseModel):
    count: int
    sum_expense: float
    sum_income: float
    balance: float

@app.get("/")
def root():
    return {"status": "ok", "service": "ai-budget-backend"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: Payload):
    def kind(r: Record):
        # type 또는 ttype 중 들어온 값 사용
        return r.ttype or r.type

    exp = sum(r.amount for r in payload.records if kind(r) == "expense")
    inc = sum(r.amount for r in payload.records if kind(r) == "income")
    return AnalyzeResponse(
        count=len(payload.records),
        sum_expense=exp,
        sum_income=inc,
        balance=inc - exp
    )
