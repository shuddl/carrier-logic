from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/carriers/{dot_number}/analytics")
async def get_carrier_analytics(dot_number: str):
    try:
        # Example carrier data as JSON
        carrier_data = {
            "dot_number": dot_number,
            "legal_name": "BLUE COLLAR EXPRESS LLC",
            "dba_name": "BLUE COLLAR EXPRESS",
            "operating_status": "AUTHORIZED",
            "safety_metrics": {
                "safety_rating": "SATISFACTORY",
                "crash_total": 0,
                "driver_oos_rate": 0,
                "vehicle_oos_rate": 0
            },
            "fleet_info": {
                "total_power_units": 5,
                "total_drivers": 5
            },
            "authority_status": "ACTIVE",
            "risk_level": "LOW"
        }
        
        return JSONResponse(
            content=carrier_data,
            headers={
                "Content-Type": "application/json"
            }
        )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={
                "Content-Type": "application/json"
            }
        )

@app.get("/api/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        headers={
            "Content-Type": "application/json"
        }
    )