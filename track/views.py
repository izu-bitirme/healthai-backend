from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DailyRecoveryLog
from .serializers import DailyRecoveryLogSerializer

class DailyRecoveryLogListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        logs = DailyRecoveryLog.objects.filter(
            recovery_cycle__patient__profile__user=request.user
        ).order_by('-date')
        
        serializer = DailyRecoveryLogSerializer(logs, many=True)
        return Response(serializer.data)


class DailyRecoveryLogDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        log = DailyRecoveryLog.objects.filter(
            recovery_cycle__patient__profile__user=request.user,
            pk=pk
        ).first()
        
        if not log:
            return Response({'error': 'Kayıt bulunamadı'}, status=404)
            
        serializer = DailyRecoveryLogSerializer(log)
        return Response(serializer.data)