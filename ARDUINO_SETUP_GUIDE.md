# คู่มือการติดตั้งและเชื่อมต่อ Arduino Gate Controller

## 📋 อุปกรณ์ที่ต้องใช้

### Arduino และอุปกรณ์
- **Arduino WiFi board** (ESP32, Arduino UNO WiFi Rev2, หรือ Arduino MKR WiFi 1010)
- **SG90 Micro Servo Motor** (1 ตัว)
- **Jumper wires** (ชาย-เมีย และ ชาย-ชาย)
- **Breadboard** (แนะนำ)
- **Buzzer** (5V, เสียงเตือน - ไม่บังคับ)
- **LED** (สำหรับแสดงสถานะ - ไม่บังคับ)
- **Resistor 220Ω** (สำหรับ LED)

### ซอฟต์แวร์
- **Arduino IDE** (เวอร์ชันล่าสุด)
- **ไลบรารี ArduinoJson** (ติดตั้งผ่าน Library Manager)

## 🔌 การเชื่อมต่อสาย

### ESP32 (แนะนำ)
```
SG90 Servo Motor:
- สีน้ำตาล (GND) → ESP32 GND
- สีแดง (VCC) → ESP32 5V
- สีส้ม (Signal) → ESP32 Pin 9

Buzzer (ไม่บังคับ):
- ขาบวก → ESP32 Pin 5
- ขาลบ → ESP32 GND

LED (ไม่บังคับ):
- ขาบวก → ESP32 Pin 2 (มี Resistor 220Ω)
- ขาลบ → ESP32 GND
```

### Arduino UNO WiFi Rev2
```
SG90 Servo Motor:
- สีน้ำตาล (GND) → Arduino GND
- สีแดง (VCC) → Arduino 5V
- สีส้ม (Signal) → Arduino Pin 9

Buzzer (ไม่บังคับ):
- ขาบวก → Arduino Pin 5
- ขาลบ → Arduino GND

LED (ไม่บังคับ):
- ขาบวก → Arduino Pin 2 (มี Resistor 220Ω)
- ขาลบ → Arduino GND
```

## 💻 การติดตั้งซอฟต์แวร์

### 1. ติดตั้ง Arduino IDE
1. ดาวน์โหลดจาก https://www.arduino.cc/en/software
2. ติดตั้งตามขั้นตอน

### 2. ติดตั้ง Board Package (สำหรับ ESP32)
1. เปิด Arduino IDE
2. ไปที่ File → Preferences
3. ใน "Additional Boards Manager URLs" ใส่:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. ไปที่ Tools → Board → Boards Manager
5. ค้นหา "ESP32" และติดตั้ง

### 3. ติดตั้ง Libraries ที่จำเป็น
1. ไปที่ Sketch → Include Library → Manage Libraries
2. ค้นหาและติดตั้ง:
   - **ArduinoJson** by Benoit Blanchon
   - **Servo** (มากับ Arduino IDE)

## 🛠️ การตั้งค่า Code

### 1. เปิดไฟล์ arduino_gate_controller.ino
### 2. แก้ไขการตั้งค่า WiFi
```cpp
const char* ssid = "ชื่อ_WiFi_ของคุณ";
const char* password = "รหัสผ่าน_WiFi_ของคุณ";
```

### 3. ปรับ Pin Numbers (ถ้าจำเป็น)
```cpp
const int servoPin = 9;    // Pin สำหรับ Servo
const int ledPin = 2;      // Pin สำหรับ LED
const int buzzerPin = 5;   // Pin สำหรับ Buzzer
```

### 4. Upload Code
1. เชื่อมต่อ Arduino กับคอมพิวเตอร์
2. เลือก Board และ Port ที่ถูกต้อง
3. กด Upload

## 🌐 การตั้งค่า Network

