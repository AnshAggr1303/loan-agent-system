# ============================================================================
# MOCK KYC DATABASE - Python
# Path: backend/mock_data/kyc_database.py
# ============================================================================

from typing import Optional, Dict
from datetime import datetime
import asyncio

MOCK_KYC_DATABASE = {
    "GOODPAN123": {
        "pan_number": "GOODPAN123",
        "full_name": "Rohan Gupta",
        "date_of_birth": "1990-05-15",
        "kyc_status": "VERIFIED",
        "phone": "9876543210",
        "address": "Mumbai, Maharashtra"
    },
    "ABCDE1234F": {
        "pan_number": "ABCDE1234F",
        "full_name": "Rajesh Kumar",
        "date_of_birth": "1988-03-20",
        "kyc_status": "VERIFIED",
        "phone": "9876543211",
        "address": "Bangalore, Karnataka"
    },
    "FGHIJ5678K": {
        "pan_number": "FGHIJ5678K",
        "full_name": "Priya Sharma",
        "date_of_birth": "1992-11-08",
        "kyc_status": "VERIFIED",
        "phone": "9876543212",
        "address": "Delhi, NCR"
    },
    "BADPAN456": {
        "pan_number": "BADPAN456",
        "full_name": "Priya Singh",
        "date_of_birth": "1995-11-20",
        "kyc_status": "VERIFIED",
        "phone": "9876543213",
        "address": "Pune, Maharashtra"
    },
    "KLMNO9012P": {
        "pan_number": "KLMNO9012P",
        "full_name": "Amit Sharma",
        "date_of_birth": "1985-07-12",
        "kyc_status": "VERIFIED",
        "phone": "9876543214",
        "address": "Hyderabad, Telangana"
    },
    "KYCFAIL789": {
        "pan_number": "KYCFAIL789",
        "full_name": "Amit Verma",
        "date_of_birth": "1988-01-30",
        "kyc_status": "PENDING_AADHAAR_LINK",
        "phone": "9876543215",
        "address": "Chennai, Tamil Nadu"
    },
}

async def verify_kyc(pan: str) -> Optional[Dict]:
    """
    Simulate KYC verification with realistic delay
    """
    # Simulate API delay
    await asyncio.sleep(1)
    
    record = MOCK_KYC_DATABASE.get(pan.upper())
    return record

def calculate_age(dob: str) -> int:
    """
    Calculate age from date of birth
    """
    today = datetime.now()
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    
    age = today.year - birth_date.year
    
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age