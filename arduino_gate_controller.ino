// Arduino Mega 2560 Gate Controller
// Choose communication method: ETHERNET or SERIAL
#define COMMUNICATION_METHOD SERIAL  // Options: ETHERNET, SERIAL

#if COMMUNICATION_METHOD == ETHERNET
  #include <SPI.h>
  #include <Ethernet.h>
  #include <ArduinoJson.h>
#endif

#include <Servo.h>

// Network settings for Ethernet (if using)
#if COMMUNICATION_METHOD == ETHERNET
  byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
  IPAddress ip(192, 168, 1, 177);  // Set your desired IP
  EthernetServer server(80);
#endif

// Servo setup - Using PWM capable pins on Mega 2560
Servo gateServo;
const int servoPin = 9;     // PWM pin for servo (pins 2-13, 44-46 on Mega)
const int ledPin = 13;      // Built-in LED pin on Mega 2560
const int buzzerPin = 8;    // Digital pin for buzzer
const int statusLedPin = 7; // Additional status LED

// Gate positions
const int GATE_CLOSED = 0;   // 0 degrees - gate closed
const int GATE_OPEN = 90;    // 90 degrees - gate open

// Gate state
bool gateIsOpen = false;
unsigned long gateOpenTime = 0;
const unsigned long AUTO_CLOSE_TIME = 10000; // Auto close after 10 seconds

// Communication protocol commands
#define CMD_OPEN_GATE "OPEN"
#define CMD_CLOSE_GATE "CLOSE"
#define CMD_STATUS "STATUS"
#define CMD_ACCESS "ACCESS"

void setup() {
  Serial.begin(115200);
  Serial.println("=== Arduino Mega 2560 Gate Controller ===");
  Serial.println("Initializing...");

  // Initialize servo
  gateServo.attach(servoPin);
  gateServo.write(GATE_CLOSED);
  Serial.println("✓ Servo initialized on pin " + String(servoPin));

  // Initialize pins
  pinMode(ledPin, OUTPUT);
  pinMode(statusLedPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  // Turn on built-in LED to show power
  digitalWrite(ledPin, HIGH);
  Serial.println("✓ Pins initialized");

#if COMMUNICATION_METHOD == ETHERNET
  // Initialize Ethernet
  Ethernet.begin(mac, ip);
  server.begin();
  Serial.println("✓ Ethernet initialized");
  Serial.print("IP address: ");
  Serial.println(Ethernet.localIP());
  digitalWrite(statusLedPin, HIGH); // Ethernet ready indicator
#else
  Serial.println("✓ Serial communication mode");
  Serial.println("Commands: OPEN, CLOSE, STATUS, ACCESS:plate:authorized");
  digitalWrite(statusLedPin, HIGH); // Serial ready indicator
#endif

  // Initial beep to indicate ready
  beep(2, 200);
  Serial.println("🚪 Gate controller ready!");
  Serial.println("=====================================");
}

void loop() {
#if COMMUNICATION_METHOD == ETHERNET
  handleEthernetClient();
#else
  handleSerialCommand();
#endif

  // Auto-close gate after timeout
  if (gateIsOpen && (millis() - gateOpenTime > AUTO_CLOSE_TIME)) {
    closeGate();
  }

  delay(10);
}

#if COMMUNICATION_METHOD == ETHERNET
void handleEthernetClient() {
  EthernetClient client = server.available();
  if (client) {
    Serial.println("New client connected");
    String currentLine = "";

    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n') {
          if (currentLine.length() == 0) {
            // Send HTTP response
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();
            client.println(generateStatusPage());
            break;
          } else {
            currentLine = "";
          }
        } else if (c != '\r') {
          currentLine += c;
        }

        // Handle API endpoints
        if (currentLine.endsWith("GET /api/status")) {
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type:application/json");
          client.println();
          client.println(getGateStatusJson());
        } else if (currentLine.endsWith("POST /api/open")) {
          String response = openGate();
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type:application/json");
          client.println();
          client.println(response);
        } else if (currentLine.endsWith("POST /api/close")) {
          String response = closeGate();
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type:application/json");
          client.println();
          client.println(response);
        }
      }
    }
    client.stop();
    Serial.println("Client disconnected");
  }
}
#endif

void handleSerialCommand() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.println("📨 Received: " + command);

    if (command == CMD_OPEN_GATE) {
      String response = openGate();
      Serial.println("📤 " + response);
    }
    else if (command == CMD_CLOSE_GATE) {
      String response = closeGate();
      Serial.println("📤 " + response);
    }
    else if (command == CMD_STATUS) {
      String response = getGateStatusJson();
      Serial.println("📤 " + response);
    }
    else if (command.startsWith(CMD_ACCESS)) {
      // Format: ACCESS:plate_number:1/0 (1=authorized, 0=denied)
      int firstColon = command.indexOf(':', 6);
      int secondColon = command.indexOf(':', firstColon + 1);

      if (firstColon > 0 && secondColon > 0) {
        String plateNumber = command.substring(firstColon + 1, secondColon);
        bool authorized = command.substring(secondColon + 1).toInt() == 1;

        Serial.println("🚗 Plate: " + plateNumber + " | Authorized: " + String(authorized));

        if (authorized) {
          String response = openGate();
          beep(1, 500); // Success beep
          Serial.println("📤 " + response);
        } else {
          beep(3, 200); // Denial beeps
          Serial.println("📤 {\"status\":\"denied\",\"message\":\"Access denied\"}");
        }
      } else {
        Serial.println("📤 ERROR: Invalid ACCESS command format. Use: ACCESS:plate:1/0");
      }
    }
    else {
      Serial.println("📤 ERROR: Unknown command. Available: OPEN, CLOSE, STATUS, ACCESS:plate:auth");
    }
  }
}


