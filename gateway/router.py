from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import subprocess
import json

from gateway.cache import get_cached_route, set_cached_route
from gateway.fallback_extractor import headless_extract_fallback
from gateway.corporate_sync import build_group_itinerary
from gateway.b2b_fulfillment import fulfillment_engine

app = FastAPI(
    title="fli Enterprise Flight Gateway",
    version="1.0.0",
    description="High-throughput zero-scraping flight search, corporate group sync, and B2B fulfillment engine in SAR."
)

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., example="JED")
    destination: str = Field(..., example="DAC")
    departure_date: str = Field(..., example="2027-01-11")
    return_date: Optional[str] = Field(None, example="2027-01-25")
    currency: str = Field("SAR", example="SAR")
    cabin_class: str = Field("ECONOMY", example="ECONOMY")

class CorporateSyncRequest(BaseModel):
    event_hub: str = Field(..., example="DAC")
    departure_date: str = Field(..., example="2027-01-11")
    return_date: Optional[str] = Field("2027-01-25", example="2027-01-25")
    origins: List[str] = Field(..., example=["JED", "RUH", "DMM"])
    currency: str = Field("SAR", example="SAR")

class PassengerInfo(BaseModel):
    first_name: str
    last_name: str
    passport_number: str
    nationality: str

class BookingRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    net_fare_sar: float
    passenger: PassengerInfo

class IssueTicketRequest(BaseModel):
    pnr: str

@app.get("/health")
def health():
    return {
        "status": "ONLINE",
        "currency_standard": "SAR",
        "engine": "fli-reverse-rpc + headless-chromium-v152",
        "b2b_wallet": fulfillment_engine.get_wallet_status()
    }

@app.post("/api/v1/search")
def search_flights(req: FlightSearchRequest):
    route_key = f"{req.origin}_{req.destination}_{req.departure_date}_{req.return_date}_{req.currency}_{req.cabin_class}"
    cached = get_cached_route(route_key)
    if cached:
        cached["cache_hit"] = True
        return cached

    cmd = [
        "/home/ubuntu/fli-env/bin/fli",
        "flights",
        req.origin,
        req.destination,
        req.departure_date,
        "--currency", req.currency,
        "--format", "json"
    ]
    if req.return_date:
        cmd.extend(["--return-date", req.return_date])
    if req.cabin_class:
        cmd.extend(["--cabin-class", req.cabin_class])

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if proc.returncode == 0 and proc.stdout:
            data = json.loads(proc.stdout)
            if data.get("flights") and len(data["flights"]) > 0:
                data["cache_hit"] = False
                set_cached_route(route_key, data)
                return data
    except Exception:
        pass

    fallback_data = headless_extract_fallback(
        req.origin,
        req.destination,
        req.departure_date,
        req.return_date,
        req.currency
    )
    fallback_data["cache_hit"] = False
    set_cached_route(route_key, fallback_data)
    return fallback_data

@app.post("/api/v1/group-sync")
def corporate_group_sync(req: CorporateSyncRequest):
    return build_group_itinerary(
        destination=req.event_hub,
        departure_date=req.departure_date,
        return_date=req.return_date,
        origins=req.origins,
        currency=req.currency
    )

@app.post("/api/v1/b2b/reserve")
def reserve_seat(req: BookingRequest):
    res = fulfillment_engine.create_reservation(
        req.origin,
        req.destination,
        req.departure_date,
        req.net_fare_sar,
        req.passenger.dict()
    )
    return res

@app.post("/api/v1/b2b/issue")
def issue_ticket(req: IssueTicketRequest):
    res = fulfillment_engine.issue_ticket(req.pnr)
    return res
