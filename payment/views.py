from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
import logging
import stripe
import paypalrestsdk
from .models import PaymentMethodSettings
from .serializers import PaymentMethodSettingsSerializer
from rest_framework.views import APIView  # <-- FIX: Import APIView


# Import the send_simple_thank_you_email utility function
from .utils import send_simple_thank_you_email  # Make sure this exists, or define it below


# Configure logging
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY

# PayPal configuration
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@api_view(['POST'])
def create_checkout_session(request):
    """POST /api/payment/create-checkout-session/"""
    try:
        # Check if Stripe is enabled
        payment_settings = PaymentMethodSettings.load()
        if not payment_settings.stripe_enabled:
            return Response(
                {'error': 'Stripe payments are currently disabled'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        items = request.data.get('items', [])
        
        if not items:
            return Response(
                {'error': 'Items are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stripe_line_items = []

        for item in items:
            # Validate required fields
            if not all(key in item for key in ['name', 'unit_amount', 'quantity']):
                return Response(
                    {'error': 'Each item must have name, unit_amount, and quantity'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stripe_line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(item['unit_amount']),  # in cents
                },
                'quantity': int(item['quantity']),
            })


        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=stripe_line_items,
            success_url= f"{settings.FRONTEND_BASE_URL}/success",
            cancel_url=f"{settings.FRONTEND_BASE_URL}/cancel",
        )
        
        return Response({
            'id': session.id,
            'url': session.url
        }, status=status.HTTP_201_CREATED)
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return Response(
            {'error': 'Payment processing error'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except ValueError as e:
        logger.error(f"Value error in checkout session: {str(e)}")
        return Response(
            {'error': 'Invalid data provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_checkout_session: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_paypal_payment(request):
    """POST /api/payment/paypal/create-payment/"""
    try:
        # Check if PayPal is enabled
        payment_settings = PaymentMethodSettings.load()
        if not payment_settings.paypal_enabled:
            return Response(
                {'error': 'PayPal payments are currently disabled'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')
        return_url = request.data.get('return_url', f'{settings.FRONTEND_BASE_URL}/payment/success')
        cancel_url = request.data.get('return_url', f'{settings.FRONTEND_BASE_URL}/payment/cancel')

        # Validate amount
        if not amount:
            return Response(
                {'error': 'Amount is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return Response(
                    {'error': 'Amount must be greater than 0'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate currency
        if currency not in ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']:
            return Response(
                {'error': 'Unsupported currency'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Book Order",
                        "sku": "book-001",
                        "price": f"{amount_float:.2f}",
                        "currency": currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{amount_float:.2f}",
                    "currency": currency
                },
                "description": "Book purchase transaction"
            }]
        })

        if payment.create():
            approval_url = next(
                (link.href for link in payment.links if link.rel == "approval_url"), 
                None
            )
            
            if not approval_url:
                logger.error("No approval URL found in PayPal response")
                return Response(
                    {'error': 'PayPal approval URL not found'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                'payment_id': payment.id,
                'approval_url': approval_url,
                'status': 'created'
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"PayPal payment creation failed: {payment.error}")
            return Response(
                {'error': 'Failed to create PayPal payment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    except paypalrestsdk.exceptions.ConnectionError as e:
        logger.error(f"PayPal connection error: {str(e)}")
        return Response(
            {'error': 'PayPal service unavailable'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"PayPal payment creation error: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_paypal_payment(request):
    """POST /api/payment/paypal/execute-payment/"""
    try:
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')

        if not payment_id or not payer_id:
            return Response(
                {'error': 'Payment ID and Payer ID are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = paypalrestsdk.Payment.find(payment_id)
        
        if not payment:
            return Response(
                {'error': 'Payment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if payment.execute({"payer_id": payer_id}):
            return Response({
                'payment_id': payment.id,
                'status': 'completed',
                'payer_info': payment.payer.payer_info,
                'transaction_id': payment.transactions[0].related_resources[0].sale.id
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"PayPal payment execution failed: {payment.error}")
            return Response(
                {'error': 'Failed to execute PayPal payment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    except paypalrestsdk.exceptions.ResourceNotFound:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except paypalrestsdk.exceptions.ConnectionError as e:
        logger.error(f"PayPal connection error: {str(e)}")
        return Response(
            {'error': 'PayPal service unavailable'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"PayPal payment execution error: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_paypal_payment_details(request, payment_id):
    """GET /api/payment/paypal/payment-details/<payment_id>/"""
    try:
        if not payment_id:
            return Response(
                {'error': 'Payment ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if not payment:
            return Response(
                {'error': 'Payment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'payment_id': payment.id,
            'state': payment.state,
            'intent': payment.intent,
            'payer': payment.payer,
            'transactions': payment.transactions,
            'create_time': payment.create_time,
            'update_time': payment.update_time
        }, status=status.HTTP_200_OK)

    except paypalrestsdk.exceptions.ResourceNotFound:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except paypalrestsdk.exceptions.ConnectionError as e:
        logger.error(f"PayPal connection error: {str(e)}")
        return Response(
            {'error': 'PayPal service unavailable'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"PayPal payment details error: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def admin_payment_settings(request):
    """GET/PUT /api/admin/payment-settings/"""
    settings = PaymentMethodSettings.load()
    
    if request.method == 'GET':
        serializer = PaymentMethodSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PaymentMethodSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def payment_methods_status(request):
    """GET /api/payment/methods-status/"""
    settings = PaymentMethodSettings.load()
    serializer = PaymentMethodSettingsSerializer(settings)
    return Response(serializer.data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_thank_you_email(request):
    """
    POST /api/payment/send-thank-you-email/
    Send a thank you email to the authenticated user without user name
    """
    try:
        user = request.user
        
        # Call email function without passing user name
        success = send_simple_thank_you_email(user_email=user.email)

        if success:
            return Response(
                {'message': 'Thank you email sent successfully'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to send thank you email'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        logger.error(f"Error sending thank you email: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = int(request.data.get('amount', 0))
            currency = request.data.get('currency', 'usd')
            if amount <= 0:
                return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={'user_id': request.user.id}
            )
            return Response({'clientSecret': intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)