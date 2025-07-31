import RPi.GPIO as GPIO
import time

# Chân GPIO mà servo được kết nối (sử dụng chế độ BCM numbering)
# Thay thế giá trị này bằng chân GPIO thực tế mà bạn đang dùng, ví dụ: SERVO = 18 trong config.py của bạn
SERVO_PIN = 18 

# Tần số PWM cho servo thường là 50Hz (50 chu kỳ/giây)
PWM_FREQUENCY = 50

# Các giá trị chu kỳ nhiệm vụ (Duty Cycle) cho các góc của servo SG90
# Đây là các giá trị tiêu chuẩn, có thể cần tinh chỉnh nhỏ tùy theo servo của bạn
# 0 độ: thường là 2.5% duty cycle
# 90 độ: thường là 7.5% duty cycle
# 180 độ: thường là 12.5% duty cycle

# Hàm chuyển đổi góc sang chu kỳ nhiệm vụ
def angle_to_duty_cycle(angle):
    # Công thức: duty = (angle / 18) + 2.5
    # Ví dụ: 0 độ -> (0/18)+2.5 = 2.5
    # 90 độ -> (90/18)+2.5 = 5+2.5 = 7.5
    # 180 độ -> (180/18)+2.5 = 10+2.5 = 12.5
    return (angle / 18.0) + 2.5

print(f"Bắt đầu kiểm tra Servo trên chân GPIO BCM {SERVO_PIN} bằng RPi.GPIO...")
    # Thiết lập chế độ đánh số chân GPIO: BCM (số GPIO, không phải số chân vật lý)
GPIO.setmode(GPIO.BCM)
# Thiết lập chân servo là output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Khởi tạo PWM object
# Chân: SERVO_PIN, Tần số: PWM_FREQUENCY (50Hz)
pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)

def angle_to_duty_cycle(angle):
    return (angle / 18.0) + 2.5

def move_servo_smoothly(start_angle, end_angle, duration_seconds):
    global pwm
    step_delay = duration_seconds / abs(end_angle - start_angle) # Độ trễ cho mỗi bước 1 độ

    if start_angle < end_angle:
        step = 1
    else:
        step = -1

    print(f"Bắt đầu di chuyển servo từ {start_angle} đến {end_angle} trong {duration_seconds} giây...")

    for angle in range(start_angle, end_angle + step, step):
        duty_cycle = angle_to_duty_cycle(angle)
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(step_delay) # Chờ cho mỗi bước
    
    # Đảm bảo servo ở vị trí cuối cùng và giữ ở đó một chút
    pwm.ChangeDutyCycle(angle_to_duty_cycle(end_angle))
    time.sleep(1) # Giữ thêm một chút ở vị trí cuối


def main():

    global pwm
    # Bắt đầu PWM với chu kỳ nhiệm vụ ban đầu là 0 (servo sẽ không di chuyển hoặc ở vị trí nghỉ)
    pwm.start(0)
    print("PWM đã khởi động.")
    time.sleep(1) # Chờ một chút để ổn định

    try:
        angles_to_test = [0, 90, 180, 90, 0] # Các góc để kiểm tra

        while True:
            move_servo_smoothly(0, 90, 1)

            move_servo_smoothly(90, 180, 1)

            move_servo_smoothly(180, 90, 1)

            move_servo_smoothly(90, 0, 1)
        print("Hoàn tất các bước kiểm tra servo.")

    except KeyboardInterrupt:
        print("\nChương trình bị ngắt bởi người dùng.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        # Quan trọng: Dừng PWM và dọn dẹp GPIO khi kết thúc
        print("Dừng PWM và dọn dẹp GPIO...")
        pwm.stop() # Dừng PWM
        GPIO.cleanup() # Giải phóng tất cả các chân GPIO đã sử dụng
        print("Đã dọn dẹp GPIO. Thoát chương trình.")

if __name__ == "__main__":
    main()