String openGate() {
  if (!gateIsOpen) {
    Serial.println("🚪 Opening gate...");
    gateServo.write(GATE_OPEN);
    gateIsOpen = true;
    gateOpenTime = millis();

    // Visual feedback
    digitalWrite(ledPin, LOW);
    delay(200);
    digitalWrite(ledPin, HIGH);

    return "{\"status\":\"opened\",\"message\":\"Gate opened successfully\",\"auto_close_in\":10}";
  } else {
    return "{\"status\":\"already_open\",\"message\":\"Gate is already open\"}";
  }
}

String closeGate() {
  if (gateIsOpen) {
    Serial.println("🔒 Closing gate...");
    gateServo.write(GATE_CLOSED);
    gateIsOpen = false;
    gateOpenTime = 0;

    return "{\"status\":\"closed\",\"message\":\"Gate closed successfully\"}";
  } else {
    return "{\"status\":\"already_closed\",\"message\":\"Gate is already closed\"}";
  }
}

String getGateStatusJson() {
  String response = "{";
  response += "\"gate_open\":" + String(gateIsOpen ? "true" : "false") + ",";
  response += "\"uptime\":" + String(millis() / 1000) + ",";
  response += "\"auto_close_time\":" + String(AUTO_CLOSE_TIME / 1000);

  if (gateIsOpen) {
    long timeRemaining = max(0L, (long)(AUTO_CLOSE_TIME - (millis() - gateOpenTime)) / 1000);
    response += ",\"time_remaining\":" + String(timeRemaining);
  }

#if COMMUNICATION_METHOD == ETHERNET
  response += ",\"communication\":\"ethernet\"";
  response += ",\"ip_address\":\"" + Ethernet.localIP().toString() + "\"";
#else
  response += ",\"communication\":\"serial\"";
#endif

  response += "}";
  return response;
}

String generateStatusPage() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Arduino Mega 2560 Gate Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { text-align: center; margin: 20px 0; }
        .open { color: #4CAF50; font-size: 24px; font-weight: bold; }
        .closed { color: #f44336; font-size: 24px; font-weight: bold; }
        button { background: #2196F3; color: white; border: none; padding: 15px 30px; margin: 10px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #1976D2; }
        .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
    <script>
        function sendCommand(command) {
            fetch('/api/' + command, { method: 'POST' })
                .then(response => response.text())
                .then(data => {
                    alert('Command sent: ' + command);
                    location.reload();
                })
                .catch(error => alert('Error: ' + error));
        }

        // Auto refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
    </script>
</head>
<body>
    <div class="container">
        <h1>🚪 Arduino Mega 2560 Gate Controller</h1>

        <div class="status">
            <p>Gate Status: <span class=")" + String(gateIsOpen ? "open\">🟢 OPEN" : "closed\">🔴 CLOSED") + R"(</span></p>
        </div>

        <div style="text-align: center;">
            <button onclick="sendCommand('open')">🚪 Open Gate</button>
            <button onclick="sendCommand('close')">🔒 Close Gate</button>
        </div>

        <div class="info">
            <h3>📡 Connection Info</h3>)";

#if COMMUNICATION_METHOD == ETHERNET
  html += R"(
            <p>IP Address: )" + Ethernet.localIP().toString() + R"(</p>
            <p>Communication: 🌐 Ethernet</p>)";
#else
  html += R"(
            <p>Communication: 📺 Serial</p>)";
#endif

  html += R"(
            <p>Uptime: )" + String(millis() / 1000) + R"( seconds</p>
        </div>

        <div class="info">
            <h3>🔧 Pin Configuration (Mega 2560)</h3>
            <p>Servo: Pin )" + String(servoPin) + R"(</p>
            <p>Built-in LED: Pin )" + String(ledPin) + R"(</p>
            <p>Status LED: Pin )" + String(statusLedPin) + R"(</p>
            <p>Buzzer: Pin )" + String(buzzerPin) + R"(</p>
        </div>

        <div class="info">
            <h3>🔧 API Endpoints</h3>
            <p><strong>GET</strong> /api/status - Get gate status</p>
            <p><strong>POST</strong> /api/open - Open gate</p>
            <p><strong>POST</strong> /api/close - Close gate</p>
        </div>
    </div>
</body>
</html>
  )";

  return html;
}

void beep(int times, int duration) {
  for (int i = 0; i < times; i++) {
    digitalWrite(buzzerPin, HIGH);
    delay(duration);
    digitalWrite(buzzerPin, LOW);
    if (i < times - 1) delay(100);
  }
}