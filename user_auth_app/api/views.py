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
from django.utils.timezone import now
from datetime import timedelta

class CustomerUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.filter(is_guest=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

class CustomerUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CurrentUser(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class RegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        print("Request received with data:", request.data)
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

            # 🟢 Aktualisiere die letzte Aktivität beim Login
            user.last_activity = now()
            user.save(update_fields=['last_activity'])
            print(f"Last activity updated for user: {user.email}")

            # Lösche bestehende Tokens und erstelle einen neuen Token
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
        # Lösche inaktive Gäste vor der Erstellung eines neuen Gastes
        guest_threshold_time = now() - timedelta(minutes=1)
        inactive_guests = CustomUser.objects.filter(
            is_guest=True,
            last_activity__lt=guest_threshold_time
        )
        if inactive_guests.exists():
            inactive_guests.delete()
            print("[GuestLoginView] Inaktive Gäste gelöscht.")

        # Erstelle einen neuen Gast
        guest_username = f"guest_{uuid.uuid4().hex[:3]}"
        guest_email = f"{guest_username}@guest.com"

        guest_user = CustomUser.objects.create_user(
            username=guest_username,
            email=guest_email,
            phone="123456789",
            password=None,
            is_guest=True,
            emblem="G",
            color="#cccccc"
        )
        guest_user.last_activity = now()  # Setze initiale Aktivität
        guest_user.save()

        token, _ = Token.objects.get_or_create(user=guest_user)

        return Response({
            "token": token.key,
            "email": guest_user.email,
            "phone": guest_user.phone,
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
        
class ActivityPingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_time = now()
        user.last_activity = current_time
        user.save(update_fields=['last_activity'])
        
        if user.is_guest:
            return Response({'message': 'Guest activity updated'}, status=200)
        
        return Response({'message': 'User activity updated'}, status=200)
    
class ValidateTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Validiert das Token direkt und überprüft die letzte Aktivität.
        """
        current_time = now()
        inactivity_duration = (current_time - request.user.last_activity).total_seconds() / 60

        if inactivity_duration > 1:  # Timeout von 1 Minute
            print(f"[ValidateTokenView] Token abgelaufen für Benutzer: {request.user.email}")
            return Response({"message": "Token expired"}, status=status.HTTP_401_UNAUTHORIZED)

        print(f"[ValidateTokenView] Token gültig für Benutzer: {request.user.email}")
        return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)