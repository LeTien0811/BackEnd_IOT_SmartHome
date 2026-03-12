import json
import paho.mqtt.client as mqtt
from django.utils import timezone
from datetime import timedelta

def on_connect(client, userdata, flags, rc):
    if rc = 0:
        print("✅ [MQTT] Đã kết nối Mosquitto Broker!")
        client.subscribe("home/sensors/gas")
    else:
        print(f"❌ [MQTT] Lỗi kết nối, mã lỗi: {rc}")

def on_message(client, userdata, msg):
    # Import trễ (Lazy Import) để tránh lỗi AppRegistryNotReady của Django
    from .models import SensorLog, Notify, Device 
    from django.db import close_old_connections
    
    # Giải quyết Điểm mù số 3: Dọn dẹp kết nối MySQL cũ bị timeout
    close_old_connections() 

    try:
        # Bóc tách JSON payload
        payload = json.loads(msg.payload.decode('utf-8'))
        temp = payload.get("temperature", 0)
        hum = payload.get("humidity", 0)
        mq2 = payload.get("mq2_raw", 0)
        mq135 = payload.get("mq135_raw", 0)
        device_id = payload.get("device_id", 1) # Mặc định thiết bị có ID = 1

        device = Device.objects.filter(device_id=device_id).first()
        if not device:
            print("⚠️ [MQTT] Thiết bị không tồn tại trong DB!")
            return

        # 1. Lưu log vào Database
        SensorLog.objects.create(
            device=device,
            temperature=temp,
            humidity=hum,
            mq2_raw=mq2,
            mq135_raw=mq135
        )
        
        print(f"📊 Đã lưu log: Nhiệt {temp}°C - MQ2 {mq2} - MQ135 {mq135}")

        # 2. Xử lý AI/Logic Cảnh báo Đỏ (Giả sử MQ vượt 2000 là nguy hiểm)
        if mq2 > 2000 or mq135 > 2000:
            now = timezone.now()
            # Giải quyết Điểm mù số 4: Cooldown 5 phút (300 giây) mới báo lại
            last_notify = Notify.objects.filter(device=device).order_by('-notify_date_create').first()
            
            if not last_notify or (now - last_notify.notify_date_create) > timedelta(minutes=5):
                # Lưu thông báo
                Notify.objects.create(
                    device=device,
                    notify_title="CẢNH BÁO ĐỎ: NGUY CƠ CHÁY NỔ/GAS!",
                    notify_content=f"Phát hiện nồng độ bất thường. MQ2: {mq2}, MQ135: {mq135}."
                )
                
                # Bắn lệnh MQTT ngược lại ESP32 để kích hoạt Quạt hút/Còi
                control_payload = {"fan_on": True, "siren_on": True}
                client.publish("home/devices/control", json.dumps(control_payload))
                
                print("🚨 ĐÃ PHÁT CẢNH BÁO VÀ BẬT QUẠT HÚT KHẨN CẤP!")

    except json.JSONDecodeError:
        print("❌ [MQTT] Lỗi định dạng JSON từ ESP32.")
    except Exception as e:
        print(f"❌ [MQTT] Lỗi xử lý: {e}")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Kết nối tới Broker nội bộ trên máy Debian
    client.connect("127.0.0.1", 1883, 60)

    # Giải quyết Điểm mù số 1: Dùng loop_start() thay vì loop_forever()
    # Nó sẽ tạo một Background Thread riêng, không block API của Flutter
    client.loop_start()
    
    