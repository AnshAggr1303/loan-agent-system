# ============================================================================
# LANGCHAIN TOOLS - All 13 Tools
# Path: backend/tools/loan_tools.py
# ============================================================================

from langchain_core.tools import tool
from typing import Optional, Dict, Any
import json
from mock_data.kyc_database import verify_kyc, calculate_age
from mock_data.credit_database import fetch_credit_score
from utils.calculations import (
    calculate_emi, 
    calculate_dti, 
    calculate_interest_rate,
    calculate_processing_fee
)
from database.supabase_client import get_supabase_client
from rag.retriever import KnowledgeRetriever
import uuid

# ============================================================================
# TOOL 1: VERIFY KYC
# ============================================================================

@tool
async def verify_kyc_tool(pan: str) -> str:
    """
    Verify customer's PAN number and fetch KYC details.
    Use this when customer provides their PAN number.
    
    Args:
        pan: PAN number in format ABCDE1234F
    
    Returns:
        JSON string with KYC details or error
    """
    try:
        record = await verify_kyc(pan.upper())
        
        if not record:
            return json.dumps({
                "success": False,
                "verified": False,
                "error": "PAN not found in records. Please verify the PAN number is correct.",
                "action_required": "Ask customer to provide valid PAN number"
            })
        
        kyc_status = record.get("kyc_status", "")
        
        if kyc_status != "VERIFIED":
            return json.dumps({
                "success": False,
                "verified": False,
                "kyc_status": kyc_status,
                "error": f"KYC verification incomplete. Status: {kyc_status}",
                "action_required": "Customer needs to complete KYC verification before applying for loan. Politely inform them they cannot proceed without verified KYC."
            })
        
        age = calculate_age(record.get("date_of_birth"))
        
        return json.dumps({
            "success": True,
            "verified": True,
            "data": {
                "pan_number": record.get("pan_number"),
                "full_name": record.get("full_name"),
                "date_of_birth": record.get("date_of_birth"),
                "age": age,
                "phone": record.get("phone"),
                "kyc_status": record.get("kyc_status"),
                "address": record.get("address")
            }
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "verified": False,
            "error": f"KYC verification failed: {str(e)}"
        })

# ============================================================================
# TOOL 2: CHECK CREDIT SCORE
# ============================================================================

