import json

from django.http import HttpResponse, JsonResponse

from .models import MpesaTransaction


def mpesa_callback(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    payload = json.loads(request.body or '{}')
    result = payload.get('Body', {}).get('stkCallback', {})
    checkout_request_id = result.get('CheckoutRequestID', '')
    merchant_request_id = result.get('MerchantRequestID', '')
    result_code = result.get('ResultCode', '')
    result_desc = result.get('ResultDesc', '')

    transaction = MpesaTransaction.objects.filter(checkout_request_id=checkout_request_id).first()
    if transaction:
        transaction.callback_payload = payload
        transaction.response_code = str(result_code)
        transaction.response_description = result_desc
        if result_code == '0':
            transaction.status = 'completed'
            transaction.order.status = 'paid'
            transaction.order.save(update_fields=['status', 'updated_at'])
        else:
            transaction.status = 'failed'
        transaction.save(update_fields=['callback_payload', 'response_code', 'response_description', 'status', 'updated_at'])

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


def mpesa_timeout(request):
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Timeout accepted'})
