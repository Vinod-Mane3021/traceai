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
    Generates a cleanly formatted, UX-optimized PDF audit report in-memory 
    using dynamic column widths to prevent LayoutErrors.
    Safely handles both string and datetime inputs.
    """
    buffer = io.BytesIO()
    
    # Set up the document with standard 1-inch margins (72 points)
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        leftMargin=72, 
        rightMargin=72, 
        topMargin=72, 
        bottomMargin=72
    )
    styles = getSampleStyleSheet()

    # --- Custom Typography Styles ---
    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=6, alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Heading3'], fontSize=12, textColor=colors.slategray, alignment=TA_CENTER, spaceAfter=20
    )
    normal_style = styles["Normal"]
    
    elements = []

    # --- 1. Document Header ---
    elements.append(Paragraph("<b>Trace AI</b> - SOC2 Security Audit Log", title_style))
    elements.append(Paragraph("Automated Vulnerability Intervention Report", subtitle_style))

    # --- Safe Date Formatting ---
    # Slices first 10 chars of a string to get 'YYYY-MM-DD' or uses strftime if it's a datetime obj
    start_str = start_date[:10] if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d')
    end_str = end_date[:10] if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d')

    # --- 2. Metadata Section (Dynamic Proportional Widths) ---
    meta_data = [
        [Paragraph("<b>Repository:</b>", normal_style), Paragraph(repo_name, normal_style)],
        [Paragraph("<b>Audit Period:</b>", normal_style), Paragraph(f"{start_str} to {end_str}", normal_style)],
        [Paragraph("<b>Generated On:</b>", normal_style), Paragraph(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", normal_style)]
    ]
    
    # 20% for labels, 80% for values
    meta_widths = [doc.width * 0.20, doc.width * 0.80]
    meta_table = Table(meta_data, colWidths=meta_widths, hAlign='LEFT')
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))

    # --- 3. Vulnerability Summary ---
    if not vulnerabilities:
        success_style = ParagraphStyle('Success', parent=normal_style, textColor=colors.darkgreen, fontSize=12)
        elements.append(Paragraph("✅ <b>Status: Clear.</b> No security violations detected during this period.", success_style))
    else:
        # Calculate Metrics
        high_count = sum(1 for v in vulnerabilities if v.severity.lower() == "high")
        other_count = len(vulnerabilities) - high_count
        
        summary_text = f"<b>Total Interventions: {len(vulnerabilities)}</b> "
        summary_text += f"(<font color='red'>High: {high_count}</font> | <font color='orange'>Medium/Low: {other_count}</font>)"
        
        elements.append(Paragraph(summary_text, styles['Heading3']))
        elements.append(Spacer(1, 10))

        # --- 4. Vulnerability Data Table ---
        table_data = [[
            Paragraph("<b>Date</b>", normal_style),
            Paragraph("<b>Severity</b>", normal_style),
            Paragraph("<b>Location</b>", normal_style),
            Paragraph("<b>Description</b>", normal_style)
        ]]

        # Populate table rows
        for vuln in vulnerabilities:
            # Format Date Safely (in case vuln.created_at is also returning a string from SQLAlchemy)
            vuln_date_str = vuln.created_at[:10] if isinstance(vuln.created_at, str) else vuln.created_at.strftime('%Y-%m-%d')
            date_p = Paragraph(vuln_date_str, normal_style)
            
            # Format Severity with color
            is_high = vuln.severity.lower() == "high"
            sev_color = colors.red if is_high else colors.darkorange
            sev_style = ParagraphStyle('Sev', parent=normal_style, textColor=sev_color, fontName="Helvetica-Bold")
            sev_p = Paragraph(vuln.severity.upper(), sev_style)
            
            # Format Location 
            loc_p = Paragraph(f"{vuln.file_path}<br/><font color='gray'>Line {vuln.line_number}</font>", normal_style)
            
            # Format Description
            desc_p = Paragraph(vuln.description, normal_style)

            table_data.append([date_p, sev_p, loc_p, desc_p])

        # Distribute the columns proportionally based on the document's usable width
        vuln_widths = [doc.width * 0.14, doc.width * 0.13, doc.width * 0.30, doc.width * 0.43]
        
        vuln_table = Table(table_data, colWidths=vuln_widths, repeatRows=1)
        
        # Apply Table Styling
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f4f4f5")),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ])
        
        # Add Zebra Striping logic
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#fafafa"))

        vuln_table.setStyle(table_style)
        elements.append(vuln_table)

    # --- Build and Return ---
    doc.build(elements)
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