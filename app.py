# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal

app = FastAPI(title="ai-budget-backend")

# CORS (러버블에서 호출하려면 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # 배포 후 러버블 도메인만 허용으로 좁히세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Record(BaseModel):
    # 요청에서 'type' 또는 'ttype' 아무거나 보내도 받도록 alias 설정
    date: str
    ttype: Literal["expense", "income"] = Field(alias="type")
    category: str | None = ""
    memo: str | None = ""
    amount: float

    # ✅ Pydantic v2 방식 (v1의 class Config → v2의 model_config)
    model_config = ConfigDict(populate_by_name=True)  # 내부에선 ttype으로 사용

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
    exp = sum(r.amount for r in payload.records if r.ttype == "expense")
    inc = sum(r.amount for r in payload.records if r.ttype == "income")
    return AnalyzeResponse(
        count=len(payload.records),
        sum_expense=exp,
        sum_income=inc,
        balance=inc - exp
    )
