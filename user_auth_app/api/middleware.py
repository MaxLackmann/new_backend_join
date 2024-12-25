from django.utils.timezone import now
from datetime import timedelta
from user_auth_app.models import CustomUser
from rest_framework.authtoken.models import Token

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        current_time = now()
        
        # **1. Aktualisiere Aktivitätszeit für eingeloggte Benutzer**
        if request.user.is_authenticated:
            if request.user.last_activity:
                inactivity_duration = (current_time - request.user.last_activity).total_seconds() / 60
                if inactivity_duration > 0.1:
                    request.user.last_activity = current_time
                    request.user.save(update_fields=['last_activity'])
            else:
                # Initiale Aktivität setzen, falls sie noch nicht gesetzt wurde
                request.user.last_activity = current_time
                request.user.save(update_fields=['last_activity'])
        
        # **2. Schutz für neue Gäste (Grace Period: 1 Minuten)**
        grace_period_time = now() - timedelta(minutes=1)
        guest_threshold_time = now() - timedelta(minutes=1)
        
        inactive_guests = CustomUser.objects.filter(
            is_guest=True,
            last_activity__lt=guest_threshold_time,
            date_joined__lt=grace_period_time  # Gäste, die älter als 1 Minuten sind
        )
        
        if inactive_guests.exists():
            print(f"[Middleware] Lösche {inactive_guests.count()} inaktive Gäste...")
            for guest in inactive_guests:
                try:
                    print(f"[Middleware] Lösche Gast-Benutzer: {guest.email}")
                    guest.delete()
                except Exception as e:
                    print(f"[Middleware] Fehler beim Löschen von Gast-Benutzer {guest.email}: {e}")
            print("[Middleware] Inaktive Gäste erfolgreich gelöscht.")
        
        # 🔑 **3. Lösche Token für inaktive Benutzer**
        user_threshold_time = now() - timedelta(minutes=1)
        inactive_users = CustomUser.objects.filter(
            is_guest=False,
            last_activity__lt=user_threshold_time
        )
        
        for user in inactive_users:
            token = Token.objects.filter(user=user).first()
            if token:
                print(f"[Middleware] Lösche Token für inaktiven Benutzer: {user.email}")
                token.delete()
                print(f"[Middleware] Token erfolgreich gelöscht für Benutzer: {user.email}")
        
        return response