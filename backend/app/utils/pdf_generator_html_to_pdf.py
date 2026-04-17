import io
import logging
from datetime import datetime, timezone
from jinja2 import Template

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception as e:
    logger.warning(f"WeasyPrint could not be loaded (likely missing system dependencies): {e}")
    WEASYPRINT_AVAILABLE = False
    # Fallback to reportlab-based generator if available
    try:
        from app.utils.pdf_generator import generate_soc2_audit_report as generate_reportlab_pdf
    except ImportError:
        generate_reportlab_pdf = None

def generate_soc2_audit_report(repo_name: str, vulnerabilities: list, start_date, end_date) -> io.BytesIO:
    """
    Generates a sleek, professional PDF audit report by rendering an HTML template 
    and converting it via WeasyPrint into an in-memory buffer.
    Falls back to ReportLab if WeasyPrint is not available.
    """
    if not WEASYPRINT_AVAILABLE:
        if generate_reportlab_pdf:
            logger.info("Falling back to ReportLab for PDF generation.")
            return generate_reportlab_pdf(repo_name, vulnerabilities, start_date, end_date)
        else:
            raise ImportError(
                "Neither WeasyPrint nor ReportLab are available for PDF generation. "
                "Please install dependencies."
            )

    # --- Safe Date Formatting ---
    start_str = start_date[:10] if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d')
    end_str = end_date[:10] if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d')
    generated_on = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Calculate metrics
    high_count = sum(1 for v in vulnerabilities if v.severity.lower() == "high")
    medium_count = sum(1 for v in vulnerabilities if v.severity.lower() == "medium")
    low_count = sum(1 for v in vulnerabilities if v.severity.lower() == "low")

    # --- HTML & CSS Template ---
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            /* --- Page Setup & Borders --- */
            @page {
                size: letter;
                margin: 0.5in 0.5in 0.75in 0.5in; /* Reduced margins */
                
                /* Sleek page borders */
                border-top: 8px solid #2563eb;
                
                /* Rich Footer Configuration */
                @bottom-left {
                    content: "© " counter(year) " Trace AI. All rights reserved.";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #94a3b8;
                    letter-spacing: 0.5px;
                }
                @bottom-center {
                    content: "TraceAI.com";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8.5pt;
                    font-weight: 600;
                    color: #2563eb;
                    letter-spacing: 0.5px;
                }
                @bottom-right {
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    font-weight: 500;
                    color: #64748b;
                }
            }

            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #334155;
                line-height: 1.65;
                font-size: 10pt;
                margin: 0;
                padding: 0;
                letter-spacing: 0.01em; /* Richer text spacing */
            }

            /* --- Header Layout --- */
            .header-table {
                width: 100%;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 12px;
                margin-bottom: 20px;
            }
            .logo-cell {
                width: 40%;
                vertical-align: middle;
            }
            /* REPLACE THE SRC ATTRIBUTE WITH YOUR ACTUAL LOGO URL OR BASE64 STRING */
            .logo-img {
                max-height: 35px;
                display: block;
            }
            .title-cell {
                width: 60%;
                text-align: right;
                vertical-align: middle;
            }
            h1 {
                margin: 0 0 4px 0;
                font-size: 20pt;
                font-weight: 800;
                color: #0f172a;
                letter-spacing: -0.5px;
            }
            .subtitle {
                margin: 0;
                color: #64748b;
                font-size: 10.5pt;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1.2px;
            }
            
            /* --- Spacers --- */
            hr.spacer {
                border: none;
                border-top: 1px dashed #cbd5e1;
                margin: 25px 0;
            }

            /* --- Metadata Box (Card Style) --- */
            .meta-box {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #2563eb;
                border-radius: 6px;
                padding: 14px 20px;
                margin-bottom: 20px;
            }
            .meta-table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            .meta-table td { 
                padding: 4px 0; 
                font-size: 10.5pt;
            }
            .meta-label { 
                font-weight: 700; 
                width: 150px; 
                color: #475569; 
                letter-spacing: 0.5px;
            }
            .meta-value {
                color: #0f172a;
                font-weight: 500;
            }
            
            /* --- Summary Section --- */
            .summary-box {
                font-size: 11pt;
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            .status-clear {
                color: #065f46;
                font-weight: 600;
                background-color: #d1fae5;
                border: 1px solid #34d399;
                padding: 12px 18px;
                border-radius: 6px;
                display: block;
            }
            .metric { 
                font-weight: 800; 
                color: #0f172a;
                font-size: 11.5pt;
            }
            
            /* --- Badges --- */
            .badge {
                padding: 5px 12px;
                border-radius: 9999px;
                font-size: 7.5pt;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                display: inline-block;
            }
            .badge-high { 
                background-color: #fef2f2; 
                color: #b91c1c; 
                border: 1px solid #fecaca;
            }
            .badge-med { 
                background-color: #fffbeb; 
                color: #b45309; 
                border: 1px solid #fde68a;
            }
            .badge-low { 
                background-color: #f0fdf4; 
                color: #15803d; 
                border: 1px solid #bbf7d0;
            }
            
            /* --- Data Table --- */
            .table-container {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                overflow: hidden; /* Helps clip inner borders to rounded edges */
            }
            .data-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
            }
            
            /* Prevent rows from breaking across pages */
            .data-table tr {
                page-break-inside: avoid;
                break-inside: avoid;
            }
            
            .data-table th, .data-table td {
                text-align: left;
                padding: 14px 16px;
                border-bottom: 1px solid #e2e8f0;
                vertical-align: top;
            }
            .data-table th {
                background-color: #f8fafc;
                color: #334155;
                font-size: 8.5pt;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 2px solid #cbd5e1;
            }
            .data-table tr:last-child td {
                border-bottom: none;
            }
            .data-table tbody tr:nth-child(even) { 
                background-color: #fafafa; 
            }
            
            .location-text { 
                color: #0f172a; 
                font-weight: 700; 
                font-family: 'Consolas', 'Courier New', Courier, monospace;
                font-size: 9.5pt;
                word-break: break-all;
            }
            .line-number { 
                color: #64748b; 
                font-size: 9pt; 
                display: block; 
                margin-top: 4px;
                font-weight: 500;
            }
            .date-text { 
                color: #475569; 
                white-space: nowrap; 
                font-weight: 600;
            }
            .time-text {
                color: #64748b;
                font-size: 8.5pt;
                font-weight: 500;
                display: block;
                margin-top: 2px;
            }
            .sr-text {
                color: #64748b;
                font-weight: 700;
            }
            .desc-text {
                color: #1e293b;
            }
        </style>
    </head>
    <body>
        <table class="header-table">
            <tr>
                <td class="logo-cell">
                    <img class="logo-img" src="https://via.placeholder.com/200x50/2563eb/ffffff?text=Trace+AI+Logo" alt="Trace AI">
                </td>
                <td class="title-cell">
                    <h1>SOC2 Security Audit Log</h1>
                    <p class="subtitle">Automated Intervention Report</p>
                </td>
            </tr>
        </table>

        <div class="meta-box">
            <table class="meta-table">
                <tr><td class="meta-label">REPOSITORY:</td><td class="meta-value">{{ repo_name }}</td></tr>
                <tr><td class="meta-label">AUDIT PERIOD:</td><td class="meta-value">{{ start_str }} &nbsp;&mdash;&nbsp; {{ end_str }}</td></tr>
                <tr><td class="meta-label">GENERATED ON:</td><td class="meta-value">{{ generated_on }} UTC</td></tr>
            </table>
        </div>

        <hr class="spacer">

        {% if vulnerabilities|length == 0 %}
            <div class="status-clear">
                ✓ Status: Clear. No security violations detected during this period.
            </div>
        {% else %}
            <div class="summary-box">
                <span class="metric">TOTAL INTERVENTIONS: {{ vulnerabilities|length }}</span> 
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span class="badge badge-high">High: {{ high_count }}</span>
                &nbsp;&nbsp;
                <span class="badge badge-med">Medium: {{ medium_count }}</span>
                &nbsp;&nbsp;
                <span class="badge badge-low">Low: {{ low_count }}</span>
            </div>

            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="width: 5%;">Sr.</th>
                            <th style="width: 14%;">Date & Time</th>
                            <th style="width: 12%;">Severity</th>
                            <th style="width: 29%;">Location</th>
                            <th style="width: 40%;">Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for vuln in vulnerabilities %}
                        <tr>
                            <td class="sr-text">{{ loop.index }}</td>
                            <td class="date-text">
                                {% if vuln.created_at is string %}
                                    {{ vuln.created_at.replace('T', ' ')[:10] }}
                                    <span class="time-text">{{ vuln.created_at.replace('T', ' ')[11:19] }}</span>
                                {% else %}
                                    {{ vuln.created_at.strftime('%Y-%m-%d') }}
                                    <span class="time-text">{{ vuln.created_at.strftime('%H:%M:%S') }}</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if vuln.severity|lower == 'high' %}
                                    <span class="badge badge-high">{{ vuln.severity }}</span>
                                {% elif vuln.severity|lower == 'medium' %}
                                    <span class="badge badge-med">{{ vuln.severity }}</span>
                                {% else %}
                                    <span class="badge badge-low">{{ vuln.severity }}</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="location-text">{{ vuln.file_path }}</div>
                                <span class="line-number">Line {{ vuln.line_number }}</span>
                            </td>
                            <td class="desc-text">{{ vuln.description }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% endif %}
    </body>
    </html>
    """

    # --- Render HTML and Convert to PDF ---
    template = Template(html_template)
    rendered_html = template.render(
        repo_name=repo_name,
        start_str=start_str,
        end_str=end_str,
        generated_on=generated_on,
        vulnerabilities=vulnerabilities,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        year=datetime.now(timezone.utc).year
    )

    buffer = io.BytesIO()
    HTML(string=rendered_html).write_pdf(buffer)
    buffer.seek(0)
    return buffer





# import io
# import logging
# from datetime import datetime, timezone
# from jinja2 import Template

# logger = logging.getLogger(__name__)

# try:
#     from weasyprint import HTML
#     WEASYPRINT_AVAILABLE = True
# except Exception as e:
#     logger.warning(f"WeasyPrint could not be loaded (likely missing system dependencies): {e}")
#     WEASYPRINT_AVAILABLE = False
#     # Fallback to reportlab-based generator if available
#     try:
#         from app.utils.pdf_generator import generate_soc2_audit_report as generate_reportlab_pdf
#     except ImportError:
#         generate_reportlab_pdf = None

# def generate_soc2_audit_report(repo_name: str, vulnerabilities: list, start_date, end_date) -> io.BytesIO:
#     """
#     Generates a sleek, professional PDF audit report by rendering an HTML template 
#     and converting it via WeasyPrint into an in-memory buffer.
#     Falls back to ReportLab if WeasyPrint is not available.
#     """
#     if not WEASYPRINT_AVAILABLE:
#         if generate_reportlab_pdf:
#             logger.info("Falling back to ReportLab for PDF generation.")
#             return generate_reportlab_pdf(repo_name, vulnerabilities, start_date, end_date)
#         else:
#             raise ImportError(
#                 "Neither WeasyPrint nor ReportLab are available for PDF generation. "
#                 "Please install dependencies."
#             )

