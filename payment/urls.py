from django.urls import path
from .views import (
    create_checkout_session, 
    create_paypal_payment, 
    execute_paypal_payment, 
    get_paypal_payment_details,
    admin_payment_settings,
    payment_methods_status,
    send_thank_you_email,
    CreatePaymentIntentView
)

urlpatterns = [
    # Stripe endpoint
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),

    
    # PayPal endpoints
   path('paypal/create-payment/', create_paypal_payment, name='create_paypal_payment'),
    path('paypal/execute-payment/', execute_paypal_payment, name='execute_paypal_payment'),
    path('paypal/payment-details/<str:payment_id>/', get_paypal_payment_details, name='paypal_payment_details'),
    
    # Payment settings endpoints
    path('admin/payment-settings/', admin_payment_settings, name='admin_payment_settings'),
    path('methods-status/', payment_methods_status, name='payment_methods_status'),
    
    #payment email page
        path('send-thank-you-email/', send_thank_you_email, name='send_thank_you_email'),

]