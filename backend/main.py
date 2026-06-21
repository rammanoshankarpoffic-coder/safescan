"""
SafeScan Backend API
---------------------
Exposes the risk engine over HTTP so the frontend (live camera QR scanner)
can send a decoded QR payload and get back a risk verdict.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from risk_engine import analyze_qr

app = FastAPI(title="SafeScan API")

# Allow the deployed frontend to call this API from the browser.
# Note: allow_credentials=True cannot be combined with a wildcard origin —
# browsers reject that combination per the CORS spec. This app doesn't use
# cookies or auth headers, so credentials aren't needed here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    payload: str


@app.get("/")
def health_check():
    return {"status": "SafeScan API is running"}


@app.post("/analyze")
def analyze(request: ScanRequest):
    """
    Receives the raw decoded text from a scanned QR code and returns
    a structured risk verdict.
    """
    result = analyze_qr(request.payload)
    return result
