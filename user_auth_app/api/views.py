from rest_framework import generics
from .serializers import CustomUserSerializer, UserRegisterSerializer
from ..models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import EmailAuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
import uuid
from join_app.models import Contact

class CustomerUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.filter(is_guest=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

class CustomerUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CurrentUser(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class RegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
        else:
            print("Registration errors:", serializer.errors)
            data = serializer.errors
        return Response(data)

class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Request received with data:", request.data) 
        serializer = EmailAuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            print("User authenticated:", user)


            if not user.is_active:
                return Response({"error": "User account is inactive."}, status=status.HTTP_403_FORBIDDEN)

            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            data = {
                'token': token.key,
                'email': user.email,
            }
            return Response(data, status=status.HTTP_200_OK)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=400)
    

class GuestLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        guest_username = f"guest_{uuid.uuid4().hex[:3]}"
        guest_email = f"{guest_username}@guest.com"

        guest_user = CustomUser.objects.create_user(
            username=guest_username,
            email=guest_email,
            password=None,
            is_guest=True,
            emblem="G",
            color="#cccccc"
        )
        guest_user.save()

        Contact.objects.create(
            user=guest_user,
            name=guest_username,
            email=guest_email,
            emblem=guest_user.emblem,
            color=guest_user.color,
            phone=""
        )

        token, _ = Token.objects.get_or_create(user=guest_user)

        return Response({
            "token": token.key,
            "email": guest_user.email,
            "username": guest_user.username,
            "emblem": guest_user.emblem,
            "color": guest_user.color
        }, status=status.HTTP_201_CREATED)

class GuestLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if hasattr(user, 'is_guest') and user.is_guest:
            user.delete()
            return Response({"message": "Gastbenutzer und Daten erfolgreich gelöscht."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Kein Gastbenutzer erkannt oder nicht authentifiziert."}, status=status.HTTP_400_BAD_REQUEST)