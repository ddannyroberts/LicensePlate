# License Plate Detection System (Django)

An AI-powered license plate detection and recognition system built with Django.

## 🚀 Features

- **Video Upload & Processing**: Upload video files to detect license plates automatically
- **AI Detection**: Advanced OCR using EasyOCR for accurate license plate recognition (Thai/English)
- **Modern UI**: Beautiful Bootstrap-based interface with drag & drop functionality
- **User Management**: Role-based access (Admin/User)
- **Database Support**: SQLite for easy setup and portability
- **Real-time Processing**: Live video processing with progress indicators
- **Access Control System**: Automatic gate control based on authorized vehicles
- **Arduino Integration**: Support for Arduino Mega 2560 gate controller (Serial/Ethernet)
- **Comprehensive Logging**: Access logs, gate control logs, and system statistics

## 📁 Project Structure

```
LicensePlate/
├── license_plate_system/          # Main Django Project
│   ├── manage.py
│   ├── license_plate_system/      # Django Settings
│   │   ├── settings.py           # Main settings (includes Arduino config)
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── authentication/            # Authentication App
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── vehicle_control/           # Vehicle Control App
│   │   ├── models.py             # AuthorizedVehicle, AccessLog, etc.
│   │   ├── views.py              # Vehicle management, video processing
│   │   ├── detection.py          # License plate detection engine
│   │   ├── arduino_integration.py # Arduino communication
│   │   └── urls.py
│   ├── dashboard/                 # Dashboard App
│   │   ├── views.py
│   │   └── urls.py
│   └── templates/                 # Django Templates
│
├── arduino_gate_controller.ino   # Arduino Mega 2560 code
├── authorized_plates.json         # Sample authorized plates
├── keras_Model.h5                 # AI Model for Vehicle Detection (optional)
├── labels.txt                     # Vehicle Type Labels
└── requirements.txt               # Python dependencies
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Navigate to Django Project

```bash
cd license_plate_system
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Or use default credentials:
- Username: `admin`
- Password: `admin123` (create via Django admin or shell)

### 5. Run the Server

```bash
python manage.py runserver
```

### 6. Access the System

- Open: http://127.0.0.1:8000
- Admin Panel: http://127.0.0.1:8000/admin
- Default Admin: `admin` / `admin123` (if created)

## 🎯 How to Use

### 1. **Login/Register**

- Register a new account or use admin credentials
- Admin users can view all detections and manage authorized vehicles
- Regular users can upload videos and view their own detections

### 2. **Upload Video**

- Go to Dashboard → Upload Video
- Drag & drop video file (MP4, AVI, MOV)
- System will automatically detect license plates frame-by-frame
- View results in detection history

### 3. **Manage Authorized Vehicles** (Admin Only)

- Go to Vehicles → Authorized Vehicles
- Add new authorized license plates
- Set vehicle type, owner name, and access level
- System will automatically grant access to authorized vehicles

### 4. **View Access Logs** (Admin Only)

- Go to Vehicles → Access Logs
- View all access attempts (authorized/denied)
- Filter by date, plate number, or authorization status

### 5. **Arduino Gate Control** (Admin Only)

- Go to Vehicles → Arduino Control
- Test Arduino connection
- Manually open/close gate
- View gate status

## 🔧 Configuration

### Database

- **Default**: SQLite (`db.sqlite3`) - automatically created
- **Production**: Can be changed to PostgreSQL in `settings.py`

### File Storage

- **Videos**: `media/videos/`
- **Images**: `media/detections/`
- **Uploads**: `media/uploads/`

### AI Model

- **Vehicle Detection**: `keras_Model.h5` (optional - disable if not available)
- **OCR Engine**: EasyOCR with Thai/English support (downloads models on first run ~100MB)

### Arduino Configuration

Edit `license_plate_system/license_plate_system/settings.py`:

```python
# Arduino Mega 2560 Configuration
ARDUINO_COMMUNICATION = "SERIAL"  # Options: "ETHERNET", "SERIAL"
ARDUINO_IP = "192.168.1.177"  # For Ethernet
ARDUINO_PORT = 80  # For Ethernet
ARDUINO_SERIAL_PORT = "/dev/ttyUSB0"  # Linux/Mac: /dev/ttyUSB0, Windows: COM3
ARDUINO_BAUD_RATE = 115200
```

## 🔌 Arduino Setup

1. Upload `arduino_gate_controller.ino` to Arduino Mega 2560
2. Connect servo to pin 9
3. Configure communication method in Arduino code:
   - `#define COMMUNICATION_METHOD SERIAL` (for USB)
   - `#define COMMUNICATION_METHOD ETHERNET` (for Ethernet Shield)
4. Update Django settings to match Arduino configuration

## 📊 Key Features

### Detection Engine

- **Multi-method Detection**: Direct OCR + Contour-based detection
- **Advanced Preprocessing**: CLAHE, bilateral filtering, morphological operations
- **Pattern Validation**: Supports Thai and international license plate formats
- **Confidence Scoring**: Only accepts detections above threshold (0.6)

### Access Control

- **Automatic Authorization**: Checks against authorized vehicle database
- **Gate Control**: Automatically opens gate for authorized vehicles
- **Access Logging**: Records all access attempts with timestamps
- **Vehicle Status Tracking**: Tracks vehicles currently inside premises

### Admin Dashboard

- **Statistics**: Total vehicles, access attempts, authorized entries
- **Recent Activity**: Latest access logs and detections
- **Top Vehicles**: Most frequently accessed vehicles
- **System Analytics**: Comprehensive reporting and analytics

## 🔐 Default Credentials

**Admin Account**:
- Username: `admin`
- Password: `admin123` (create via `python manage.py createsuperuser`)

## 📝 Notes

- The AI vehicle detection model is optional (requires TensorFlow/Keras)
- EasyOCR will download models on first run (~100MB)
- Video processing may take time depending on file size
- For production, use proper WSGI server (Gunicorn, uWSGI) with Nginx
- Arduino integration is optional - system works without it

## 🛟 Troubleshooting

1. **Import Errors**: Make sure all dependencies are installed (`pip install -r requirements.txt`)
2. **No Detection**: Check video quality and license plate visibility
3. **Slow Processing**: Reduce video resolution or length
4. **Database Issues**: Delete `db.sqlite3` and run migrations again
5. **Arduino Connection**: Check serial port/network settings in `settings.py`

## 🎯 API Endpoints

### Vehicle Control
- `GET /vehicles/authorized/` - List authorized vehicles
- `POST /vehicles/add-vehicle/` - Add authorized vehicle
- `GET /vehicles/access-logs/` - View access logs
- `POST /vehicles/upload-video/` - Upload video for processing

### Arduino API
- `GET /vehicles/api/arduino/status/` - Get gate status
- `POST /vehicles/api/arduino/open-gate/` - Open gate
- `POST /vehicles/api/arduino/close-gate/` - Close gate
- `GET /vehicles/api/arduino/test-connection/` - Test Arduino connection

## 📚 Technologies Used

- **Backend**: Django 5.2+
- **Database**: SQLite (PostgreSQL for production)
- **Computer Vision**: OpenCV, EasyOCR
- **AI/ML**: Keras (optional - for vehicle classification)
- **Hardware**: Arduino Mega 2560
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript

## 🚀 Production Deployment

1. Set `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your domain
3. Use PostgreSQL instead of SQLite
4. Set up static files serving (WhiteNoise or Nginx)
5. Use Gunicorn/uWSGI with Nginx
6. Set up SSL/HTTPS
7. Configure proper secret key

---

**License**: This project is for educational purposes.