#     # --- Safe Date Formatting ---
#     start_str = start_date[:10] if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d')
#     end_str = end_date[:10] if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d')
#     generated_on = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

#     # Calculate metrics
#     high_count = sum(1 for v in vulnerabilities if v.severity.lower() == "high")
#     medium_count = sum(1 for v in vulnerabilities if v.severity.lower() == "medium")
#     low_count = sum(1 for v in vulnerabilities if v.severity.lower() == "low")

#     # --- HTML & CSS Template ---
#     html_template = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <style>
#             /* --- Page Setup & Borders --- */
#             @page {
#                 size: letter;
#                 margin: 0.5in 0.5in 0.75in 0.5in; /* Reduced margins */
                
#                 /* Sleek page borders */
#                 border-top: 8px solid #2563eb;
                
#                 /* Rich Footer Configuration */
#                 @bottom-left {
#                     content: "© " counter(year) " Trace AI. All rights reserved.";
#                     font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
#                     font-size: 8pt;
#                     color: #94a3b8;
#                     letter-spacing: 0.5px;
#                 }
#                 @bottom-center {
#                     content: "TraceAI.com";
#                     font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
#                     font-size: 8.5pt;
#                     font-weight: 600;
#                     color: #2563eb;
#                     letter-spacing: 0.5px;
#                 }
#                 @bottom-right {
#                     content: "Page " counter(page) " of " counter(pages);
#                     font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
#                     font-size: 8pt;
#                     font-weight: 500;
#                     color: #64748b;
#                 }
#             }

