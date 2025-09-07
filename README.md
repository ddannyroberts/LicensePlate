# License Plate Detection System

An AI-powered license plate detection and recognition system with both Flask and Django implementations.

## 🚀 Features

- **Video Upload & Processing**: Upload video files to detect license plates automatically
- **AI Detection**: Advanced OCR using EasyOCR for accurate license plate recognition
- **Modern UI**: Beautiful Bootstrap-based interface with drag & drop functionality
- **User Management**: Role-based access (Admin/User)
- **Database Support**: SQLite for easy setup and portability
- **Real-time Processing**: Live video processing with progress indicators

## 📁 Project Structure

```
license_plate_project_full_2/
├── app.py                      # Flask Application (Updated)
├── templates/                  # Flask Templates
│   ├── dashboard.html          # User Dashboard (Video Upload)
│   ├── admin_dashboard.html    # Admin Dashboard
│   ├── login.html             # Login Page
│   └── register.html          # Registration Page
├── static/                    # Static Files
│   ├── uploads/               # Uploaded images
│   └── videos/                # Uploaded videos
├── license_plate_django/      # Django Implementation
│   ├── manage.py
│   ├── license_plate_django/  # Django Settings
│   ├── plate_detector/        # Django App
│   └── templates/            # Django Templates
├── keras_Model.h5            # AI Model for Vehicle Detection
├── labels.txt               # Vehicle Type Labels
└── requirements.txt         # Dependencies
```

## 🛠️ Installation & Setup

### Flask Version (Recommended for simplicity)

1. **Install Dependencies**:
   ```bash
   pip install Flask Flask-SQLAlchemy opencv-python easyocr numpy Pillow
   ```

2. **Run the Application**:
   ```bash
   python3 app.py
   ```

3. **Access the System**:
   - Open: http://127.0.0.1:5000
   - **Admin Login**: `admin` / `admin123`
   - **Create User**: Register new account on login page

### Django Version (Full-featured)

1. **Navigate to Django Directory**:
   ```bash
   cd license_plate_django
   ```

2. **Install Dependencies**:
   ```bash
   pip install django opencv-python easyocr
   ```

3. **Run Migrations**:
   ```bash
   python3 manage.py migrate
   ```

4. **Run the Server**:
   ```bash
   python3 manage.py runserver
   ```

5. **Access the System**:
   - Open: http://127.0.0.1:8000
   - **Admin Login**: `admin` / `admin123`

## 🎯 How to Use

### 1. **Login/Register**
   - Register a new account or use admin credentials
   - Admin users can view all detections
   - Regular users can only see their own data

### 2. **Upload Video**
   - Go to Dashboard
   - Drag & drop video file (MP4, AVI, MOV)
   - Click "Start Processing"
   - Wait for AI to detect license plates

### 3. **Manual Entry**
   - Fill in vehicle information manually
   - Upload vehicle image (optional)
   - Save to database

### 4. **View Results**
   - Detection History table shows all processed data
   - Click on media links to view images/videos
   - Admin can see all users' data

## 🔧 Configuration

### Database
- **Flask**: Uses SQLite (`license_plate.db`) - automatically created
- **Django**: Uses SQLite (`db.sqlite3`) - created with migrations

### File Storage
- **Images**: `static/uploads/`
- **Videos**: `static/videos/`
- **Django Media**: `media/videos/` and `media/plates/`

### AI Model
- **Vehicle Detection**: `keras_Model.h5` (optional - disable if not available)
- **OCR Engine**: EasyOCR with Thai/English support

## 🎨 UI Features

- **Modern Design**: Bootstrap 5 with gradient backgrounds
- **Responsive**: Works on desktop and mobile
- **Interactive**: Drag & drop, progress bars, hover effects
- **English Interface**: All text in English
- **Professional**: Clean, modern appearance

## 📊 Key Improvements

### From Original Version:
- ✅ **MySQL → SQLite**: Easier setup, no external database required
- ✅ **Camera → Video Upload**: More practical file-based processing
- ✅ **Enhanced OCR**: Better image preprocessing and accuracy
- ✅ **Modern UI**: Professional Bootstrap interface
- ✅ **English Language**: Full English interface
- ✅ **Django Version**: Complete MVC framework implementation

### New Features:
- ✅ **Video Processing**: Frame-by-frame license plate detection
- ✅ **Progress Indicators**: Real-time processing feedback
- ✅ **File Management**: Organized storage of media files
- ✅ **Enhanced Detection**: Better regex patterns for license plates
- ✅ **Admin Dashboard**: Comprehensive management interface

## 🔐 Default Credentials

**Admin Account (Both Systems)**:
- Username: `admin`
- Password: `admin123`

## 📝 Notes

- The AI vehicle detection model is optional (requires TensorFlow/Keras)
- EasyOCR will download models on first run (~100MB)
- Video processing may take time depending on file size
- For production, use proper WSGI server (not Flask development server)

## 🛟 Troubleshooting

1. **Import Errors**: Make sure all dependencies are installed
2. **No Detection**: Check video quality and license plate visibility
3. **Slow Processing**: Reduce video resolution or length
4. **Database Issues**: Delete `.db` files to reset

## 🎯 Both Systems Ready!

You now have **two complete systems**:
- **Flask**: Simple, fast, SQLite-based
- **Django**: Full-featured, admin panel, ORM

Choose the one that best fits your needs! 🚀# ProjectYear3
