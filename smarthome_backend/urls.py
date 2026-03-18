"""
URL configuration for smarthome_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from iot_api.views import CustomLoginView, DeviceViewSet, SensorLogViewSet, HourlyChartAPIView, RoomViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'sensor-logs', SensorLogViewSet, basename='sensorlog')
urlpatterns = [
    path('admin/', admin.site.urls),
    # API login born JWT
    path('api/auth/login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    # API refresh Token when Access Token expired
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/chart/hourly/', HourlyChartAPIView.as_view(), name='chart_hourly'),

    # All API for device will be located last prefix /api/
    # Ex: GET /api/devices/ (get list device), DELETE /api/devices/1/ (delete)
    path('api/', include(router.urls)),
]
