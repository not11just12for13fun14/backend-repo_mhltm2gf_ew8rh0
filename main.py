import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Event, Ticket

app = FastAPI(title="Events API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities

def to_str_id(doc):
    if not doc:
        return doc
    d = dict(doc)
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    return d


@app.get("/")
def read_root():
    return {"message": "Events API running"}


@app.get("/test")
def test_database():
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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
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
    return response


# Events Endpoints
@app.post("/api/events", response_model=dict)
def create_event(event: Event):
    try:
        event_id = create_document("event", event)
        return {"id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events", response_model=List[dict])
def list_events(limit: Optional[int] = 50):
    try:
        docs = get_documents("event", {}, limit)
        return [to_str_id(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/today", response_model=List[dict])
def list_today_events():
    try:
        # Get events where date is today (UTC)
        today = datetime.utcnow().date()
        tomorrow = datetime.utcnow().date()
        # fetch all then filter in python due to naive datetimes
        docs = get_documents("event")
        results = []
        for d in docs:
            dt = d.get("date")
            if isinstance(dt, datetime) and dt.date() == today:
                results.append(to_str_id(d))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/{event_id}", response_model=dict)
def get_event(event_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        doc = db["event"].find_one({"_id": ObjectId(event_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Event not found")
        return to_str_id(doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid id")


# Tickets Endpoints
@app.post("/api/tickets", response_model=dict)
def create_ticket(ticket: Ticket):
    try:
        ticket_id = create_document("ticket", ticket)
        return {"id": ticket_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