#             body {
#                 font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
#                 color: #334155;
#                 line-height: 1.65;
#                 font-size: 10pt;
#                 margin: 0;
#                 padding: 0;
#                 letter-spacing: 0.01em; /* Richer text spacing */
#             }

#             /* --- Header Layout --- */
#             .header-table {
#                 width: 100%;
#                 border-bottom: 2px solid #e2e8f0;
#                 padding-bottom: 12px;
#                 margin-bottom: 20px;
#             }
#             .logo-cell {
#                 width: 40%;
#                 vertical-align: middle;
#             }
#             /* REPLACE THE SRC ATTRIBUTE WITH YOUR ACTUAL LOGO URL OR BASE64 STRING */
#             .logo-img {
#                 max-height: 35px;
#                 display: block;
#             }
#             .title-cell {
#                 width: 60%;
#                 text-align: right;
#                 vertical-align: middle;
#             }
#             h1 {
#                 margin: 0 0 4px 0;
#                 font-size: 20pt;
#                 font-weight: 800;
#                 color: #0f172a;
#                 letter-spacing: -0.5px;
#             }
#             .subtitle {
#                 margin: 0;
#                 color: #64748b;
#                 font-size: 10.5pt;
#                 font-weight: 500;
#                 text-transform: uppercase;
#                 letter-spacing: 1.2px;
#             }
            
