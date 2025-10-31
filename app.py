# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal, List
from datetime import datetime

app = FastAPI(title="ai-budget-backend")

# ★ 배포 후에는 ["https://<너의-러버블-도메인>"] 으로 좁히세요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Record(BaseModel):
    id: Optional[int] = None
    date: str                              # "YYYY-MM-DD"
    type: Literal["expense", "income", "saving"]
    amount: float
    category: str = "기본"
    memo: str = ""
    model_config = ConfigDict(populate_by_name=True)

# 임시 인메모리 DB (처음엔 이걸로 OK → 나중에 DB로 교체)
DB = {
    "records": [],        # list[dict]
    "budgets": {}         # {"YYYY-MM": number}
}

@app.get("/")
def ping():
    return {"status":"ok"}

# ---- 예산 ----
@app.put("/budget/{ym}")
def set_budget(ym: str, value: float):
    DB["budgets"][ym] = value
    return {"ok": True, "ym": ym, "value": value}

@app.get("/budget/{ym}")
def get_budget(ym: str):
    return {"ym": ym, "value": DB["budgets"].get(ym, 0)}

# ---- 레코드 CRUD ----
@app.post("/records")
def create_record(r: Record):
    r.id = int(datetime.now().timestamp() * 1000)
    DB["records"].append(r.model_dump())
    return r

@app.get("/records")
def list_records(ym: Optional[str] = None, date: Optional[str] = None):
    arr = DB["records"]
    if date:
        arr = [x for x in arr if x["date"] == date]
    elif ym:
        arr = [x for x in arr if x["date"].startswith(ym)]
    return {"items": arr}

@app.put("/records/{rid}")
def update_record(rid: int, r: Record):
    for i, x in enumerate(DB["records"]):
        if x["id"] == rid:
            r.id = rid
            DB["records"][i] = r.model_dump()
            return r
    raise HTTPException(404, "not found")

@app.delete("/records/{rid}")
def delete_record(rid: int):
    before = len(DB["records"])
    DB["records"] = [x for x in DB["records"] if x["id"] != rid]
    return {"deleted": before - len(DB["records"])}

# ---- 월간 통계(1~12월, 지출/수입/저축 합계) ----
@app.get("/stats/monthly/{year}")
def stats_monthly(year: int):
    def sum_month(m, t):
        prefix = f"{year}-{m:02d}"
        return sum(x["amount"] for x in DB["records"] if x["date"].startswith(prefix) and x["type"] == t)
    items = []
    for m in range(1, 12+1):
        items.append({
            "month": m,
            "expense": sum_month(m, "expense"),
            "income":  sum_month(m, "income"),
            "saving":  sum_month(m, "saving"),
        })
    return {"items": items}
