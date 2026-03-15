from django.apps import AppConfig
import os

class IotApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'iot_api'
    def ready(self):
        if os.environ.get('RUN_MAIN') == True:
            from . import mqtt_setup
            mqtt_setup.start_mqtt()