#             /* --- Spacers --- */
#             hr.spacer {
#                 border: none;
#                 border-top: 1px dashed #cbd5e1;
#                 margin: 25px 0;
#             }

#             /* --- Metadata Box (Card Style) --- */
#             .meta-box {
#                 background-color: #f8fafc;
#                 border: 1px solid #e2e8f0;
#                 border-left: 4px solid #2563eb;
#                 border-radius: 6px;
#                 padding: 14px 20px;
#                 margin-bottom: 20px;
#             }
#             .meta-table { 
#                 width: 100%; 
#                 border-collapse: collapse; 
#             }
#             .meta-table td { 
#                 padding: 4px 0; 
#                 font-size: 10.5pt;
#             }
#             .meta-label { 
#                 font-weight: 700; 
#                 width: 150px; 
#                 color: #475569; 
#                 letter-spacing: 0.5px;
#             }
#             .meta-value {
#                 color: #0f172a;
#                 font-weight: 500;
#             }
            
#             /* --- Summary Section --- */
#             .summary-box {
#                 font-size: 11pt;
#                 display: flex;
#                 align-items: center;
#                 margin-bottom: 10px;
#             }
#             .status-clear {
#                 color: #065f46;
#                 font-weight: 600;
#                 background-color: #d1fae5;
#                 border: 1px solid #34d399;
#                 padding: 12px 18px;
#                 border-radius: 6px;
#                 display: block;
#             }
#             .metric { 
#                 font-weight: 800; 
#                 color: #0f172a;
#                 font-size: 11.5pt;
#             }
            
#             /* --- Badges --- */
#             .badge {
#                 padding: 5px 12px;
#                 border-radius: 9999px;
#                 font-size: 7.5pt;
#                 font-weight: 800;
#                 text-transform: uppercase;
#                 letter-spacing: 0.8px;
#                 display: inline-block;
#             }
#             .badge-high { 
#                 background-color: #fef2f2; 
#                 color: #b91c1c; 
#                 border: 1px solid #fecaca;
#             }
#             .badge-med { 
#                 background-color: #fffbeb; 
#                 color: #b45309; 
#                 border: 1px solid #fde68a;
#             }
#             .badge-low { 
#                 background-color: #f0fdf4; 
#                 color: #15803d; 
#                 border: 1px solid #bbf7d0;
#             }
            
#             /* --- Data Table --- */
#             .table-container {
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 overflow: hidden; /* Helps clip inner borders to rounded edges */
#             }
#             .data-table {
#                 width: 100%;
#                 border-collapse: separate;
#                 border-spacing: 0;
#             }
            
#             /* Prevent rows from breaking across pages */
#             .data-table tr {
#                 page-break-inside: avoid;
#                 break-inside: avoid;
#             }
            
#             .data-table th, .data-table td {
#                 text-align: left;
#                 padding: 14px 16px;
#                 border-bottom: 1px solid #e2e8f0;
#                 vertical-align: top;
#             }
#             .data-table th {
#                 background-color: #f8fafc;
#                 color: #334155;
#                 font-size: 8.5pt;
#                 font-weight: 700;
#                 text-transform: uppercase;
#                 letter-spacing: 1px;
#                 border-bottom: 2px solid #cbd5e1;
#             }
#             .data-table tr:last-child td {
#                 border-bottom: none;
#             }
#             .data-table tbody tr:nth-child(even) { 
#                 background-color: #fafafa; 
#             }
            
