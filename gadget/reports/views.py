from django.shortcuts import render

from reports.models import SalesReport


def reports_home(request):
    reports = SalesReport.objects.order_by('-report_date')[:10]
    return render(request, 'reports/reports_home.html', {'reports': reports})
