from rest_framework import serializers
from .models import PaymentMethodSettings

class PaymentMethodSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodSettings
        fields = ['stripe_enabled', 'paypal_enabled', 'updated_at']