# ============================================================================
# CALCULATION UTILITIES - Python
# Path: backend/utils/calculations.py
# ============================================================================

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate EMI (Equated Monthly Installment)
    Formula: EMI = [P × R × (1+R)^N] / [(1+R)^N-1]
    """
    monthly_rate = annual_rate / 12 / 100
    
    if monthly_rate == 0:
        return principal / tenure_months
    
    emi = (principal * monthly_rate * pow(1 + monthly_rate, tenure_months)) / \
          (pow(1 + monthly_rate, tenure_months) - 1)
    
    return round(emi, 2)

def calculate_dti(existing_emi: float, new_emi: float, monthly_income: float) -> float:
    """
    Calculate Debt-to-Income ratio (%)
    """
    total_emi = existing_emi + new_emi
    dti_ratio = (total_emi / monthly_income) * 100
    return round(dti_ratio, 2)

def calculate_interest_rate(credit_score: int) -> float:
    """
    Calculate interest rate based on credit score
    """
    if credit_score >= 750:
        return 10.5
    elif credit_score >= 700:
        return 12.0
    elif credit_score >= 650:
        return 13.5
    elif credit_score >= 600:
        return 15.0
    else:
        return 18.0

def calculate_processing_fee(loan_amount: float) -> float:
    """
    Calculate processing fee (2% of loan amount)
    """
    fee = loan_amount * 0.02
    return max(1000, min(fee, 10000))  # Min 1000, Max 10000

def is_valid_pan(pan: str) -> bool:
    """
    Validate PAN format: ABCDE1234F
    """
    import re
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return bool(re.match(pattern, pan.upper()))