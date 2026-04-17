import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import red, orange, green, black
from app.models.core import Vulnerability


def generate_soc2_audit_report(repo_name: str, vulnerabilities: list[Vulnerability], start_date: datetime, end_date: datetime) -> io.BytesIO:
    """
    Generates a PDF audit report in-memory and returns the buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]

    elements = []

    # Header
    elements.append(Paragraph(f"Trace AI - SOC2 Security Audit Log", title_style)) 
    elements.append(Paragraph(f"Repository: {repo_name}", subtitle_style))
    elements.append(Paragraph(f"Audit Period: {start_date} to {end_date}", normal_style))
    elements.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", normal_style))
    elements.append(Spacer(1, 20))

    if not vulnerabilities:
        elements.append(Paragraph("✅ No security violations detected during this period.", normal_style))
    else:
        elements.append(Paragraph(f"Total Interventions: {len(vulnerabilities)}", subtitle_style))
        elements.append(Spacer(1, 10))

        # List each vulnerability
        for vuln in vulnerabilities:
            color = red if vuln.severity.lower() == "high" else orange
            severity_style = ParagraphStyle('Severity', parent=normal_style, textColor=color)\
            
            elements.append(Paragraph(f"<b>{vuln.created_at.strftime('%Y-%m-%d')} - {vuln.file_path} (Line {vuln.line_number})</b>", normal_style))
            elements.append(Paragraph(f"Severity: {vuln.severity.upper()}", severity_style))
            elements.append(Paragraph(f"Issue: {vuln.description}", normal_style))
            elements.append(Spacer(1, 15))

    # Build the PDF
    doc.build(elements)

    # Reset buffer position to the beginning so it can be read by FastAPI
    buffer.seek(0)
    return buffer