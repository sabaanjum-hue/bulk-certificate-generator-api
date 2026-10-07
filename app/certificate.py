from datetime import date
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

def generate_certificate(output_dir: Path, certificate_id: str, recipient_name: str,
                         course: str, event_name: str, issue_date: date) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{certificate_id}.pdf"

    width, height = landscape(A4)
    pdf = canvas.Canvas(str(output_path), pagesize=(width, height))

    # Single predefined certificate template.
    pdf.setStrokeColor(colors.HexColor("#1F4E79"))
    pdf.setLineWidth(3)
    pdf.rect(35, 35, width - 70, height - 70)

    pdf.setFillColor(colors.HexColor("#1F4E79"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 105, "CERTIFICATE OF PARTICIPATION")

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 145, "This certificate is proudly presented to")

    pdf.setFillColor(colors.HexColor("#17365D"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(width / 2, height - 205, recipient_name)

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 245, f"for successfully participating in {course}")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 280, event_name)

    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, 75, f"Issue date: {issue_date.isoformat()}")
    pdf.drawRightString(width - 70, 75, f"Certificate ID: {certificate_id}")

    pdf.save()
    return output_path
