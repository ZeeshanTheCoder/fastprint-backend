from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['email', 'username', 'id']  # For exact filtering via ?email=...
    search_fields = ['email', 'username', 'first_name', 'last_name']  # For partial matching via ?search=...
    authentication_classes = []  # Remove authentication requirement
    permission_classes = []      # Remove permission requirement
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Handle search parameter specifically for email lookup
        search_param = self.request.query_params.get('search', None)
        if search_param:
            # First try exact email match, then fallback to general search
            exact_match = queryset.filter(email=search_param)
            if exact_match.exists():
                return exact_match
        return queryset

class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = []  # Remove authentication requirement
    permission_classes = []      # Remove permission requirement


@api_view(['POST'])
@permission_classes([AllowAny])
def save_account_settings(request):
    try:
        email = request.data.get('email')
        username = request.data.get('username')
        
        profile = None
        if email:
            profile = UserProfile.objects.filter(email=email).first()
        elif username:
            profile = UserProfile.objects.filter(username=username).first()
        
        if profile:
            # Update existing profile
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            # Create new profile
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            saved_profile = serializer.save()
            return Response({
                'success': True,
                'message': 'Account settings saved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_account(request, profile_id):
    try:
        profile = UserProfile.objects.get(id=profile_id)
        profile.delete()
        return Response({
            'success': True,
            'message': 'Account deleted successfully'
        }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)