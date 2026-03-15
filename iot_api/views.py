from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, DeviceSerializer, SensorLogSerializer
from .permissions import IsDeviceAdminOrMemberReadOnly
from .models import Device, SensorLog
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from django.db.models.functions import TruncHour
from datetime import timedelta
from django.utils import timezone

class HourlyChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response({"detail": "device_id required"}, status=400)

        user_roles = request.auth.get('role', {}) if request.auth else {}
        allowed_home_ids = [int(k) for k in user_roles.keys() if str(k).isdigit()]

        last_24h = timezone.now() - timedelta(hours=24)

        data = SensorLog.objects.filter(
            device__home__in=allowed_home_ids,
            device_id=device_id,
            timestamp__gte=last_24h
        ).annotate(
            hour=TruncHour('timestamp')
        ).values('hour').annotate(
            avg_temp=Avg('temperature'),
            avg_hum=Avg('humidity'),
            avg_mq2=Avg('mq2_raw'),
            avg_mq135=Avg('mq135_raw')
        ).order_by('hour')

        return Response(data)

class SensorLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API này chỉ cho phép GET (Xem). Bị cấm hoàn toàn POST, PUT, DELETE.
    """
    serializer_class = SensorLogSerializer
    # Chỉ cần đăng nhập là được, quyền xem nhà nào sẽ được lọc ở hàm get_queryset
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_roles = self.request.auth.get('role', {}) if self.request.auth else {}
        allowed_home_ids = [int(k) for k in user_roles.keys() if str(k).isdigit()]

        # 1. Bức tường bảo mật: Chỉ cho phép lấy Log của các thiết bị thuộc nhà mình
        # Dùng 'device__home__in' vì SensorLog liên kết với Device, Device liên kết với Home
        queryset = SensorLog.objects.filter(device__home__in=allowed_home_ids)

        # 2. Tính năng Lọc: App Mobile sẽ truyền device_id lên để lấy log của 1 thiết bị cụ thể
        # Ví dụ: GET /api/sensor-logs/?device_id=5
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device_id=device_id)

        # 3. Sắp xếp: Luôn trả về Log MỚI NHẤT lên đầu (thay 'id' bằng tên cột ngày tháng của bạn nếu cần)
        return queryset.order_by('-timestamp')

class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated, IsDeviceAdminOrMemberReadOnly]

    def get_queryset(self):
        user_roles = self.request.auth.get('role', {})
        allowed_home_ids = [int(k) for k in user_roles.keys() if str(k).isdigit()]
        return Device.objects.filter(home__in=allowed_home_ids)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
