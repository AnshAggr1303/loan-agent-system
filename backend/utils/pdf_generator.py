# ============================================================================
# PDF GENERATOR - Sanction Letter with Supabase Storage
# Path: backend/utils/pdf_generator.py
# ============================================================================

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
from database.supabase_client import get_supabase_client
import uuid

def create_sanction_letter(application_data: dict) -> tuple[bytes, str]:
    """
    Generate sanction letter PDF and upload to Supabase Storage
    
    Returns:
        tuple: (pdf_bytes, public_url)
    """
    
    # Extract data
    customer_name = application_data.get("customer_name", "Valued Customer")
    loan_amount = application_data.get("loan_amount", 0)
    interest_rate = application_data.get("interest_rate", 0)
    tenure = application_data.get("tenure", 0)
    monthly_emi = application_data.get("monthly_emi", 0)
    processing_fee = application_data.get("processing_fee", 0)
    application_id = application_data.get("application_id", str(uuid.uuid4()))
    pan = application_data.get("pan_number", "N/A")
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8
    )
    
    # Build content
    content = []
    
    # Header
    content.append(Paragraph("QUICKLOAN NBFC", title_style))
    content.append(Paragraph("Personal Loan Sanction Letter", subtitle_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Date and Reference
    today = datetime.now().strftime("%B %d, %Y")
    content.append(Paragraph(f"<b>Date:</b> {today}", normal_style))
    content.append(Paragraph(f"<b>Reference No:</b> QL-{application_id[:8].upper()}", normal_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Customer Details
    content.append(Paragraph("Dear " + customer_name + ",", heading_style))
    content.append(Spacer(1, 0.1*inch))
    
    # Approval Message
    approval_text = f"""
    We are pleased to inform you that your personal loan application has been <b>APPROVED</b>. 
    After careful evaluation of your profile and creditworthiness, we are sanctioning the following loan:
    """
    content.append(Paragraph(approval_text, normal_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Loan Details Table
    loan_details = [
        ["Loan Details", ""],
        ["Sanctioned Amount", f"₹{loan_amount:,.2f}"],
        ["Interest Rate", f"{interest_rate}% per annum"],
        ["Loan Tenure", f"{tenure} months"],
        ["Monthly EMI", f"₹{monthly_emi:,.2f}"],
        ["Processing Fee", f"₹{processing_fee:,.2f}"],
        ["Total Repayment", f"₹{(monthly_emi * tenure):,.2f}"],
    ]
    
    table = Table(loan_details, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(table)
    content.append(Spacer(1, 0.3*inch))
    
    # Terms & Conditions
    content.append(Paragraph("Terms & Conditions:", heading_style))
    
    terms = [
        "1. This sanction is valid for 30 days from the date of issue.",
        "2. The loan will be disbursed upon submission of required documents.",
        "3. EMI payments must be made on or before the due date to avoid penalties.",
        "4. Prepayment is allowed after 6 months with a 2% prepayment charge.",
        "5. The interest rate is fixed for the entire tenure.",
        "6. Late payment charges of 2% per month will apply on overdue EMIs.",
    ]
    
    for term in terms:
        content.append(Paragraph(term, normal_style))
    
    content.append(Spacer(1, 0.3*inch))
    
    # Documents Required
    content.append(Paragraph("Documents Required for Disbursal:", heading_style))
    
    docs = [
        "• PAN Card copy",
        "• Aadhaar Card copy",
        "• Last 3 months salary slips",
        "• Last 6 months bank statements",
        "• Passport size photographs (2 copies)",
    ]
    
    for doc in docs:
        content.append(Paragraph(doc, normal_style))
    
    content.append(Spacer(1, 0.3*inch))
    
    # Closing
    closing_text = """
    Congratulations on your loan approval! Please contact our customer service team at 1800-XXX-XXXX 
    or visit our nearest branch to complete the documentation process.
    """
    content.append(Paragraph(closing_text, normal_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Signature
    content.append(Paragraph("Yours sincerely,", normal_style))
    content.append(Spacer(1, 0.5*inch))
    content.append(Paragraph("<b>QuickLoan NBFC</b>", normal_style))
    content.append(Paragraph("Loan Approval Team", normal_style))
    
    # Build PDF
    doc.build(content)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    # Upload to Supabase Storage
    try:
        supabase = get_supabase_client()
        filename = f"sanction-letter-{application_id}.pdf"
        
        # Upload to storage
        supabase.storage.from_("sanction-letters").upload(
            filename,
            pdf_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_("sanction-letters").get_public_url(filename)
        
        return pdf_bytes, public_url
        
    except Exception as e:
        print(f"❌ Error uploading to Supabase Storage: {e}")
        # Return with fallback URL
        return pdf_bytes, f"/api/documents/{application_id}/download"

def upload_pdf_to_storage(pdf_bytes: bytes, filename: str) -> str:
    """
    Upload PDF to Supabase Storage
    
    Returns:
        str: Public URL
    """
    try:
        supabase = get_supabase_client()
        
        supabase.storage.from_("sanction-letters").upload(
            filename,
            pdf_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
        
        public_url = supabase.storage.from_("sanction-letters").get_public_url(filename)
        return public_url
        
    except Exception as e:
        print(f"❌ Error uploading PDF: {e}")
        raise