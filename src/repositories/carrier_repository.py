from sqlalchemy.orm import Session, joinedload
from ..database.models import CarrierRecord, SafetyMetrics, RiskAssessment
from typing import Optional, List
from datetime import datetime

class CarrierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_carrier_by_dot(self, dot_number: str) -> Optional[CarrierRecord]:
        return self.db.query(CarrierRecord).filter(
            CarrierRecord.dot_number == dot_number
        ).first()

    def create_carrier(self, carrier_data: dict) -> CarrierRecord:
        carrier = CarrierRecord(**carrier_data)
        self.db.add(carrier)
        self.db.commit()
        self.db.refresh(carrier)
        return carrier

    def update_carrier(self, carrier: CarrierRecord, updates: dict) -> CarrierRecord:
        for key, value in updates.items():
            setattr(carrier, key, value)
        carrier.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(carrier)
        return carrier

    def get_all_carriers(self, skip: int = 0, limit: int = 100) -> List[CarrierRecord]:
        return (
            self.db.query(CarrierRecord)
            .options(
                joinedload(CarrierRecord.inspections),
                joinedload(CarrierRecord.safety_metrics),
                joinedload(CarrierRecord.inspection_locations),
                joinedload(CarrierRecord.routes)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )