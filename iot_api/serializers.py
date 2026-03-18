from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import HomeMember, Device, SensorLog, Member, Room

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ['device_date_create', 'device_date_update']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = Member.objects.filter(email=email).first()

            if user and user.check_password(password):
                if not user.is_active:
                    raise exceptions.AuthenticationFailed('Tài khoản này đã bị khóa')
            else:
                raise exceptions.AuthenticationFailed('Thông tin tài khoản không đúng')
        else:
            raise exceptions.AuthenticationFailed('Vui lòng cung cấp đầy đủ thông tin')

        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        home_role = {}
        membership = HomeMember.objects.filter(member=user)
        for hm in membership:
            home_role[str(hm.home.home)] = hm.role

        token['role'] = home_role

        return {
            'refresh': str(token),
            'access': str(token.access_token),
        }

class SensorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorLog
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

# {
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3MzkzNzM2MiwiaWF0IjoxNzczMzMyNTYyLCJqdGkiOiJkNThkZmJmZGViODU0ODg1YjA0YzQwNzU4ZDkwNjlhMSIsInVzZXJfaWQiOiIxIiwidXNlcm5hbWUiOiJsZXZpZXR0aWVuIiwiZW1haWwiOiJsZXRpZW4yMDgxQGdtYWlsLmNvbSIsInJvbGUiOnt9fQ.0NRyK7mzMprU2TlmEFh9g3sHj3X_idvafwJjmT0Vs3Y",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzczMzMzNDYyLCJpYXQiOjE3NzMzMzI1NjIsImp0aSI6ImQ2YmJlZDMwNmFmMzQxNDM5NDIyZjBhNjBjYjFlYzBmIiwidXNlcl9pZCI6IjEiLCJ1c2VybmFtZSI6ImxldmlldHRpZW4iLCJlbWFpbCI6ImxldGllbjIwODFAZ21haWwuY29tIiwicm9sZSI6e319._nCkwIbGyZdb-e0jvrvX6Ha7eQKYUIsnV3xIgyBV_U8"
# }