@tool
async def check_credit_score_tool(pan: str) -> str:
    """
    Fetch customer's credit score from credit bureau.
    Use this after KYC is verified.
    
    Args:
        pan: Customer's PAN number
    
    Returns:
        JSON string with credit score details
    """
    try:
        credit_record = await fetch_credit_score(pan.upper())
        
        if not credit_record:
            return json.dumps({
                "success": False,
                "error": "No credit history found for this PAN."
            })
        
        score = credit_record.get("score")
        
        # Determine eligibility based on score
        if score >= 750:
            score_category = "Excellent"
            eligible = True
        elif score >= 700:
            score_category = "Very Good"
            eligible = True
        elif score >= 650:
            score_category = "Good"
            eligible = True
        else:
            score_category = "Needs Improvement"
            eligible = False
        
        return json.dumps({
            "success": True,
            "eligible": eligible,
            "data": {
                "score": score,
                "score_category": score_category,
                "status": credit_record.get("status"),
                "active_loans": credit_record.get("active_loans"),
                "credit_history_years": credit_record.get("credit_history_years"),
                "defaults": credit_record.get("defaults"),
                "minimum_required": 650,
                "meets_minimum": score >= 650
            }
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# ============================================================================
# TOOL 3: CHECK EXISTING CUSTOMER
# ============================================================================

@tool
async def check_existing_customer_tool(pan: str) -> str:
    """
    Check if customer already exists in our database.
    Use this to retrieve saved information and avoid asking again.
    
    Args:
        pan: Customer's PAN number
    
    Returns:
        JSON string with customer data if exists
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("customers").select("*").eq("pan_number", pan.upper()).execute()
        
        if not result.data or len(result.data) == 0:
            return json.dumps({
                "exists": False,
                "message": "Customer not found. This is a new customer."
            })
        
        customer = result.data[0]
        
        return json.dumps({
            "exists": True,
            "data": {
                "customer_id": customer.get("id"),
                "full_name": customer.get("full_name"),
                "age": customer.get("age"),
                "phone": customer.get("phone"),
                "email": customer.get("email"),
                "employment_type": customer.get("employment_type"),
                "monthly_income": customer.get("monthly_income"),
                "kyc_status": customer.get("kyc_status")
            }
        })
    except Exception as e:
        return json.dumps({"exists": False, "error": str(e)})

# ============================================================================
# TOOL 4: CALCULATE ELIGIBILITY
# ============================================================================

@tool
def calculate_eligibility_tool(monthly_income: float, employment_type: str, existing_emi: float = 0) -> str:
    """
    Calculate maximum eligible loan amount based on income.
    
    Args:
        monthly_income: Monthly income in rupees
        employment_type: One of 'Salaried', 'Self-Employed', 'Business Owner'
        existing_emi: Existing monthly EMI obligations (default 0)
    
    Returns:
        JSON string with eligibility details
    """
    try:
        multipliers = {
            "Salaried": 10,
            "Self-Employed": 5,
            "Business Owner": 8
        }
        
        multiplier = multipliers.get(employment_type, 5)
        max_loan_amount = monthly_income * multiplier
        
        # Calculate affordable EMI (50% of income minus existing EMI)
        affordable_emi = (monthly_income * 0.5) - existing_emi
        
        # Max loan based on affordable EMI (rough estimate)
        max_loan_from_emi = affordable_emi * 30 if affordable_emi > 0 else 0
        
        eligible_amount = min(max_loan_amount, max_loan_from_emi)
        
        return json.dumps({
            "max_eligible_amount": int(eligible_amount),
            "monthly_income": monthly_income,
            "employment_type": employment_type,
            "existing_emi": existing_emi,
            "affordable_new_emi": max(0, affordable_emi),
            "calculation_basis": f"Based on {multiplier}x monthly income"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# ============================================================================
# TOOL 5: CHECK BUSINESS RULES
# ============================================================================

@tool
def check_business_rules_tool(
    age: int,
    monthly_income: float,
    employment_type: str,
    credit_score: int,
    loan_amount: float,
    existing_emi: float,
    tenure: int
) -> str:
    """
    Validate if loan application meets all business rules.
    
    Args:
        age: Customer age
        monthly_income: Monthly income
        employment_type: Employment type
        credit_score: Credit score
        loan_amount: Requested loan amount
        existing_emi: Existing EMI
        tenure: Loan tenure in months
    
    Returns:
        JSON string with rule validation results
    """
    try:
        rules = {
            "age_check": 21 <= age <= 60,
            "income_check": monthly_income >= (25000 if employment_type == "Salaried" else 40000),
            "credit_score_check": credit_score >= 650
        }
        
        # Calculate DTI
        interest_rate = calculate_interest_rate(credit_score)
        monthly_emi = calculate_emi(loan_amount, interest_rate, tenure)
        dti_ratio = calculate_dti(existing_emi, monthly_emi, monthly_income)
        rules["dti_check"] = dti_ratio <= 50
        
        failed_rules = []
        if not rules["age_check"]:
            failed_rules.append("Age must be between 21-60 years")
        if not rules["income_check"]:
            min_income = 25000 if employment_type == "Salaried" else 40000
            failed_rules.append(f"Minimum income: ₹{min_income:,}")
        if not rules["credit_score_check"]:
            failed_rules.append("Minimum credit score: 650")
        if not rules["dti_check"]:
            failed_rules.append(f"DTI ratio {dti_ratio:.1f}% exceeds 50%")
        
        return json.dumps({
            "all_rules_passed": len(failed_rules) == 0,
            "rules_evaluation": rules,
            "failed_rules": failed_rules,
            "dti_ratio": dti_ratio,
            "estimated_emi": monthly_emi,
            "interest_rate": interest_rate
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# ============================================================================
# TOOL 6: MAKE UNDERWRITING DECISION
# ============================================================================

@tool
def make_underwriting_decision_tool(customer_data: str) -> str:
    """
    Make final loan approval/rejection decision.
    This is the final decision tool after all data is collected.
    
    Args:
        customer_data: JSON string with all customer data
    
    Returns:
        JSON string with approval/rejection decision
    """
    try:
        data = json.loads(customer_data)
        
        # Extract required fields with defaults
        age = data.get("age")
        monthly_income = data.get("monthly_income")
        employment_type = data.get("employment_type")
        credit_score = data.get("credit_score") or data.get("score")  # Handle both field names
        loan_amount = data.get("loan_amount_requested") or data.get("loan_amount") or data.get("max_eligible_amount")
        tenure = data.get("tenure", 36)  # Default to 36 months if not provided
        existing_emi = data.get("existing_emi", 0)
        
        # Validate required fields
        if not all([age, monthly_income, employment_type, credit_score, loan_amount]):
            missing = []
            if not age: missing.append("age")
            if not monthly_income: missing.append("monthly_income")
            if not employment_type: missing.append("employment_type")
            if not credit_score: missing.append("credit_score")
            if not loan_amount: missing.append("loan_amount")
            
            return json.dumps({
                "error": f"Missing required fields: {', '.join(missing)}"
            })
        
        failed_rules = []
        
        # Age check
        if age < 21 or age > 60:
            failed_rules.append("Age requirement not met (21-60)")
        
        # Income check
        min_income = 25000 if employment_type == "Salaried" else 40000
        if monthly_income < min_income:
            failed_rules.append(f"Minimum income ₹{min_income:,}")
        
        # Credit score check
        if credit_score < 650:
            failed_rules.append("Credit score below 650")
        
        # DTI check
        interest_rate = calculate_interest_rate(credit_score)
        monthly_emi = calculate_emi(loan_amount, interest_rate, tenure)
        dti_ratio = calculate_dti(existing_emi, monthly_emi, monthly_income)
        
        if dti_ratio > 50:
            failed_rules.append(f"DTI ratio {dti_ratio:.1f}% exceeds 50%")
        
        # Decision
        if failed_rules:
            return json.dumps({
                "approved": False,
                "decision": "rejected",
                "failed_rules": failed_rules,
                "rejection_reason": "Application does not meet eligibility criteria"
            })
        
        processing_fee = calculate_processing_fee(loan_amount)
        
        return json.dumps({
            "approved": True,
            "decision": "approved",
            "sanctioned_amount": loan_amount,
            "interest_rate": interest_rate,
            "monthly_emi": monthly_emi,
            "tenure": tenure,
            "dti_ratio": dti_ratio,
            "processing_fee": processing_fee
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# ============================================================================
# TOOL 7: CREATE/UPDATE CUSTOMER
# ============================================================================

@tool
async def create_or_update_customer_tool(customer_data: str) -> str:
    """
    Create new customer or update existing customer in database.
    
    Args:
        customer_data: JSON string with customer information
    
    Returns:
        JSON string with customer_id
    """
    try:
        data = json.loads(customer_data)
        supabase = get_supabase_client()
        
        # Filter to only customer table fields (not credit data)
        customer_fields = {
            "pan_number": data.get("pan_number"),
            "full_name": data.get("full_name"),
            "dob": data.get("date_of_birth"),
            "age": data.get("age"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "kyc_status": data.get("kyc_status", "verified"),
            "employment_type": data.get("employment_type"),
            "monthly_income": data.get("monthly_income"),
            "company_name": data.get("company_name"),
        }
        
        # Remove None values
        customer_fields = {k: v for k, v in customer_fields.items() if v is not None}
        
        # PAN is required
        if not customer_fields.get("pan_number"):
            return json.dumps({"success": False, "error": "PAN number is required"})
        
        # Check if exists
        existing = supabase.table("customers").select("id").eq("pan_number", customer_fields["pan_number"]).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update
            result = supabase.table("customers").update(customer_fields).eq("pan_number", customer_fields["pan_number"]).execute()
            return json.dumps({
                "success": True,
                "customer_id": existing.data[0]["id"],
                "action": "updated"
            })
        else:
            # Create
            result = supabase.table("customers").insert(customer_fields).execute()
            return json.dumps({
                "success": True,
                "customer_id": result.data[0]["id"],
                "action": "created"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# ============================================================================
# TOOL 8: SAVE APPLICATION
# ============================================================================

@tool
async def save_application_tool(application_data: str) -> str:
    """
    Save loan application to database.
    
    Args:
        application_data: JSON string with application details
    
    Returns:
        JSON string with application_id
    """
    try:
        data = json.loads(application_data)
        supabase = get_supabase_client()
        
        result = supabase.table("loan_applications").insert(data).execute()
        
        return json.dumps({
            "success": True,
            "application_id": result.data[0]["id"]
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# ============================================================================
# TOOL 9: RETRIEVE KNOWLEDGE (RAG)
# ============================================================================

@tool
def retrieve_knowledge_tool(query: str) -> str:
    """
    Search knowledge base for product information, rates, policies.
    Use this to answer customer questions about our loans.
    
    Args:
        query: What information to search for
    
    Returns:
        Relevant information from knowledge base
    """
    try:
        retriever = KnowledgeRetriever()
        context = retriever.get_context(query, top_k=3)
        
        return json.dumps({
            "found": True,
            "context": context
        })
    except Exception as e:
        return json.dumps({"found": False, "error": str(e)})

# ============================================================================
# TOOL 10: SAVE CONVERSATION
# ============================================================================

@tool
async def save_conversation_tool(session_id: str, stage: str, collected_data: str) -> str:
    """
    Update conversation session state.
    
    Args:
        session_id: Session ID (must be valid UUID)
        stage: Current conversation stage
        collected_data: JSON string of collected data
    
    Returns:
        Success status
    """
    try:
        supabase = get_supabase_client()
        
        # Validate UUID format
        import uuid as uuid_lib
        try:
            uuid_lib.UUID(session_id)
        except ValueError:
            return json.dumps({"success": False, "error": "Invalid session_id format. Must be UUID."})
        
        data_dict = json.loads(collected_data)
        
        supabase.table("conversation_sessions").update({
            "current_stage": stage,
            "collected_data": data_dict
        }).eq("id", session_id).execute()
        
        return json.dumps({"success": True})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# ============================================================================
# TOOL 11: GET APPLICATION HISTORY
# ============================================================================

@tool
async def get_application_history_tool(customer_id: str) -> str:
    """
    Get customer's past loan applications.
    
    Args:
        customer_id: Customer ID
    
    Returns:
        JSON string with application history
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("loan_applications").select("*").eq("customer_id", customer_id).order("created_at", desc=True).limit(5).execute()
        
        if not result.data or len(result.data) == 0:
            return json.dumps({
                "has_history": False,
                "message": "No previous applications"
            })
        
        return json.dumps({
            "has_history": True,
            "total_applications": len(result.data),
            "applications": result.data
        })
    except Exception as e:
        return json.dumps({"has_history": False, "error": str(e)})

# ============================================================================
# TOOL 12: GENERATE SANCTION LETTER
# ============================================================================

@tool
async def generate_sanction_letter_tool(application_data: str) -> str:
    """
    Generate PDF sanction letter for approved loan and upload to Supabase Storage.
    Only use after loan is approved.
    
    Args:
        application_data: JSON string with application details
    
    Returns:
        JSON string with public PDF URL
    """
    try:
        from utils.pdf_generator import create_sanction_letter
        
        data = json.loads(application_data)
        
        # Generate PDF and upload to Supabase Storage
        pdf_bytes, public_url = create_sanction_letter(data)
        
        return json.dumps({
            "success": True,
            "message": "Sanction letter generated successfully",
            "download_url": public_url,
            "file_size_kb": len(pdf_bytes) / 1024
        })
    except Exception as e:
        print(f"❌ Error generating sanction letter: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to generate sanction letter: {str(e)}"
        })

# ============================================================================
# TOOL 13: CALCULATE EMI
# ============================================================================

@tool
def calculate_emi_tool(loan_amount: float, interest_rate: float, tenure: int) -> str:
    """
    Calculate monthly EMI for given loan parameters.
    
    Args:
        loan_amount: Loan amount in rupees
        interest_rate: Annual interest rate
        tenure: Tenure in months
    
    Returns:
        JSON string with EMI and other details
    """
    try:
        emi = calculate_emi(loan_amount, interest_rate, tenure)
        total_payment = emi * tenure
        total_interest = total_payment - loan_amount
        
        return json.dumps({
            "monthly_emi": round(emi, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "tenure": tenure
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# ============================================================================
# EXPORT ALL TOOLS
# ============================================================================

ALL_TOOLS = [
    verify_kyc_tool,
    check_credit_score_tool,
    check_existing_customer_tool,
    calculate_eligibility_tool,
    check_business_rules_tool,
    make_underwriting_decision_tool,
    create_or_update_customer_tool,
    save_application_tool,
    retrieve_knowledge_tool,
    save_conversation_tool,
    get_application_history_tool,
    generate_sanction_letter_tool,
    calculate_emi_tool
]

def get_all_tools():
    """Return all tools for LangChain agent"""
    return ALL_TOOLS