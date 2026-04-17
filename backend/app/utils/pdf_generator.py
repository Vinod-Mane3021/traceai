import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

# Assuming Vulnerability model is imported here
# from app.models.core import Vulnerability

def generate_soc2_audit_report(repo_name: str, vulnerabilities: list, start_date, end_date) -> io.BytesIO:
    """
    Generates a sleek, professional PDF audit report using ReportLab.
    Matches the design of the HTML-based generator for consistency.
    """
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        leftMargin=50, 
        rightMargin=50, 
        topMargin=60, 
        bottomMargin=70
    )
    styles = getSampleStyleSheet()

    # --- Custom Typography & Styles ---
    title_style = ParagraphStyle(
        'MainTitle', 
        parent=styles['Heading1'], 
        fontSize=22, 
        fontName='Helvetica-Bold',
        spaceAfter=2, 
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', 
        parent=styles['Normal'], 
        fontSize=10, 
        textColor=colors.HexColor("#64748b"), 
        textTransform='uppercase',
        letterSpacing=1.2,
        spaceAfter=30
    )
    meta_label_style = ParagraphStyle(
        'MetaLabel', 
        parent=styles['Normal'], 
        fontSize=9, 
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#475569"),
        letterSpacing=0.5
    )
    meta_value_style = ParagraphStyle(
        'MetaValue', 
        parent=styles['Normal'], 
        fontSize=10, 
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#0f172a")
    )
    
    elements = []

    # --- 1. Page Decoration (Blue Top Border) ---
    def add_page_decorations(canvas, doc):
        canvas.saveState()
        # Blue top border
        canvas.setFillColor(colors.HexColor("#2563eb"))
        canvas.rect(0, letter[1] - 10, letter[0], 10, fill=1, stroke=0)
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawString(50, 40, f"© {datetime.now().year} Trace AI. All rights reserved.")
        
        canvas.setFont('Helvetica-Bold', 8.5)
        canvas.setFillColor(colors.HexColor("#2563eb"))
        canvas.drawCentredString(letter[0]/2, 40, "TraceAI.com")
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawRightString(letter[0] - 50, 40, f"Page {doc.page} of 1") # Note: Total pages is complex in ReportLab
        canvas.restoreState()

    # --- 2. Header ---
    elements.append(Paragraph("SOC2 Security Audit Log", title_style))
    elements.append(Paragraph("Automated Intervention Report", subtitle_style))

    # Safe Date Formatting
    start_str = start_date[:10] if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d')
    end_str = end_date[:10] if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d')
    generated_on = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # --- 3. Metadata Box (Card Style) ---
    meta_data = [
        [Paragraph("REPOSITORY:", meta_label_style), Paragraph(repo_name, meta_value_style)],
        [Paragraph("AUDIT PERIOD:", meta_label_style), Paragraph(f"{start_str} — {end_str}", meta_value_style)],
        [Paragraph("GENERATED ON:", meta_label_style), Paragraph(f"{generated_on} UTC", meta_value_style)]
    ]
    
    meta_table = Table(meta_data, colWidths=[120, doc.width - 120])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEABOVE', (0, 0), (-1, 0), 0, colors.white), # Just to force border
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        # Blue left border (simulated)
        ('LINEBEFORE', (0, 0), (0, -1), 4, colors.HexColor("#2563eb")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 25))

    # --- 4. Content ---
    if not vulnerabilities:
        elements.append(Paragraph("✓ Status: Clear. No security violations detected during this period.", 
                                 ParagraphStyle('Success', parent=styles['Normal'], textColor=colors.HexColor("#065f46"), fontSize=11, fontName='Helvetica-Bold')))
    else:
        high_count = sum(1 for v in vulnerabilities if v.severity.lower() == "high")
        other_count = len(vulnerabilities) - high_count
        
        summary_text = f"<b>TOTAL INTERVENTIONS: {len(vulnerabilities)}</b> &nbsp;&nbsp; "
        summary_text += f"<font color='#b91c1c'>High: {high_count}</font> &nbsp;&nbsp; "
        summary_text += f"<font color='#b45309'>Medium/Low: {other_count}</font>"
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 15))

        # Data Table
        table_data = [[
            Paragraph("<b>DATE</b>", styles['Normal']),
            Paragraph("<b>SEVERITY</b>", styles['Normal']),
            Paragraph("<b>LOCATION</b>", styles['Normal']),
            Paragraph("<b>DESCRIPTION</b>", styles['Normal'])
        ]]

        for vuln in vulnerabilities:
            date_str = vuln.created_at[:10] if isinstance(vuln.created_at, str) else vuln.created_at.strftime('%Y-%m-%d')
            
            # Severity color coding
            sev_color = "#b91c1c" if vuln.severity.lower() == "high" else "#b45309"
            sev_bg = "#fef2f2" if vuln.severity.lower() == "high" else "#fffbeb"
            
            table_data.append([
                Paragraph(date_str, styles['Normal']),
                Paragraph(f"<font color='{sev_color}'><b>{vuln.severity.upper()}</b></font>", styles['Normal']),
                Paragraph(f"<b>{vuln.file_path}</b><br/><font color='#64748b' size='8'>Line {vuln.line_number}</font>", styles['Normal']),
                Paragraph(vuln.description, styles['Normal'])
            ])

        vuln_table = Table(table_data, colWidths=[doc.width * 0.15, doc.width * 0.15, doc.width * 0.30, doc.width * 0.40], repeatRows=1)
        vuln_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#334155")),
            ('FONTSIZE', (0, 0), (-1, 0), 8.5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(vuln_table)

    # --- Build ---
    doc.build(elements, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    buffer.seek(0)
    return buffer
    
# import io
# from datetime import datetime, timezone
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.colors import red, orange, green, black
# from app.models.core import Vulnerability


# def generate_soc2_audit_report(repo_name: str, vulnerabilities: list[Vulnerability], start_date: datetime, end_date: datetime) -> io.BytesIO:
#     """
#     Generates a PDF audit report in-memory and returns the buffer.
#     """
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     styles = getSampleStyleSheet()

#     # Custom Styles
#     title_style = styles["Heading1"]
#     subtitle_style = styles["Heading2"]
#     normal_style = styles["Normal"]

#     elements = []

#     # Header
#     elements.append(Paragraph(f"Trace AI - SOC2 Security Audit Log", title_style))
#     elements.append(Paragraph(f"Repository: {repo_name}", subtitle_style))
#     elements.append(Paragraph(f"Audit Period: {start_date} to {end_date}", normal_style))
#     elements.append(Paragraph(f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", normal_style))
#     elements.append(Spacer(1, 20))

#     if not vulnerabilities:
#         elements.append(Paragraph("✅ No security violations detected during this period.", normal_style))
#     else:
#         elements.append(Paragraph(f"Total Interventions: {len(vulnerabilities)}", subtitle_style))
#         elements.append(Spacer(1, 10))

#         # List each vulnerability
#         for vuln in vulnerabilities:
#             color = red if vuln.severity.lower() == "high" else orange
#             severity_style = ParagraphStyle('Severity', parent=normal_style, textColor=color)\

#             elements.append(Paragraph(f"<b>{vuln.created_at.strftime('%Y-%m-%d')} - {vuln.file_path} (Line {vuln.line_number})</b>", normal_style))
#             elements.append(Paragraph(f"Severity: {vuln.severity.upper()}", severity_style))
#             elements.append(Paragraph(f"Issue: {vuln.description}", normal_style))
#             elements.append(Spacer(1, 15))

#     # Build the PDF
#     doc.build(elements)

#     # Reset buffer position to the beginning so it can be read by FastAPI
#     buffer.seek(0)
#     return buffer