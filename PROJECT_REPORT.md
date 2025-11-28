# License Plate Detection System
## Project Report

---

## 1. Introduction

### 1.1 Background
The License Plate Detection System is an AI-powered web application designed to automatically detect and recognize vehicle license plates from video footage. The system serves as a comprehensive solution for vehicle access control, enabling organizations to manage authorized vehicles and monitor access attempts efficiently.

### 1.2 Objectives
- Develop an automated license plate detection system using AI/OCR technology
- Create a user-friendly web interface for vehicle management
- Implement role-based access control (Admin/User)
- Provide real-time video processing and detection capabilities
- Generate comprehensive reports and statistics for access monitoring

### 1.3 Scope
The system supports both Thai and international license plate formats, processes video files automatically, and maintains a database of registered vehicles with detailed access logs and statistics.

---

## 2. System Architecture

### 2.1 Technology Stack

**Backend Framework:**
- Django 5.2.6 - Web framework
- Python 3.13.5 - Programming language

**AI/Computer Vision:**
- EasyOCR 1.7.0+ - OCR engine (Thai/English support)
- OpenCV 4.8.0+ - Image processing
- NumPy 1.24.0+ - Numerical computing
- Keras/TensorFlow (Optional) - Vehicle type classification

**Database:**
- SQLite - Development
- PostgreSQL - Production

**Frontend:**
- Bootstrap 5 - UI framework
- HTML/CSS/JavaScript

**Deployment:**
- Gunicorn - WSGI server
- WhiteNoise - Static files serving
- Render.com - Cloud hosting

### 2.2 System Components

#### 2.2.1 Django Applications

**Authentication App (`authentication/`)**
- User registration and login
- Profile management
- Session handling
- AJAX validation

**Vehicle Control App (`vehicle_control/`)**
- License plate registration
- Video upload and processing
- License plate detection engine
- Known/Unknown plate categorization
- Access history management

**Dashboard App (`dashboard/`)**
- User dashboard
- Admin dashboard with statistics
- Recent activity display
- Analytics and reporting

#### 2.2.2 Core Detection Engine

**AdvancedLicensePlateDetector Class**
- Multi-method detection (Direct OCR + Contour-based)
- Image preprocessing (CLAHE, bilateral filtering, morphological operations)
- Pattern validation (Thai and international formats)
- Confidence scoring (threshold: 0.6)
- Lazy loading for performance optimization

---

## 3. System Features

### 3.1 User Features

**License Plate Registration:**
- Register license plates with images
- Store vehicle information (type, brand, model, color)
- Owner details management
- View registered plates

**Detection History:**
- View personal detection history
- Access detection images
- Check confidence scores

### 3.2 Admin Features

**Video Processing:**
- Upload video files (MP4, AVI, MOV)
- Automatic frame-by-frame processing
- Real-time progress tracking
- Batch detection processing

**Vehicle Management:**
- View all registered plates
- Manage authorized vehicles
- Categorize Known/Unknown plates
- Access detailed detection information

**Analytics & Reporting:**
- Total registered plates
- Detection statistics
- Access logs and timeline
- Recent activity monitoring
- Top detected vehicles

### 3.3 Detection Capabilities

**Multi-format Support:**
- Thai license plates (Thai characters + numbers)
- International formats (alphanumeric)
- Pattern validation
- Confidence scoring

**Processing Methods:**
- Direct OCR on preprocessed images
- Contour-based region detection
- Multiple preprocessing techniques
- Best result selection

---

## 4. Database Design

### 4.1 Data Models

**UserProfile**
- Extended user information
- Phone number and address

**RegisteredLicensePlate**
- Plate number, image, owner information
- Vehicle details (type, brand, model, color)
- Registration timestamp

**VideoDetection**
- Video file reference
- Processing status (processing/completed/error)
- Upload and processing timestamps

**KnownLicensePlate**
- Detected plates matching registered database
- Confidence score, detection image
- Frame number and timestamp

**UnknownLicensePlate**
- Detected plates not in database
- Vehicle type prediction
- Detection metadata

### 4.2 Relationships
- User → RegisteredLicensePlate (One-to-Many)
- VideoDetection → KnownLicensePlate (One-to-Many)
- VideoDetection → UnknownLicensePlate (One-to-Many)
- RegisteredLicensePlate → KnownLicensePlate (One-to-Many)

---

## 5. Implementation Details

### 5.1 Detection Algorithm

**Step 1: Image Preprocessing**
- Convert to grayscale
- Apply bilateral filter (noise reduction)
- CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Morphological operations

**Step 2: Detection Methods**
- **Method 1:** Direct EasyOCR on preprocessed image
- **Method 2:** Contour-based region detection + OCR

**Step 3: Validation**
- Pattern matching (Thai/International formats)
- Confidence threshold check (≥0.6)
- Text cleaning and normalization

