from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..data.fmcsa_client import FMCSAClient

router = APIRouter(
    prefix="/carriers",
    tags=["carriers"]
)

@router.get("/{dot_number}/analysis")
async def analyze_carrier(
    dot_number: str, 
    db: Session = Depends(get_db)
):
    try:
        client = FMCSAClient()
        # Add debug print
        print(f"Analyzing carrier {dot_number}")
        carrier = client.get_carrier_by_dot(dot_number, db)
        
        if not carrier:
            raise HTTPException(
                status_code=404, 
                detail=f"Carrier {dot_number} not found"
            )
        
        return client.get_carrier_analysis(carrier)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{dot_number}")
async def get_carrier(dot_number: str, db: Session = Depends(get_db)):
    try:
        client = FMCSAClient()
        print(f"Getting carrier data for DOT: {dot_number}")  # Debug print
        carrier = client.get_carrier_by_dot(dot_number)  # Removed db parameter
        if not carrier:
            raise HTTPException(status_code=404, detail=f"Carrier {dot_number} not found")
        return carrier
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))