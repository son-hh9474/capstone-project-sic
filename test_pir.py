from gpiozero import MotionSensor, LED
from time import sleep
import threading

# --- Cấu hình chân GPIO ---
PIR_PIN = 4  # Chân GPIO của cảm biến PIR
LED_PIN = 17 # Chân GPIO của LED

# Thời gian LED sẽ sáng sau khi phát hiện chuyển động (delay phần mềm)
LED_ON_DELAY_SECONDS = 5

# --- Khởi tạo đối tượng cảm biến và LED ---
pir = MotionSensor(PIR_PIN)
led = LED(LED_PIN)

# Biến để theo dõi trạng thái LED (để không bật lại timer nếu LED đã được hẹn giờ tắt)
led_timer = None

def turn_off_led_after_delay():
    """Hàm này sẽ được gọi bởi timer để tắt LED."""
    led.off()
    print("LED đã tắt sau khi hết thời gian chờ.")

print(f"Bắt đầu kiểm tra cảm biến PIR trên chân GPIO {PIR_PIN} với LED trên chân GPIO {LED_PIN}...")
print("Di chuyển trước cảm biến PIR để kiểm tra.")
print(f"LED sẽ sáng trong {LED_ON_DELAY_SECONDS} giây kể từ lần phát hiện cuối cùng.")

try:
    # Vòng lặp chính liên tục kiểm tra trạng thái của PIR
    while True:
        if pir.is_active:
            # Phát hiện chuyển động (chân PIR đang HIGH)
            if not led.is_lit: # Nếu LED chưa sáng, bật nó lên
                led.on()
                print("!!! Phát hiện chuyển động - LED BẬT !!!")
            
            # Reset/Khởi động lại timer để giữ LED sáng thêm
            # Mỗi khi phát hiện chuyển động, timer sẽ được reset.
            # LED sẽ chỉ tắt nếu không có chuyển động nào được phát hiện trong suốt LED_ON_DELAY_SECONDS.
            if led_timer and led_timer.is_alive():
                led_timer.cancel() # Hủy timer cũ nếu nó đang chạy
            
            led_timer = threading.Timer(LED_ON_DELAY_SECONDS, turn_off_led_after_delay)
            led_timer.start()

        else:
            # Không phát hiện chuyển động (chân PIR đang LOW)
            # Logic tắt LED được quản lý bởi `led_timer` ở trên, không cần làm gì thêm ở đây
            pass 
        
        sleep(0.1) # Dừng một chút để không chiếm dụng CPU quá mức
        
except KeyboardInterrupt:
    print("\nChương trình bị ngắt bởi người dùng. Đang thoát...")
finally:
    if led_timer and led_timer.is_alive():
        led_timer.cancel() # Hủy timer nếu đang chạy
    led.off() # Đảm bảo LED tắt khi thoát
    print("Đã tắt LED và dọn dẹp GPIO.")