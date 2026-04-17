import io
from datetime import datetime, timezone
from jinja2 import Template
from weasyprint import HTML

def generate_soc2_audit_report(repo_name: str, vulnerabilities: list, start_date, end_date) -> io.BytesIO:
    """
    Generates a sleek, professional PDF audit report by rendering an HTML template 
    and converting it via WeasyPrint into an in-memory buffer.
    """
    # --- Safe Date Formatting ---
    start_str = start_date[:10] if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d')
    end_str = end_date[:10] if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d')
    generated_on = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Calculate metrics
    high_count = sum(1 for v in vulnerabilities if v.severity.lower() == "high")
    other_count = len(vulnerabilities) - high_count

    # --- HTML & CSS Template ---
    # Using modern fonts, pill badges, and clean horizontal-only table borders.
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {
                size: letter;
                margin: 1in;
                @bottom-right {
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    color: #94a3b8;
                }
            }
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1e293b;
                line-height: 1.5;
                font-size: 10pt;
            }
            .header {
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0 0 5px 0;
                font-size: 22pt;
                color: #0f172a;
            }
            .subtitle {
                margin: 0;
                color: #64748b;
                font-size: 12pt;
                font-weight: 400;
            }
            
            /* Metadata Box */
            .meta-box {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 25px;
            }
            .meta-table { width: 100%; border-collapse: collapse; }
            .meta-table td { padding: 4px 0; }
            .meta-label { font-weight: 600; width: 120px; color: #475569; }
            
            /* Summary Section */
            .summary-box {
                margin-bottom: 20px;
                font-size: 11pt;
            }
            .status-clear {
                color: #15803d;
                font-weight: 600;
                background-color: #dcfce7;
                padding: 10px 15px;
                border-radius: 6px;
                display: inline-block;
            }
            .metric { font-weight: bold; }
            
            /* Badges */
            .badge {
                padding: 4px 10px;
                border-radius: 9999px; /* Pill shape */
                font-size: 8.5pt;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .badge-high { background-color: #fee2e2; color: #b91c1c; }
            .badge-med { background-color: #ffedd5; color: #c2410c; }
            
            /* Data Table */
            .data-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            .data-table th, .data-table td {
                text-align: left;
                padding: 12px 10px;
                border-bottom: 1px solid #e2e8f0;
                vertical-align: top;
            }
            .data-table th {
                color: #64748b;
                font-size: 9pt;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            /* Zebra striping for readability */
            .data-table tbody tr:nth-child(even) { background-color: #fcfcfd; }
            
            .location-text { color: #0f172a; font-weight: 500; }
            .line-number { color: #94a3b8; font-size: 9pt; display: block; margin-top: 2px;}
            .date-text { color: #475569; white-space: nowrap; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Trace AI <span style="font-weight:300;">| SOC2 Security Audit Log</span></h1>
            <p class="subtitle">Automated Vulnerability Intervention Report</p>
        </div>

        <div class="meta-box">
            <table class="meta-table">
                <tr><td class="meta-label">Repository:</td><td>{{ repo_name }}</td></tr>
                <tr><td class="meta-label">Audit Period:</td><td>{{ start_str }} to {{ end_str }}</td></tr>
                <tr><td class="meta-label">Generated On:</td><td>{{ generated_on }} UTC</td></tr>
            </table>
        </div>

        {% if vulnerabilities|length == 0 %}
            <div class="status-clear">
                ✓ Status: Clear. No security violations detected during this period.
            </div>
        {% else %}
            <div class="summary-box">
                <span class="metric">Total Interventions: {{ vulnerabilities|length }}</span> 
                &nbsp;&nbsp;&nbsp;
                <span class="badge badge-high">High: {{ high_count }}</span>
                &nbsp;
                <span class="badge badge-med">Medium/Low: {{ other_count }}</span>
            </div>

            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width: 12%;">Date</th>
                        <th style="width: 15%;">Severity</th>
                        <th style="width: 33%;">Location</th>
                        <th style="width: 40%;">Description</th>
                    </tr>
                </thead>
                <tbody>
                    {% for vuln in vulnerabilities %}
                    <tr>
                        <td class="date-text">
                            {{ vuln.created_at[:10] if vuln.created_at is string else vuln.created_at.strftime('%Y-%m-%d') }}
                        </td>
                        <td>
                            {% if vuln.severity|lower == 'high' %}
                                <span class="badge badge-high">{{ vuln.severity }}</span>
                            {% else %}
                                <span class="badge badge-med">{{ vuln.severity }}</span>
                            {% endif %}
                        </td>
                        <td>
                            <div class="location-text">{{ vuln.file_path }}</div>
                            <span class="line-number">Line {{ vuln.line_number }}</span>
                        </td>
                        <td>{{ vuln.description }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </body>
    </html>
    """

    # --- Render HTML and Convert to PDF ---
    # 1. Compile the Jinja2 template with our variables
    template = Template(html_template)
    rendered_html = template.render(
        repo_name=repo_name,
        start_str=start_str,
        end_str=end_str,
        generated_on=generated_on,
        vulnerabilities=vulnerabilities,
        high_count=high_count,
        other_count=other_count
    )

    # 2. Use WeasyPrint to convert the HTML string to a PDF
    buffer = io.BytesIO()
    HTML(string=rendered_html).write_pdf(buffer)
    
    # 3. Reset buffer position so FastAPI can stream it successfully
    buffer.seek(0)
    return buffer