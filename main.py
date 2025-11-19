import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Tournament, Prediction

app = FastAPI(title="Crypto Prediction Tournaments API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Crypto Prediction API is live"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ---- API Models for requests ----
class TournamentCreate(BaseModel):
    title: str
    symbol: str
    description: Optional[str] = None
    prize_pool: float = 0
    entry_fee: float = 0
    starts_at: datetime
    ends_at: datetime

class PredictionCreate(BaseModel):
    tournament_id: str
    user_name: str
    direction: str  # 'up' or 'down'
    confidence: int

# ---- Helper ----
def collection_name(model_cls) -> str:
    return model_cls.__name__.lower()

# ---- Tournament Endpoints ----
@app.post("/api/tournaments")
def create_tournament(payload: TournamentCreate):
    data = Tournament(**payload.model_dump())
    tid = create_document(collection_name(Tournament), data)
    return {"id": tid}

@app.get("/api/tournaments")
def list_tournaments():
    docs = get_documents(collection_name(Tournament), {})
    # convert ObjectId to str if present
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    # order by start time descending if possible
    docs.sort(key=lambda x: x.get("starts_at", datetime.now(timezone.utc)), reverse=True)
    return docs

# ---- Prediction Endpoints ----
@app.post("/api/predictions")
def create_prediction(payload: PredictionCreate):
    # simple validation for direction
    if payload.direction not in ("up", "down"):
        raise HTTPException(status_code=422, detail="direction must be 'up' or 'down'")
    data = Prediction(**payload.model_dump())
    pid = create_document(collection_name(Prediction), data)
    return {"id": pid}

@app.get("/api/predictions")
def list_predictions(tournament_id: Optional[str] = None):
    filt = {"tournament_id": tournament_id} if tournament_id else {}
    docs = get_documents(collection_name(Prediction), filt)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    # newest first
    docs.sort(key=lambda x: x.get("created_at", datetime.now(timezone.utc)), reverse=True)
    return docs

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