#             .location-text { 
#                 color: #0f172a; 
#                 font-weight: 700; 
#                 font-family: 'Consolas', 'Courier New', Courier, monospace;
#                 font-size: 9.5pt;
#                 word-break: break-all;
#             }
#             .line-number { 
#                 color: #64748b; 
#                 font-size: 9pt; 
#                 display: block; 
#                 margin-top: 4px;
#                 font-weight: 500;
#             }
#             .date-text { 
#                 color: #475569; 
#                 white-space: nowrap; 
#                 font-weight: 600;
#             }
#             .sr-text {
#                 color: #64748b;
#                 font-weight: 700;
#             }
#             .desc-text {
#                 color: #1e293b;
#             }
#         </style>
#     </head>
#     <body>
#         <table class="header-table">
#             <tr>
#                 <td class="logo-cell">
#                     <img class="logo-img" src="https://via.placeholder.com/200x50/2563eb/ffffff?text=Trace+AI+Logo" alt="Trace AI">
#                 </td>
#                 <td class="title-cell">
#                     <h1>SOC2 Security Audit Log</h1>
#                     <p class="subtitle">Automated Intervention Report</p>
#                 </td>
#             </tr>
#         </table>

#         <div class="meta-box">
#             <table class="meta-table">
#                 <tr><td class="meta-label">REPOSITORY:</td><td class="meta-value">{{ repo_name }}</td></tr>
#                 <tr><td class="meta-label">AUDIT PERIOD:</td><td class="meta-value">{{ start_str }} &nbsp;&mdash;&nbsp; {{ end_str }}</td></tr>
#                 <tr><td class="meta-label">GENERATED ON:</td><td class="meta-value">{{ generated_on }} UTC</td></tr>
#             </table>
#         </div>

#         <hr class="spacer">

#         {% if vulnerabilities|length == 0 %}
#             <div class="status-clear">
#                 ✓ Status: Clear. No security violations detected during this period.
#             </div>
#         {% else %}
#             <div class="summary-box">
#                 <span class="metric">TOTAL INTERVENTIONS: {{ vulnerabilities|length }}</span> 
#                 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
#                 <span class="badge badge-high">High: {{ high_count }}</span>
#                 &nbsp;&nbsp;
#                 <span class="badge badge-med">Medium: {{ medium_count }}</span>
#                 &nbsp;&nbsp;
#                 <span class="badge badge-low">Low: {{ low_count }}</span>
#             </div>

#             <div class="table-container">
#                 <table class="data-table">
#                     <thead>
#                         <tr>
#                             <th style="width: 5%;">Sr.</th>
#                             <th style="width: 12%;">Date</th>
#                             <th style="width: 12%;">Severity</th>
#                             <th style="width: 30%;">Location</th>
#                             <th style="width: 41%;">Description</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         {% for vuln in vulnerabilities %}
#                         <tr>
#                             <td class="sr-text">{{ loop.index }}</td>
#                             <td class="date-text">
#                                 {{ vuln.created_at[:10] if vuln.created_at is string else vuln.created_at.strftime('%Y-%m-%d') }}
#                             </td>
#                             <td>
#                                 {% if vuln.severity|lower == 'high' %}
#                                     <span class="badge badge-high">{{ vuln.severity }}</span>
#                                 {% elif vuln.severity|lower == 'medium' %}
#                                     <span class="badge badge-med">{{ vuln.severity }}</span>
#                                 {% else %}
#                                     <span class="badge badge-low">{{ vuln.severity }}</span>
#                                 {% endif %}
#                             </td>
#                             <td>
#                                 <div class="location-text">{{ vuln.file_path }}</div>
#                                 <span class="line-number">Line {{ vuln.line_number }}</span>
#                             </td>
#                             <td class="desc-text">{{ vuln.description }}</td>
#                         </tr>
#                         {% endfor %}
#                     </tbody>
#                 </table>
#             </div>
#         {% endif %}
#     </body>
#     </html>
#     """

#     # --- Render HTML and Convert to PDF ---
#     template = Template(html_template)
#     rendered_html = template.render(
#         repo_name=repo_name,
#         start_str=start_str,
#         end_str=end_str,
#         generated_on=generated_on,
#         vulnerabilities=vulnerabilities,
#         high_count=high_count,
#         medium_count=medium_count,
#         low_count=low_count,
#         year=datetime.now(timezone.utc).year
#     )

#     buffer = io.BytesIO()
#     HTML(string=rendered_html).write_pdf(buffer)
#     buffer.seek(0)
#     return buffer