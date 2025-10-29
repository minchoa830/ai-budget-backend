# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import List, Literal

app = FastAPI(title="ai-budget-backend")

# CORS (러버블/프론트에서 호출하려면 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 배포 후 러버블 도메인만 허용으로 좁히는 걸 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------ Schemas ------
class Record(BaseModel):
    date: str
    # 입력 시 'type' 또는 'ttype' 아무거나 허용, 응답은 항상 'type'으로 직렬화
    ttype: Literal["expense", "income"] = Field(
        validation_alias=AliasChoices("type", "ttype"),
        serialization_alias="type"
    )
    category: str | None = ""
    memo: str | None = ""
    amount: float

    # 내부에서는 필드 이름(ttype)으로 접근 가능
    model_config = ConfigDict(populate_by_name=True)

class Payload(BaseModel):
    records: List[Record]

class AnalyzeResponse(BaseModel):
    count: int
    sum_expense: float
    sum_income: float
    balance: float

# ------ Routes ------
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
