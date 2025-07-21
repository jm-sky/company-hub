"""CRUD operations for companies."""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models import Company, RegonData, MfData, ViesData


def get_company_by_nip(db: Session, nip: str) -> Optional[Company]:
    """Get company by NIP."""
    return db.query(Company).filter(Company.nip == nip).first()


def create_company(db: Session, nip: str, name: Optional[str] = None) -> Company:
    """Create a new company."""
    company = Company(nip=nip, name=name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_or_create_company(db: Session, nip: str, name: Optional[str] = None) -> Company:
    """Get existing company or create new one."""
    company = get_company_by_nip(db, nip)
    if not company:
        company = create_company(db, nip, name)
    elif name and name != company.name:
        company.name = name  # type: ignore
        db.commit()
        db.refresh(company)
    return company


def get_regon_data(db: Session, company_id: int) -> Optional[RegonData]:
    """Get latest REGON data for company."""
    return (
        db.query(RegonData)
        .filter(RegonData.company_id == company_id)
        .order_by(desc(RegonData.fetched_at))
        .first()
    )


def is_regon_data_expired(regon_data: Optional[RegonData]) -> bool:
    """Check if REGON data is expired."""
    if not regon_data:
        return True
    return datetime.now(timezone.utc) > regon_data.expires_at  # type: ignore


def store_regon_data(
    db: Session,
    company_id: int,
    entity_type: str,
    report_type: str,
    data: dict
) -> RegonData:
    """Store REGON data for company."""
    regon_data = RegonData(
        company_id=company_id,
        entity_type=entity_type,
        report_type=report_type,
        data=data
    )
    db.add(regon_data)
    db.commit()
    db.refresh(regon_data)
    return regon_data


def get_mf_data(db: Session, company_id: int) -> Optional[MfData]:
    """Get latest MF data for company."""
    return (
        db.query(MfData)
        .filter(MfData.company_id == company_id)
        .order_by(desc(MfData.fetched_at))
        .first()
    )


def is_mf_data_expired(mf_data: Optional[MfData]) -> bool:
    """Check if MF data is expired."""
    if not mf_data:
        return True
    return datetime.now(timezone.utc) > mf_data.expires_at  # type: ignore


def store_mf_data(db: Session, company_id: int, data: dict) -> MfData:
    """Store MF data for company."""
    mf_data = MfData(company_id=company_id, data=data)
    db.add(mf_data)
    db.commit()
    db.refresh(mf_data)
    return mf_data


def get_vies_data(db: Session, company_id: int) -> Optional[ViesData]:
    """Get latest VIES data for company."""
    return (
        db.query(ViesData)
        .filter(ViesData.company_id == company_id)
        .order_by(desc(ViesData.fetched_at))
        .first()
    )


def is_vies_data_expired(vies_data: Optional[ViesData]) -> bool:
    """Check if VIES data is expired."""
    if not vies_data:
        return True
    return datetime.now(timezone.utc) > vies_data.expires_at  # type: ignore


def store_vies_data(
    db: Session,
    company_id: int,
    data: dict,
    consultation_number: Optional[str] = None
) -> ViesData:
    """Store VIES data for company."""
    vies_data = ViesData(
        company_id=company_id,
        data=data,
        consultation_number=consultation_number
    )
    db.add(vies_data)
    db.commit()
    db.refresh(vies_data)
    return vies_data
