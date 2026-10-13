from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db import connections
from django.db.utils import OperationalError

class HealthCheckView(APIView):
    """
    Checks if the application is alive.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)

class ReadyCheckView(APIView):
    """
    Checks if the application is ready to handle requests (e.g., DB connection is up).
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        # Check Database
        db_conn = connections['default']
        try:
            db_conn.ensure_connection()
        except OperationalError:
            return Response({"status": "unready", "reason": "database_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({"status": "ready"}, status=status.HTTP_200_OK)
