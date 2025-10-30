# ============================================================================
# MOCK CREDIT DATABASE - Python
# Path: backend/mock_data/credit_database.py
# ============================================================================

from typing import Optional, Dict
import asyncio

MOCK_CREDIT_DATABASE = {
    "GOODPAN123": {
        "pan_number": "GOODPAN123",
        "score": 790,
        "status": "No defaults",
        "active_loans": 1,
        "credit_history_years": 8,
        "defaults": 0
    },
    "ABCDE1234F": {
        "pan_number": "ABCDE1234F",
        "score": 820,
        "status": "Excellent",
        "active_loans": 0,
        "credit_history_years": 10,
        "defaults": 0
    },
    "FGHIJ5678K": {
        "pan_number": "FGHIJ5678K",
        "score": 720,
        "status": "Good",
        "active_loans": 2,
        "credit_history_years": 5,
        "defaults": 0
    },
    "BADPAN456": {
        "pan_number": "BADPAN456",
        "score": 680,
        "status": "Fair",
        "active_loans": 3,
        "credit_history_years": 4,
        "defaults": 0
    },
    "KLMNO9012P": {
        "pan_number": "KLMNO9012P",
        "score": 670,
        "status": "Fair",
        "active_loans": 2,
        "credit_history_years": 6,
        "defaults": 1
    },
    "KYCFAIL789": {
        "pan_number": "KYCFAIL789",
        "score": 620,
        "status": "Poor - 2 defaults",
        "active_loans": 4,
        "credit_history_years": 3,
        "defaults": 2
    },
}

async def fetch_credit_score(pan: str) -> Optional[Dict]:
    """
    Simulate credit score API with delay
    """
    # Simulate API delay
    await asyncio.sleep(1)
    
    record = MOCK_CREDIT_DATABASE.get(pan.upper())
    return record

def get_credit_score_band(score: int) -> str:
    """
    Get credit score band
    """
    if score >= 750:
        return "Excellent"
    elif score >= 700:
        return "Very Good"
    elif score >= 650:
        return "Good"
    elif score >= 600:
        return "Fair"
    else:
        return "Poor"