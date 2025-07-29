from time import sleep

from config import TRASH_PIN_DISTANCE_ECHO, TRASH_PIN_DISTANCE_TRIGGER, TRASH_PIN_MOTION, SERVO

from gpiozero import DistanceSensor, MotionSensor, Servo

from RPLCD.i2c import CharLCD

import requests

import time

import threading
#phần khai báo cảm biến, màn hình, động cơ servo

motion_detected_status = False

fill_level = 0

Max_range = 4.0

Threshold = 20

Distance_sensor = DistanceSensor(echo=TRASH_PIN_DISTANCE_ECHO, trigger=TRASH_PIN_DISTANCE_TRIGGER, max_distance=Max_range, queue_len=5, partial=True)

Pir_sensor = MotionSensor(TRASH_PIN_MOTION)

lid_servo = Servo(SERVO)

lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2) 

is_lid_open = False

#cho servo xoay về chính giữa
lid_servo.mid()

def _display_status(line1, line2):
    """Hiển thị trạng thái"""
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string(line1[:16])
    if line2:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(line2[:16])

def _display_the_fill(data):
    """hiển thị độ đầy"""
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string('the fill level:')
    lcd.cursor_pos = (1, 0)
    lcd.write_string(str(data) + '%')

    
def _open_lid():
    """Mở nắp thùng rác"""
    global is_lid_open
    if not is_lid_open:
        lid_servo.max()
        is_lid_open = True
        _display_status("Chao ban!", "Hay bo rac vao")
        print("Nắp thùng rác MỞ - Phát hiện NGƯỜI")

def _close_lid():
        """Đóng nắp thùng rác"""
        global is_lid_open
        if is_lid_open:
            lid_servo.min()
            is_lid_open = False
            _display_status("Cam on ban!", "Hen gap lai")
            print("Nắp thùng rác ĐÓNG")


# ----- Cấu hình ThingSpeak của bạn -----
# Thay thế bằng API Key của kênh ThingSpeak của bạn
THINGSPEAK_API_KEY = "P2WO76WAQYQWUT6M"
# URL API của ThingSpeak
THINGSPEAK_URL = "https://api.thingspeak.com/update"
def send_data_to_thingspeak():
    """
    Gửi dữ liệu cảm biến lên kênh ThingSpeak.
    :param fill_level: Mức độ đầy của thùng rác (0-100%).
    :param lid_status: Trạng thái nắp (0: Đóng, 1: Mở).
    :param ir_detected: Trạng thái phát hiện người (0: Không, 1: Có).
    """
    global fill_level # Đọc biến toàn cục
    global is_lid_open # Đọc biến toàn cục
    global motion_detected_status # Đọc biến toàn cục
    payload = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": int(fill_level),     # Map với Field 1: FillLevel trên ThingSpeak
        "field2": is_lid_open,    # Map với Field 2: LidStatus trên ThingSpeak
        "field3": motion_detected_status  # Map với Field 3: IRDetected trên ThingSpeak
    }

    try:
        response = requests.get(THINGSPEAK_URL, params=payload)
        # Hoặc dùng requests.post(THINGSPEAK_URL, data=payload) nếu muốn dùng POST
        
        if response.status_code == 200:
            print(f"Dữ liệu đã được gửi thành công. Phản hồi: {response.text}")
        else:
            print(f"Lỗi khi gửi dữ liệu. Mã trạng thái: {response.status_code}, Phản hồi: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối: {e}")


def measure_the_fill_level():
    """
    hàm đo độ đầy thùng rác: sử dụng cảm biến siêu âm kết hợp màn hình LCD 16x2 xuất ra màn hình
    """
    global is_lid_open
    global fill_level
    if not is_lid_open:
        distance = Distance_sensor.distance * 100
        fill_level = ((Threshold - distance) / Threshold) * 100
        if fill_level_calculated < 0: fill_level_calculated = 0
        if fill_level_calculated > 100: fill_level_calculated = 100
        _display_the_fill(int(fill_level))
        sleep(60)
    

def _is_person_nearby():
    """
    Kiểm tra có NGƯỜI gần không sử dụng PIR_Sensor và điều khiển nắp.
    Cập nhật lịch sử phát hiện người để quyết định đóng nắp.
    """
    global motion_detected_status
    motion_detected = Pir_sensor.is_active
    motion_detected_status = motion_detected
    if motion_detected_status: 
        _open_lid()
        sleep(5)
    else: 
        _close_lid()
    sleep(0.5)

# =====================================================================================
# CÁC HÀM WRAPPER SẼ CHẠY TRONG CÁC LUỒNG RIÊNG
# =====================================================================================

def _person_nearby_thread_func():
    """Luồng xử lý phát hiện người và điều khiển nắp."""
    print("Luồng 'Phát Hiện Người' bắt đầu.")
    while True:
        _is_person_nearby() # Gọi hàm logic chính
        sleep(0.5) # Tần suất kiểm tra PIR (0.5 giây)

def _fill_level_thread_func():
    """Luồng xử lý đo mức đầy."""
    print("Luồng 'Đo Mức Đầy' bắt đầu.")
    while True:
        measure_the_fill_level() # Gọi hàm logic chính
        sleep(1) # Tần suất đo mức đầy (1 giây)

def _thingspeak_upload_thread_func():
    """Luồng xử lý gửi dữ liệu lên ThingSpeak."""
    print("Luồng 'ThingSpeak Upload' bắt đầu.")
    THINGSPEAK_UPLOAD_INTERVAL_SEC = 20 # Gửi dữ liệu mỗi 20 giây
    last_upload_time = 0
    while True:
        current_time = time.time()
        if current_time - last_upload_time >= THINGSPEAK_UPLOAD_INTERVAL_SEC:
            send_data_to_thingspeak() # Gọi hàm logic chính
            last_upload_time = current_time
        sleep(1) # Kiểm tra điều kiện gửi dữ liệu mỗi giây

# =====================================================================================
# KHỐI MAIN CỦA CHƯƠNG TRÌNH - SẼ CHẠY KHI FILE ĐƯỢC THỰC THI TRỰC TIẾP
# =====================================================================================
if __name__ == "__main__":
    print("Khởi tạo hệ thống thùng rác thông minh...")
    _display_status("Khoi dong...", "Smart Waste Bin")
    sleep(2) # Đợi một chút để khởi động LCD

    # Tạo và khởi động các luồng
    person_thread = threading.Thread(target=_person_nearby_thread_func)
    person_thread.daemon = True # Luồng daemon sẽ tự động dừng khi chương trình chính kết thúc
    person_thread.start()

    fill_thread = threading.Thread(target=_fill_level_thread_func)
    fill_thread.daemon = True
    fill_thread.start()

    thingspeak_thread = threading.Thread(target=_thingspeak_upload_thread_func)
    thingspeak_thread.daemon = True
    thingspeak_thread.start()

    print("Các luồng đã được khởi động. Chương trình chính đang chạy...")
    
    # Vòng lặp chính của chương trình (có thể không làm gì nhiều, chỉ giữ chương trình chạy)
    try:
        while True:
            # Luồng chính có thể thực hiện các tác vụ nhẹ hoặc chỉ đơn giản là ngủ
            # để các luồng khác làm việc.
            sleep(1)
    except KeyboardInterrupt:
        print("\nChương trình bị ngắt bởi người dùng. Đang thoát...")
    finally:
        # Đảm bảo LCD được tắt hoặc hiển thị thông báo cuối cùng
        lcd.clear()
        lcd.write_string("Shutting down...")
        sleep(1)
        lcd.clear()
        print("Chương trình đã thoát.")




