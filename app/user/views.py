from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .models import User


from user.serializers import UserSerializer, AuthTokenSerializer, MerchantStatusSerializer

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    render_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class SetMerchantStatusView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    serializer_class = MerchantStatusSerializer

    def post(self, request):
        serializer = MerchantStatusSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            status_bool = serializer.validated_data['status']

            try:
                user = User.objects.get(id=user_id)
                user.is_merchant = status_bool
                user.save()
                return Response({'status': 'success', 'message': 'Merchant status updated'})
            except User.DoesNotExist:
                return Response({'status': 'error', 'message': 'User not found'}, status=404)
        else:
            return Response(serializer.errors, status=400)