"""
Onboarding Agent - Send welcome packages to hired candidates
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from agents.email_agent import send_onboarding_email


def send_welcome_package(candidate: dict, role: str) -> dict:
    """
    Send onboarding welcome email with documents to a hired candidate.
    
    Returns:
        dict with status and message
    """
    name = candidate.get("name", "Candidate")
    email = candidate.get("email", "")
    
    if not email:
        return {"status": "error", "message": f"No email address for candidate {name}"}
        
    salary = candidate.get("salary", "$120,000") # Default or passed in value
        
    try:
        pdf_path = _generate_offer_pdf(name, role, salary)
        
        # In a real system, you'd attach the specific PDF to candidate's email
        # For this prototype, send_onboarding_email looks inside data/onboarding_docs
        # So we ensure the PDF is saved there.
        success = send_onboarding_email(candidate, role)
        if success:
            return {
                "status": "sent",
                "message": f"Welcome package with Offer Letter sent to {name} at {email}"
            }
        else:
            return {
                "status": "not_configured",
                "message": "Gmail credentials not configured. Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _generate_offer_pdf(name: str, role: str, salary: str) -> str:
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "onboarding_docs")
    os.makedirs(out_dir, exist_ok=True)
    
    pdf_path = os.path.join(out_dir, f"Offer_Letter_{name.replace(' ', '_')}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 80, "OFFICIAL LETTER OF OFFER")
    
    c.setFont("Helvetica", 12)
    today = datetime.now().strftime("%B %d, %Y")
    c.drawString(50, height - 120, f"Date: {today}")
    
    c.drawString(50, height - 160, f"Dear {name},")
    
    text = f"We are thrilled to offer you the position of {role}."
    c.drawString(50, height - 190, text)
    
    text2 = f"Your starting base salary will be {salary} per year."
    c.drawString(50, height - 210, text2)
    
    text3 = "Welcome to the team! We look forward to building great things together."
    c.drawString(50, height - 240, text3)
    
    c.drawString(50, height - 300, "Sincerely,")
    c.drawString(50, height - 320, "HR Director")
    
    c.save()
    return pdf_path
