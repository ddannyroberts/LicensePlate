# Arduino Mega 2560 Integration Guide

## Overview

โปรเจค License Plate System ได้รับการอัพเดทให้รองรับ Arduino Mega 2560 แล้ว โดยมีการปรับปรุงใหม่ดังนี้:

### ✅ สิ่งที่ได้รับการปรับปรุง

1. **โค้ด Arduino** ปรับให้เหมาะกับ Mega 2560
2. **Communication Methods** รองรับทั้ง Serial และ Ethernet
3. **Pin Assignments** เฉพาะสำหรับ Mega 2560
4. **Python Integration** เชื่อมต่อกับ Flask app
5. **Web Interface** อัพเดท control panel

## Quick Start Guide

### 1. เลือกวิธีการสื่อสาร

#### Option A: Serial Communication (แนะนำ)
```cpp
#define COMMUNICATION_METHOD SERIAL
```

**ข้อดี:**
- ไม่ต้องใช้ Shield เพิ่ม
- เชื่อมต่อผ่าน USB ได้เลย
- ราคาถูก พร้อมใช้งาน

**ข้อเสีย:**
- ต้องเชื่อมต่อกับคอมพิวเตอร์เสมอ
- ไม่มี Web interface

#### Option B: Ethernet Shield
```cpp
#define COMMUNICATION_METHOD ETHERNET
```

**ข้อดี:**
- มี Web interface
- ไม่ต้องพึ่งคอมพิวเตอร์
- Access ผ่าน network ได้

**ข้อเสีย:**
- ต้องซื้อ Ethernet Shield เพิ่ม
- ต้องมี network infrastructure

### 2. การติดตั้ง Hardware

#### Arduino Mega 2560 Pin Connections:
```
Pin 9  → Servo Motor (Signal)
Pin 13 → Built-in LED (Power indicator)
Pin 7  → Status LED (Optional)
Pin 8  → Buzzer (Optional)
5V     → Servo Power (Red)
GND    → Servo Ground (Brown/Black)
```

#### สำหรับ Ethernet (ถ้าใช้):
- ต่อ Ethernet Shield บน Arduino Mega
- เสียบ RJ45 cable เข้า router

### 3. การติดตั้ง Software

#### Arduino IDE:
1. เปิดไฟล์ `arduino_gate_controller.ino`
2. เลือก Board: Arduino Mega 2560
3. เลือก Port ที่ถูกต้อง
4. Upload โค้ด

#### Python Dependencies:
```bash
pip install pyserial  # สำหรับ Serial communication
```

### 4. การกำหนดค่า

#### ใน app.py:
```python
# เลือกวิธีการสื่อสาร
ARDUINO_COMMUNICATION = "SERIAL"  # หรือ "ETHERNET"

# สำหรับ Serial
ARDUINO_SERIAL_PORT = "/dev/ttyUSB0"  # Linux/Mac
# ARDUINO_SERIAL_PORT = "COM3"       # Windows

# สำหรับ Ethernet
ARDUINO_IP = "192.168.1.177"
```

#### ใน Arduino:
```cpp
// สำหรับ Ethernet (ถ้าใช้)
IPAddress ip(192, 168, 1, 177);
```

## การใช้งาน

### 1. Serial Commands
เมื่อใช้ Serial communication สามารถส่งคำสั่งได้ดังนี้:

```
OPEN                    → เปิดประตู
CLOSE                   → ปิดประตู
STATUS                  → ขอสถานะ
ACCESS:ABC123:1         → อนุญาตป้ายทะเบียน ABC123
ACCESS:XYZ789:0         → ปฏิเสธป้ายทะเบียน XYZ789
```

### 2. Web Interface (Ethernet เท่านั้น)
เข้าใช้งานผ่าน: `http://192.168.1.177`

API Endpoints:
```
GET  /api/status        → ดูสถานะ
POST /api/open          → เปิดประตู
POST /api/close         → ปิดประตู
```

### 3. Flask App Integration
ระบบจะใช้งานอัตโนมัติผ่าน License Plate Detection:

```python
# ตัวอย่างการใช้งาน
result = send_to_arduino("gate/status")
result = open_gate_arduino("ABC123", "John Doe", True)
```

## การทดสอบ

### 1. ทดสอบ Arduino
1. เปิด Serial Monitor (115200 baud)
2. ส่งคำสั่ง: `STATUS`
3. ควรได้ response JSON กลับมา

### 2. ทดสอบ Python Integration
1. เข้า Admin Panel: `/admin/arduino_control`
2. กด "Test Connection"
3. ตรวจสอบ status และ log

### 3. ทดสอบ License Plate Detection
1. อัพโหลดรูป license plate
2. ตรวจสอบว่า Arduino ได้รับคำสั่งหรือไม่
3. ดู log ใน Serial Monitor

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย:

#### 1. Serial Port ไม่ทำงาน
```bash
# ดู available ports
ls /dev/tty*           # Linux/Mac
# หรือ Device Manager   # Windows

# ปรับสิทธิ์ (Linux)
sudo chmod 666 /dev/ttyUSB0
```

#### 2. Servo ไม่เคลื่อนที่
- ตรวจสอบการต่อ power (5V, GND)
- ตรวจสอบ signal wire (Pin 9)
- ทดสอบด้วย servo sweep code ก่อน

#### 3. pyserial Error
```bash
pip install pyserial
# หรือถ้าใช้ conda
conda install pyserial
```

#### 4. Permission Denied (Linux)
```bash
sudo usermod -a -G dialout $USER
# ต้อง logout/login ใหม่
```

### Debug Commands:

#### Arduino Serial Monitor:
```
STATUS     → ตรวจสอบสถานะ
OPEN       → ทดสอบเปิดประตู
CLOSE      → ทดสอบปิดประตู
```

#### Python Debug:
```python
# เทส connection
result = test_arduino_connection()
print(result)

# เทส basic command
result = send_arduino_serial_command("STATUS")
print(result)
```

## Security Notes

⚠️ **ข้อควรระวัง:**
- ใช้เฉพาะใน network ที่ปลอดภัย
- ไม่แชร์ IP address หรือ port ออกสู่อินเทอร์เน็ต
- ตั้งรหัสผ่าน admin ให้แข็งแรง
- ตรวจสอบ physical access ไปยัง Arduino

## Advanced Configuration

### Custom Pin Assignment:
```cpp
const int servoPin = 9;       // เปลี่ยนได้ (PWM pins: 2-13, 44-46)
const int ledPin = 13;        // Built-in LED
const int buzzerPin = 8;      // Buzzer pin
const int statusLedPin = 7;   // Status indicator
```

### Auto-close Timing:
```cpp
const unsigned long AUTO_CLOSE_TIME = 10000; // 10 วินาที
```

### Network Settings (Ethernet):
```cpp
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);
```

## สรุป

ระบบได้รับการปรับปรุงให้เหมาะกับ Arduino Mega 2560 เรียบร้อยแล้ว:

✅ รองรับ Serial และ Ethernet communication
✅ Pin assignments เฉพาะสำหรับ Mega 2560
✅ Python integration ที่สมบูรณ์
✅ Web interface อัพเดทแล้ว
✅ Error handling และ debugging

**คำแนะนำ:** ใช้ Serial communication สำหรับการเริ่มต้น เพราะง่ายและไม่ต้องซื้ออุปกรณ์เพิ่ม

---

🔧 **ต้องการความช่วยเหลือเพิ่มเติม:**
- ตรวจสอบ Serial Monitor ของ Arduino (115200 baud)
- ดู log ใน Flask app console
- ใช้ Test Connection ใน Admin Panel