**Step 4: Result Selection**
- Compare results from both methods
- Select highest confidence result
- Return plate text, confidence, and bounding box

### 5.2 Video Processing

**Processing Flow:**
1. Admin uploads video file
2. System creates VideoDetection record (status: processing)
3. Video processed frame-by-frame (every 30th frame)
4. Each frame analyzed for license plates
5. Detected plates compared with registered database
6. Results saved as KnownLicensePlate or UnknownLicensePlate
7. Status updated to completed

**Performance Optimization:**
- Frame skipping (process every 30 frames)
- Lazy loading of EasyOCR model
- Thread-safe detector instance
- Efficient database queries

### 5.3 Security Features

- Role-based access control (Admin/User)
- CSRF protection
- Session management
- Password validation
- Secure file upload handling

---

## 6. User Interface

### 6.1 Design Principles
- Modern, responsive design
- Bootstrap 5 framework
- Mobile-friendly interface
- Intuitive navigation
- Real-time feedback

### 6.2 Key Pages

**Authentication:**
- Login page with remember me
- Registration with validation
- Profile management

**Dashboard:**
- User dashboard (personal statistics)
- Admin dashboard (comprehensive analytics)

**Vehicle Management:**
- Plate registration form
- My plates listing
- Video upload interface
- Detection history
- Admin plate management

---

## 7. Deployment

### 7.1 Production Environment
- **Platform:** Render.com
- **Database:** PostgreSQL
- **Web Server:** Gunicorn
- **Static Files:** WhiteNoise
- **Python Version:** 3.13.5

### 7.2 Configuration
- Environment variables for sensitive data
- Database URL configuration
- Static files collection
- Automatic migrations on deploy

### 7.3 Deployment Process
1. Code pushed to GitHub
2. Render auto-deploys on commit
3. Build command: Install dependencies + collectstatic
4. Pre-deploy: Run migrations
5. Start command: Launch Gunicorn server

---

## 8. Testing & Results

### 8.1 Detection Accuracy
- Supports Thai and English license plates
- Confidence threshold: 0.6
- Multiple detection methods for reliability
- Pattern validation for accuracy

### 8.2 Performance
- Frame skipping for faster processing
- Lazy loading reduces startup time
- Efficient database queries
- Optimized image processing

### 8.3 System Capabilities
- ✅ Automatic license plate detection
- ✅ Multi-format support (Thai/International)
- ✅ User and admin management
- ✅ Comprehensive reporting
- ✅ Video processing
- ✅ Access control system

---

## 9. Limitations & Future Improvements

### 9.1 Current Limitations
- Video processing is synchronous (may be slow for large files)
- No background task queue (Celery)
- No real-time video streaming
- Vehicle type detection requires optional Keras model
- Limited API endpoints for external integration

### 9.2 Future Enhancements
- Implement Celery for asynchronous video processing
- Add real-time video streaming support
- Develop REST API for external systems
- Enhance vehicle type detection accuracy
- Add mobile app support
- Implement cloud storage for media files
- Add email notifications
- Enhance analytics with charts and graphs

---

## 10. Conclusion

The License Plate Detection System successfully provides an automated solution for vehicle access control using AI-powered license plate recognition. The system offers:

- **Reliable Detection:** Multi-method approach ensures accurate results
- **User-Friendly Interface:** Modern, responsive design for easy use
- **Comprehensive Management:** Complete vehicle and access management
- **Scalable Architecture:** Ready for production deployment
- **Extensible Design:** Easy to add new features and improvements

The system demonstrates effective integration of AI/OCR technology with web application development, providing a practical solution for vehicle access control and monitoring.

---

## 11. References

### Technologies
- Django Documentation: https://docs.djangoproject.com/
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- OpenCV: https://opencv.org/
- Bootstrap: https://getbootstrap.com/

### Deployment
- Render.com Documentation: https://render.com/docs
- Gunicorn: https://gunicorn.org/
- PostgreSQL: https://www.postgresql.org/

---

## Appendix

### A. Project Structure
```
LicensePlate/
├── license_plate_system/          # Main Django Project
│   ├── authentication/            # Authentication App
│   ├── vehicle_control/           # Vehicle Control App
│   ├── dashboard/                 # Dashboard App
│   └── templates/                 # HTML Templates
├── requirements.txt               # Dependencies
└── render.yaml                    # Deployment Config
```

### B. Key Files
- `detection.py` - License plate detection engine
- `models.py` - Database models
- `views.py` - Business logic
- `settings.py` - Configuration

### C. Environment Variables
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `ALLOWED_HOSTS` - Allowed domains
- `DATABASE_URL` - Database connection string

---

**Report Version:** 1.0  
**Date:** 2024  
**Status:** Production Ready

