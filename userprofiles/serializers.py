# accounts/serializers.py
from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'first_name',
            'last_name', 
            'username',
            'email',
            'password',
            'country',
            'city',
            'postal_code',
            'address',
            'account_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_email(self, value):
        """
        Optional email validation
        """
        if value and not '@' in value:
            raise serializers.ValidationError("Enter a valid email address.")
        return value
    
    def validate_account_type(self, value):
        """
        Validate account type
        """
        if value and value not in ['personal', 'business']:
            raise serializers.ValidationError("Account type must be 'personal' or 'business'.")
        return value