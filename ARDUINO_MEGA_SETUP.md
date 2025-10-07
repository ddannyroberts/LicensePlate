# Arduino Mega 2560 Gate Controller Setup Guide

## Hardware Requirements

### Arduino Mega 2560
- ✅ Arduino Mega 2560 R3
- ✅ USB Cable (Type B)
- ✅ Power Supply (7-12V recommended)

### Components
- 🔧 SG90 Servo Motor (for gate mechanism)
- 💡 LED (optional status indicator)
- 🔊 Buzzer (optional audio feedback)
- 📡 **Choose ONE communication method:**
  - **Option A:** Ethernet Shield (W5100/W5500) + RJ45 cable
  - **Option B:** Serial communication via USB
  - **Option C:** ESP32/ESP8266 as WiFi module

### Pin Connections (Default Configuration)

```
Arduino Mega 2560 Pin Assignment:
├── Pin 9  → Servo Motor (Signal Wire)
├── Pin 13 → Built-in LED (Power indicator)
├── Pin 7  → External Status LED (optional)
├── Pin 8  → Buzzer (optional)
└── GND/5V → Power connections
```

## Software Setup

### 1. Arduino IDE Configuration
```bash
# Install required libraries (if using Ethernet)
Library Manager → Search and Install:
- Ethernet (by Arduino)
- Servo (by Arduino)
```

### 2. Communication Method Selection

Edit the configuration in `arduino_gate_controller.ino`:

```cpp
// Choose your communication method
#define COMMUNICATION_METHOD SERIAL    // Options: ETHERNET, SERIAL
```

### Option A: Ethernet Shield Setup
```cpp
#define COMMUNICATION_METHOD ETHERNET

// Network configuration
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);  // Set your network IP
```

**Hardware Connection:**
- Mount Ethernet Shield on Arduino Mega
- Connect RJ45 cable to your router/switch
- Power the Arduino via USB or external power

**Web Interface:**
- Access: `http://192.168.1.177` (or your configured IP)

### Option B: Serial Communication Setup
```cpp
#define COMMUNICATION_METHOD SERIAL
```

**Hardware Connection:**
- Connect Arduino to computer via USB
- No additional networking hardware required

**Control Commands:**
```
Serial Monitor Commands (115200 baud):
├── OPEN          → Open gate
├── CLOSE         → Close gate
├── STATUS        → Get gate status
└── ACCESS:ABC123:1 → Authorized plate access
```

### Option C: ESP32/ESP8266 WiFi Module
If you want to add WiFi capability, connect an ESP module:

**ESP32 to Mega Connection:**
```
ESP32   →  Mega 2560
├── TX  →  Pin 19 (RX1)
├── RX  →  Pin 18 (TX1)
├── GND →  GND
└── 3.3V→  3.3V
```

## Installation Steps

### 1. Hardware Assembly
1. **Mount Components:**
   - Attach servo to gate mechanism
   - Connect servo signal wire to Pin 9
   - Connect power (red) to 5V, ground (brown) to GND

2. **Optional Components:**
   - LED: Connect to Pin 7 (with resistor)
   - Buzzer: Connect to Pin 8
   - Status indicators as needed

3. **Communication Setup:**
   - **Ethernet:** Mount shield and connect network cable
   - **Serial:** Connect USB cable to computer
   - **WiFi:** Connect ESP module as described above

### 2. Software Configuration
1. **Upload Code:**
   ```bash
   Arduino IDE → Tools → Board → Arduino Mega 2560
   Arduino IDE → Tools → Port → Select your port
   Arduino IDE → Upload
   ```

2. **Test Basic Functions:**
   ```bash
   # Open Serial Monitor (115200 baud)
   # Send commands: OPEN, CLOSE, STATUS
   ```

### 3. Integration with License Plate System

#### For Serial Communication:
Update your Python Flask app to communicate via serial:

```python
import serial
import json

def send_arduino_command(command):
    ser = serial.Serial('/dev/ttyUSB0', 115200)  # Adjust port
    ser.write(f"{command}\n".encode())
    response = ser.readline().decode().strip()
    ser.close()
    return response

# Usage examples:
send_arduino_command("OPEN")
send_arduino_command("ACCESS:ABC123:1")  # Authorized plate
send_arduino_command("ACCESS:XYZ789:0")  # Denied plate
```

#### For Ethernet Communication:
Update your Flask app to use HTTP requests:

```python
import requests

ARDUINO_IP = "192.168.1.177"

def send_arduino_request(endpoint, data=None):
    url = f"http://{ARDUINO_IP}/api/{endpoint}"
    if data:
        response = requests.post(url, json=data)
    else:
        response = requests.get(url)
    return response.json()

# Usage examples:
send_arduino_request("open")
send_arduino_request("status")
```

## Pin Configuration Details

### Arduino Mega 2560 Pinout Reference
```
Digital PWM Pins (suitable for servo): 2-13, 44-46
├── Pin 9  → Servo (PWM)
├── Pin 13 → Built-in LED
├── Pin 7  → Status LED
└── Pin 8  → Buzzer

Ethernet Shield Pins (if used): 10, 50, 51, 52, 53
Serial Pins: 0-1 (USB), 14-19 (Serial1-3)
```

### Power Requirements
- **Arduino Mega:** 5V via USB or 7-12V external
- **Servo Motor:** 4.8-6V (can use Arduino 5V)
- **Ethernet Shield:** 5V (powered by Arduino)

## Troubleshooting

### Common Issues

1. **Servo Not Moving:**
   - Check power connections (5V, GND)
   - Verify signal wire on PWM pin (Pin 9)
   - Test with simple servo sweep code

2. **Ethernet Not Connecting:**
   - Check Ethernet cable and network settings
   - Verify IP address configuration
   - Ensure shield is properly mounted

3. **Serial Communication Issues:**
   - Check baud rate (115200)
   - Verify correct COM port selection
   - Ensure no other applications using the port

4. **Power Issues:**
   - Use external power for servo if drawing too much current
   - Check all GND connections
   - Verify voltage levels with multimeter

### LED Status Indicators
- **Built-in LED (Pin 13):** Always on = Arduino powered
- **Status LED (Pin 7):** On = Communication ready
- **LED Blinking:** Various system states

### Serial Debug Output
Monitor the Serial output for debugging:
```
=== Arduino Mega 2560 Gate Controller ===
✓ Servo initialized on pin 9
✓ Pins initialized
✓ Serial communication mode
🚪 Gate controller ready!
```

## Advanced Configuration

### Custom Pin Assignment
Modify these constants for different pin configurations:
```cpp
const int servoPin = 9;       // Change servo pin
const int ledPin = 13;        // Built-in LED
const int buzzerPin = 8;      // Buzzer pin
const int statusLedPin = 7;   // Status LED pin
```

### Network Settings (Ethernet)
```cpp
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);    // Static IP
// OR use DHCP: Ethernet.begin(mac);
```

### Auto-close Timing
```cpp
const unsigned long AUTO_CLOSE_TIME = 10000; // 10 seconds
```

## Support

For additional help:
1. Check Arduino IDE Serial Monitor for debug output
2. Verify all hardware connections match the pinout
3. Test each component individually before integration
4. Ensure proper power supply for all components

---
**Note:** This setup is specifically optimized for Arduino Mega 2560. Pin assignments and capabilities may differ from ESP32 or other Arduino models.