### 1. หา IP Address ของ Arduino
หลังจาก Upload Code แล้ว:
1. เปิด Serial Monitor (Ctrl+Shift+M)
2. รอให้ Arduino เชื่อมต่อ WiFi
3. จดบันทึก IP Address ที่แสดง เช่น `192.168.1.100`

### 2. แก้ไข Flask App
ในไฟล์ `app.py` ตรง:
```python
ARDUINO_IP = "192.168.1.100"  # ใส่ IP ของ Arduino
```

### 3. ทดสอบการเชื่อมต่อ
1. เปิดเบราว์เซอร์
2. ไปที่ `http://IP_ของ_Arduino` เช่น `http://192.168.1.100`
3. ควรเห็นหน้าควบคุมประตู

## 🎯 การทดสอบระบบ

### ทดสอบ Arduino
1. เข้าหน้าเว็บของ Arduino
2. กด "Open Gate" และ "Close Gate"
3. สังเกต Servo Motor ควรหมุน

### ทดสอบการเชื่อมต่อกับ Flask
1. เข้า Admin Dashboard ใน Flask App
2. ไปที่ Arduino Control Panel
3. ทดสอบเปิด/ปิดประตูจากเว็บ

### ทดสอบการจดจำป้ายทะเบียน
1. เพิ่มป้ายทะเบียนที่ได้รับอนุญาต
2. ทดสอบด้วย Live Camera หรือ Upload Video
3. เมื่อจดจำป้ายทะเบียนได้ ประตูควรเปิดอัตโนมัติ

## 🚨 การแก้ไขปัญหา

### Arduino ไม่เชื่อมต่อ WiFi
- ตรวจสอบชื่อและรหัสผ่าน WiFi
- ตรวจสอบสัญญาณ WiFi
- ลองใช้ WiFi 2.4GHz (ESP32 ไม่รองรับ 5GHz)

### Servo ไม่หมุน
- ตรวจสอบการต่อสาย (GND, VCC, Signal)
- ตรวจสอบแหล่งจ่ายไฟ 5V
- ลองเปลี่ยน Pin ของ Servo

### Flask ไม่เชื่อมต่อกับ Arduino
- ตรวจสอบ IP Address ใน `app.py`
- ตรวจสอบ Firewall
- ตรวจสอบว่า Arduino และ Flask อยู่ในเครือข่ายเดียวกัน

### การ Debug
1. เปิด Serial Monitor ใน Arduino IDE
2. ดู log ใน Terminal ของ Flask App
3. ตรวจสอบ Network connectivity

## 🔧 การปรับแต่งเพิ่มเติม

### ปรับเวลาปิดประตูอัตโนมัติ
```cpp
const unsigned long AUTO_CLOSE_TIME = 10000; // มิลลิวินาที (10 วินาที)
```

### ปรับมุมการเปิด/ปิดประตู
```cpp
const int GATE_CLOSED = 0;   // มุมปิด (องศา)
const int GATE_OPEN = 90;    // มุมเปิด (องศา)
```

### เพิ่มระบบรักษาความปลอดภัย
- เพิ่ม Authentication Token
- เพิ่ม Rate Limiting
- เพิ่ม Log การเข้าถึง

## 📞 การขอความช่วยเหลือ

หากมีปัญหาการติดตั้งหรือใช้งาน:
1. ตรวจสอบการเชื่อมต่อสายอีกครั้ง
2. ตรวจสอบ Code และการตั้งค่า
3. ใช้ Serial Monitor เพื่อ Debug
4. ตรวจสอบ Network และ Firewall

## 🎉 สำเร็จแล้ว!

เมื่อตั้งค่าเสร็จสิ้น ระบบของคุณจะสามารถ:
- จดจำป้ายทะเบียนรถได้
- เปิดประตูอัตโนมัติสำหรับรถที่ได้รับอนุญาต
- ควบคุมประตูแบบ Manual ผ่านเว็บ
- บันทึก Log การเข้า-ออก
- แสดงสถานะระบบแบบ Real-time