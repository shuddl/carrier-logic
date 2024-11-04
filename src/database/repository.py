from sqlalchemy.orm import Session, joinedload
from ..database.models import CarrierRecord
from . import models
from datetime import datetime
from typing import Optional, List

class CarrierRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_carrier(self, carrier_data: dict) -> models.CarrierRecord:
        # Extract carrier info from nested structure
        if 'content' in carrier_data and 'carrier' in carrier_data['content']:
            carrier_info = carrier_data['content']['carrier']
        else:
            carrier_info = carrier_data.get('carrier', {})

        carrier = self.get_carrier_by_dot(str(carrier_info['dotNumber']))
        
        if not carrier:
            carrier = models.CarrierRecord(
                dot_number=str(carrier_info['dotNumber']),
                legal_name=carrier_info.get('legalName', ''),
                dba_name=carrier_info.get('dbaName'),
                is_active=carrier_info.get('statusCode') == 'A',
                operating_status=carrier_info.get('statusCode'),
                allowed_to_operate=carrier_info.get('allowedToOperate') == 'Y',
                fleet_size=carrier_info.get('totalPowerUnits'),
                driver_count=carrier_info.get('totalDrivers'),
                safety_rating=carrier_info.get('safetyRating'),
                safety_rating_date=carrier_info.get('safetyRatingDate'),
                raw_data=carrier_data  # Store complete response
            )
            self.db.add(carrier)
        else:
            carrier.updated_at = datetime.utcnow()
            carrier.legal_name = carrier_info.get('legalName', '')
            carrier.dba_name = carrier_info.get('dbaName')
            carrier.is_active = carrier_info.get('statusCode') == 'A'
            carrier.operating_status = carrier_info.get('statusCode')
            carrier.allowed_to_operate = carrier_info.get('allowedToOperate') == 'Y'
            carrier.fleet_size = carrier_info.get('totalPowerUnits')
            carrier.driver_count = carrier_info.get('totalDrivers')
            carrier.safety_rating = carrier_info.get('safetyRating')
            carrier.safety_rating_date = carrier_info.get('safetyRatingDate')
            carrier.raw_data = carrier_data  # Update raw data
        
        self.db.commit()
        self.db.refresh(carrier)
        return carrier

    def get_carrier_by_dot(self, dot_number: str) -> Optional[models.CarrierRecord]:
        return self.db.query(models.CarrierRecord).filter(
            models.CarrierRecord.dot_number == dot_number
        ).first()

    def update_carrier(self, carrier: models.CarrierRecord, carrier_data: dict) -> models.CarrierRecord:
        carrier.updated_at = datetime.utcnow()
        carrier.raw_data = carrier_data
        # Update other fields as needed
        self.db.commit()
        self.db.refresh(carrier)
        return carrier

    def create_or_update_safety_metrics(self, carrier_id: int, metrics_data: dict) -> models.SafetyMetrics:
        metrics = self.db.query(models.SafetyMetrics).filter(
            models.SafetyMetrics.carrier_id == carrier_id
        ).first()

        if not metrics:
            metrics = models.SafetyMetrics(
                carrier_id=carrier_id,
                crash_total=metrics_data.get('crashTotal', 0),
                fatal_crashes=metrics_data.get('fatalCrash', 0),
                injury_crashes=metrics_data.get('injCrash', 0),
                tow_crashes=metrics_data.get('towawayCrash', 0),
                driver_oos_rate=float(metrics_data.get('driverOosRate', 0)),
                vehicle_oos_rate=float(metrics_data.get('vehicleOosRate', 0)),
                hazmat_oos_rate=float(metrics_data.get('hazmatOosRate', 0)),
                driver_inspections=metrics_data.get('driverInsp', 0),
                vehicle_inspections=metrics_data.get('vehicleInsp', 0),
                hazmat_inspections=metrics_data.get('hazmatInsp', 0),
                driver_oos_national_avg=float(metrics_data.get('driverOosRateNationalAverage', 0)),
                vehicle_oos_national_avg=float(metrics_data.get('vehicleOosRateNationalAverage', 0)),
                hazmat_oos_national_avg=float(metrics_data.get('hazmatOosRateNationalAverage', 0))
            )
            self.db.add(metrics)
        else:
            # Update existing metrics
            for key, value in metrics_data.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)

        self.db.commit()
        self.db.refresh(metrics)
        return metrics

    def get_carrier_history(self, dot_number: str) -> List[models.RiskAssessment]:
        """
        Get historical risk assessments for a carrier ordered by date
        """
        return self.db.query(models.RiskAssessment)\
            .join(models.CarrierRecord)\
            .filter(models.CarrierRecord.dot_number == dot_number)\
            .order_by(models.RiskAssessment.assessment_date.desc())\
            .all()

    def create_risk_assessment(self, carrier_id: int, analysis_data: dict) -> models.RiskAssessment:
        """
        Create a new risk assessment record for a carrier
        """
        assessment = models.RiskAssessment(
            carrier_id=carrier_id,
            assessment_date=datetime.utcnow(),
            risk_level=analysis_data.get('risk_level'),
            risk_factors=analysis_data.get('risk_factors'),
            warnings=analysis_data.get('warnings', []),
            metrics_analysis=analysis_data.get('metrics_analysis', {})
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment