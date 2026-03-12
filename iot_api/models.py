from django.db import models
from django.contrib.auth.models import AbstractUser

class Member(AbstractUser):
    # AbstractUser đã có sẵn: username, email, password, first_name, last_name
    avatar_url = models.URLField(blank=True, null=True) 
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
class Home(models.Model):
    home = models.AutoField(primary_key=True)
    home_name = models.CharField(max_length=255)
    home_number_phone = models.CharField(max_length=12)
    home_address = models.CharField(max_length=255)
    home_password = models.CharField(max_length=255) 
    home_date_created = models.DateTimeField(auto_now_add=True)
    home_date_update = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.home_id

class HomeMember(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='homes')
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name='members')
    role = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'home')  
    
class Device(models.Model):
    device = models.AutoField(primary_key=True)
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name='devices')
    device_name = models.CharField(max_length=150)
    device_status = models.CharField(max_length=20)
    device_is_on = models.BooleanField(default=False) # Đã đổi sang Boolean
    device_date_create = models.DateTimeField(auto_now_add=True)
    device_date_update = models.DateTimeField(auto_now=True)    
    def __str__(self):
        return f"{self.device_name} - {self.home.home_name}"
    
class SensorLog(models.Model):
    sensor_log = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensor_logs')
    temperature = models.FloatField()
    humidity = models.FloatField()
    mq2_raw = models.FloatField()
    mq135_raw = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Notify(models.Model):
    notify = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='notifications')
    notify_title = models.CharField(max_length=255)
    notify_content = models.TextField()
    notify_date_create = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    report = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='reports')
    report_title = models.CharField(max_length=255)
    report_content = models.TextField()
    report_date_create = models.DateTimeField(auto_now_add=True)