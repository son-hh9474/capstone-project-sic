from gpiozero import DistanceSensor
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# Sửa lỗi: LGPIOFactory phải được gọi như một hàm để tạo đối tượng
factory = LGPIOFactory()

# Khai báo cảm biến với pin_factory đã được sửa
# Khoảng cách được trả về là mét
sensor = DistanceSensor(echo=24, trigger=23, max_distance=4.0, queue_len=10, partial=True, pin_factory=factory)

try:
    while True:
        # Lấy khoảng cách gần nhất
        distance_meters = sensor.distance
        
        # Chuyển đổi sang centimet để dễ đọc hơn
        distance_cm = distance_meters * 100
        
        # Sửa lỗi: Không thể cộng trực tiếp chuỗi và số thực
        # Sử dụng f-string để in giá trị một cách chính xác
        print(f"Khoảng cách: {distance_cm:.2f} cm")
        
        # Thêm một khoảng chờ để tránh chương trình chạy quá nhanh
        sleep(1)

except KeyboardInterrupt:
    print("Thoát chương trình.")
    sensor.close()