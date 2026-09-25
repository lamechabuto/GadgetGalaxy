import base64
from decimal import Decimal

import requests
from django.conf import settings
from django.utils import timezone


class MpesaSTKService:
    def __init__(self, shortcode=None, passkey=None, consumer_key=None, consumer_secret=None, environment=None):
        self.shortcode = shortcode or getattr(settings, 'MPESA_SHORTCODE', '')
        self.passkey = passkey or getattr(settings, 'MPESA_PASSKEY', '')
        self.consumer_key = consumer_key or getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = consumer_secret or getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.environment = (environment or getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')).lower()
        self.base_url = 'https://sandbox.safaricom.co.ke' if self.environment == 'sandbox' else 'https://api.safaricom.co.ke'

    def build_password(self, timestamp):
        raw = f'{self.shortcode}{self.passkey}{timestamp}'.encode('utf-8')
        return base64.b64encode(raw).decode('utf-8')

    @staticmethod
    def normalize_phone_number(phone_number):
        digits = ''.join(ch for ch in str(phone_number) if ch.isdigit())
        if len(digits) == 9 and digits.startswith('7'):
            return f'254{digits}'
        if len(digits) == 12 and digits.startswith('254'):
            return digits
        if len(digits) == 10 and digits.startswith('0'):
            return f'254{digits[1:]}'
        return digits

    def _get_access_token(self):
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError('M-Pesa credentials are not configured.')

        credentials = base64.b64encode(
            f'{self.consumer_key}:{self.consumer_secret}'.encode('utf-8')
        ).decode('utf-8')
        response = requests.get(
            f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials',
            headers={'Authorization': f'Basic {credentials}'},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get('access_token')
        if not token:
            raise ValueError('M-Pesa access token could not be generated.')
        return token

    def initiate_stk_push(self, order, phone_number):
        if not self.shortcode or not self.passkey:
            return self._create_pending_local_transaction(order, phone_number, 'Test mode: missing M-Pesa credentials.')

        if not order or not getattr(order, 'total_amount', None):
            raise ValueError('Order total is missing for M-Pesa STK request.')

        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        amount = int(Decimal(str(order.total_amount)).quantize(Decimal('1')))
        msisdn = self.normalize_phone_number(phone_number)
        payload = {
            'BusinessShortCode': str(self.shortcode),
            'Password': self.build_password(timestamp),
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': msisdn,
            'PartyB': str(self.shortcode),
            'PhoneNumber': msisdn,
            'CallBackURL': getattr(settings, 'MPESA_CALLBACK_URL', ''),
            'AccountReference': f'Order-{order.pk}',
            'TransactionDesc': f'Payment for order #{order.pk}',
            'Remark': 'GadgetGalaxy purchase',
        }

        access_token = self._get_access_token()
        response = requests.post(
            f'{self.base_url}/mpesa/stkpush/v1/processrequest',
            json=payload,
            headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
            timeout=30,
        )
        try:
            response_data = response.json()
        except ValueError:
            response_data = {}

        if response.status_code != 200 or response_data.get('ResponseCode') not in (None, '0'):
            raise ValueError(response_data.get('ResponseDescription') or 'M-Pesa request failed.')

        return self._persist_transaction(order, amount, msisdn, response_data)

    def _persist_transaction(self, order, amount, msisdn, response_data):
        from .models import MpesaTransaction

        transaction, _ = MpesaTransaction.objects.get_or_create(order=order)
        transaction.amount = amount
        transaction.phone_number = msisdn
        transaction.merchant_request_id = response_data.get('MerchantRequestID', '')
        transaction.checkout_request_id = response_data.get('CheckoutRequestID', '')
        transaction.response_code = str(response_data.get('ResponseCode', ''))
        transaction.response_description = response_data.get('ResponseDescription', '')
        transaction.status = 'pending' if response_data.get('ResponseCode', '0') == '0' else 'failed'
        transaction.save()
        return response_data

    def _create_pending_local_transaction(self, order, phone_number, message):
        if not order or not getattr(order, 'total_amount', None):
            raise ValueError('Order total is missing for M-Pesa STK request.')

        from .models import MpesaTransaction

        amount = int(Decimal(str(order.total_amount)).quantize(Decimal('1')))
        msisdn = self.normalize_phone_number(phone_number)
        transaction, _ = MpesaTransaction.objects.get_or_create(order=order)
        transaction.amount = amount
        transaction.phone_number = msisdn
        transaction.response_code = '0'
        transaction.response_description = message
        transaction.status = 'pending'
        transaction.save()
        return {
            'ResponseCode': '0',
            'ResponseDescription': message,
            'MerchantRequestID': f'mock-{order.pk}',
            'CheckoutRequestID': f'ws_CO_Stub_{order.pk}',
        }
