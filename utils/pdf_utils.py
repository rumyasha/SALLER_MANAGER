from weasyprint import HTML
from io import BytesIO
from django.template.loader import render_to_string

def generate_pdf(template_name, context):
    html_string = render_to_string(template_name, context)
    html = HTML(string=html_string)
    pdf_bytes = html.write_pdf()
    return BytesIO(pdf_bytes)