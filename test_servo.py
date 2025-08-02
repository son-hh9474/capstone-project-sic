from gpiozero import Servo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# Khai báo factory để tương thích với Pi 5
factory = LGPIOFactory()

# Khai báo chân GPIO bạn dùng để kết nối với servo
# Thay đổi số 18 nếu bạn dùng chân GPIO khác
servo = Servo(18, pin_factory=factory)

try:
    while True:
        # Quay servo về vị trí tối thiểu (0 độ)
        print("Quay về vị trí tối thiểu...")
        servo.min()
        sleep(1)

        # Quay servo về vị trí giữa (90 độ)
        print("Quay về vị trí giữa...")
        servo.mid()
        sleep(1)

        # Quay servo về vị trí tối đa (180 độ)
        print("Quay về vị trí tối đa...")
        servo.max()
        sleep(1)

except KeyboardInterrupt:
    print("Thoát chương trình.")
    servo.close()