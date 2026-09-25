from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from invoices.models import Invoice


def invoice_list(request):
    invoices = Invoice.objects.select_related('order').order_by('-issued_at')
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice.objects.select_related('order'), pk=invoice_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph('GadgetGalaxy Invoice', styles['Title']),
        Spacer(1, 0.2 * inch),
        Paragraph(f'Invoice No: {invoice.invoice_number}', styles['Heading2']),
        Spacer(1, 0.2 * inch),
    ]

    order_details = [
        ['Order #', str(invoice.order.id)],
        ['Customer', invoice.order.customer_name],
        ['Email', invoice.order.customer_email or 'N/A'],
        ['Issued', invoice.issued_at.strftime('%Y-%m-%d %H:%M')],
        ['Status', invoice.get_status_display()],
        ['Total', f'${invoice.total_amount:.2f}'],
    ]
    order_table = Table(order_details, colWidths=[1.8 * inch, 4.4 * inch])
    order_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.6, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ])
    )
    story.append(order_table)
    story.append(Spacer(1, 0.3 * inch))

    items = [['Product', 'Qty', 'Unit Price', 'Total']]
    for item in invoice.order.items.select_related('product'):
        items.append([
            item.product.name,
            str(item.quantity),
            f'${item.unit_price:.2f}',
            f'${item.total_price:.2f}',
        ])
    items.append(['', '', 'Total', f'${invoice.total_amount:.2f}'])

    item_table = Table(items, colWidths=[3.0 * inch, 0.8 * inch, 1.5 * inch, 1.2 * inch])
    item_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.6, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ])
    )
    story.append(item_table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
    return response
