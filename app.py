# === app.py ===
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import easyocr
from datetime import datetime
import json
from functools import wraps

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///license_plate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['VIDEO_FOLDER'] = 'static/videos/'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size

db = SQLAlchemy(app)

# Import advanced detection system
import re
import threading
import time
from typing import List, Tuple, Optional, Dict
from difflib import SequenceMatcher

class AdvancedLicensePlateDetector:
    def __init__(self):
        self.reader = easyocr.Reader(['th', 'en'])
        self.confidence_threshold = 0.6
        self.min_area = 1000
        self.aspect_ratio_range = (2, 8)
        
        # Thai license plate patterns
        self.thai_patterns = [
            r'^[\u0E01-\u0E5B]{1,3}\s*\d{1,4}$',  # Thai chars + numbers
            r'^\d{1,3}[\u0E01-\u0E5B]{1,3}\d{1,4}$',  # Num + Thai + Num
            r'^[\u0E01-\u0E5B]{2}\s*\d{4}$',  # 2 Thai + 4 digits
        ]
        
        # International patterns
        self.intl_patterns = [
            r'^[A-Z]{2,3}\s*\d{3,4}$',  # AA 123, ABC 1234
            r'^\d{1,3}[A-Z]{1,3}\d{1,4}$',  # 1A23, 12AB34
            r'^[A-Z0-9]{5,8}$',  # General alphanumeric
        ]
        
        # Vehicle type model
        self.vehicle_model = None
        self.class_names = []
        self.load_vehicle_model()

    def load_vehicle_model(self):
        try:
            from keras.models import load_model
            if os.path.exists("keras_Model.h5") and os.path.exists("labels.txt"):
                self.vehicle_model = load_model("keras_Model.h5", compile=False)
                with open("labels.txt", "r") as f:
                    self.class_names = f.readlines()
        except ImportError:
            print("Keras not installed, vehicle type detection disabled")
            self.vehicle_model = None

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Advanced image preprocessing for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(filtered)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        return morph

    def detect_license_plate_contours(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect license plate regions using contour detection"""
        gray = self.preprocess_image(image)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        plate_candidates = []
        
        for contour in contours:
            # Calculate area and bounding rectangle
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Check if it matches license plate dimensions
            if (self.aspect_ratio_range[0] <= aspect_ratio <= self.aspect_ratio_range[1] and
                w > 100 and h > 20):
                plate_candidates.append((x, y, w, h))
        
        return plate_candidates

    def extract_text_from_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Tuple[str, float]:
        """Extract text from a specific region using multiple methods"""
        x, y, w, h = region
        
        # Add padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        roi = image[y:y+h, x:x+w]
        
        if roi.size == 0:
            return "", 0.0
        
        # Resize for better OCR
        if w < 200:
            scale_factor = 200 / w
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Try multiple preprocessing methods
        methods = [
            roi,  # Original
            self.preprocess_image(roi),  # Enhanced
            cv2.threshold(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), 0, 255, 
                         cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # Otsu threshold
        ]
        
        best_text = ""
        best_confidence = 0.0
        
        for processed_roi in methods:
            try:
                results = self.reader.readtext(processed_roi)
                for (bbox, text, conf) in results:
                    if conf > best_confidence and len(text.strip()) >= 4:
                        candidate_text = self.clean_text(text)
                        if self.validate_license_plate(candidate_text):
                            best_text = candidate_text
                            best_confidence = conf
            except Exception as e:
                continue
        
        return best_text, best_confidence

    def clean_text(self, text: str) -> str:
        """Clean and standardize extracted text"""
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^\u0E01-\u0E5BA-Z0-9\s]', '', text.upper())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Common OCR error corrections
        corrections = {
            'O': '0', 'I': '1', 'S': '5', 'Z': '2',
            'G': '6', 'B': '8', 'Q': '0'
        }
        
        for wrong, correct in corrections.items():
            cleaned = cleaned.replace(wrong, correct)
        
        return cleaned

    def validate_license_plate(self, text: str) -> bool:
        """Validate if text matches license plate patterns"""
        if len(text) < 4 or len(text) > 10:
            return False
        
        # Check against all patterns
        all_patterns = self.thai_patterns + self.intl_patterns
        
        for pattern in all_patterns:
            if re.match(pattern, text):
                return True
        
        # Additional heuristic checks
        has_letter = bool(re.search(r'[A-Z\u0E01-\u0E5B]', text))
        has_number = bool(re.search(r'\d', text))
        
        return has_letter and has_number

    def detect_license_plate(self, image: np.ndarray) -> Tuple[str, float, Tuple[int, int, int, int]]:
        """Main detection method combining multiple approaches"""
        best_text = ""
        best_confidence = 0.0
        best_region = None
        
        # Method 1: Direct EasyOCR on preprocessed image
        preprocessed = self.preprocess_image(image)
        try:
            results = self.reader.readtext(preprocessed)
            for (bbox, text, conf) in results:
                if conf > self.confidence_threshold:
                    candidate_text = self.clean_text(text)
                    if self.validate_license_plate(candidate_text) and conf > best_confidence:
                        best_text = candidate_text
                        best_confidence = conf
                        # Calculate bounding box
                        points = np.array(bbox, dtype=np.int32)
                        x, y, w, h = cv2.boundingRect(points)
                        best_region = (x, y, w, h)
        except Exception as e:
            pass
        
        # Method 2: Contour-based detection
        plate_candidates = self.detect_license_plate_contours(image)
        
        for region in plate_candidates:
            text, conf = self.extract_text_from_region(image, region)
            if conf > best_confidence and conf > self.confidence_threshold:
                best_text = text
                best_confidence = conf
                best_region = region
        
        return best_text, best_confidence, best_region
    
    def detect_plate_and_crop(self, image):
        """Legacy method for compatibility"""
        plate_text, confidence, region = self.detect_license_plate(image)
        
        if plate_text and region:
            x, y, w, h = region
            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            crop = image[y:y+h, x:x+w]
            return plate_text, crop
        
        return "UNKNOWN", None
    
    def predict_vehicle_type(self, image):
        """Predict vehicle type using the trained model"""
        if self.vehicle_model is None:
            return "Unknown"
        
        try:
            resized = cv2.resize(image, (224, 224))
            image_np = np.asarray(resized, dtype=np.float32).reshape(1, 224, 224, 3)
            image_np = (image_np / 127.5) - 1
            
            prediction = self.vehicle_model.predict(image_np, verbose=0)
            index = np.argmax(prediction)
            
            if index < len(self.class_names):
                vehicle_type = self.class_names[index].strip().split()[-1]
                confidence = float(prediction[0][index])
                return vehicle_type if confidence > 0.5 else "Unknown"
            
        except Exception as e:
            print(f"Error in vehicle type prediction: {e}")
        
        return "Unknown"
    
    def process_video_file(self, video_path):
        """Process entire video file and extract license plates"""
        cap = cv2.VideoCapture(video_path)
        results = []
        frame_count = 0
        
        frame_skip = 30  # Process every 30th frame
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                h, w = frame.shape[:2]
                plate_area = frame[int(h * 0.6):, :]
                
                plate_text, plate_crop = self.detect_plate_and_crop(plate_area)
                vehicle_type = self.predict_vehicle_type(frame)
                
                if plate_text != "UNKNOWN":
                    result = {
                        'plate_text': plate_text,
                        'plate_crop': plate_crop,
                        'vehicle_type': vehicle_type,
                        'timestamp': frame_count / cap.get(cv2.CAP_PROP_FPS)
                    }
                    results.append(result)
            
            frame_count += 1
        
        cap.release()
        return results


class AccessControlSystem:
    def __init__(self, authorized_plates_file: str = "authorized_plates.json"):
        self.authorized_plates = self.load_authorized_plates(authorized_plates_file)
        self.access_log = []
        self.gate_status = "CLOSED"
        self.detector = AdvancedLicensePlateDetector()
        
    def load_authorized_plates(self, filename: str) -> Dict[str, Dict]:
        """Load authorized license plates from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default authorized plates file
            default_plates = {
                "ABC123": {
                    "owner": "John Doe",
                    "vehicle_type": "Car",
                    "access_level": "full",
                    "registered_date": "2024-01-01"
                },
                "XYZ789": {
                    "owner": "Jane Smith", 
                    "vehicle_type": "SUV",
                    "access_level": "full",
                    "registered_date": "2024-01-02"
                }
            }
            self.save_authorized_plates(filename, default_plates)
            return default_plates
    
    def save_authorized_plates(self, filename: str, plates: Dict[str, Dict]):
        """Save authorized plates to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plates, f, ensure_ascii=False, indent=2)
    
    def add_authorized_plate(self, plate_number: str, owner: str, vehicle_type: str = "Car", access_level: str = "full"):
        """Add a new authorized plate"""
        self.authorized_plates[plate_number] = {
            "owner": owner,
            "vehicle_type": vehicle_type,
            "access_level": access_level,
            "registered_date": datetime.now().strftime("%Y-%m-%d")
        }
        self.save_authorized_plates("authorized_plates.json", self.authorized_plates)
    
    def is_authorized(self, plate_number: str) -> bool:
        """Check if a license plate is authorized"""
        # Normalize plate number for comparison
        normalized_plate = re.sub(r'\s+', '', plate_number.upper())
        
        # Check exact match first
        if normalized_plate in self.authorized_plates:
            return True
        
        # Check similar plates (handle OCR errors)
        for authorized_plate in self.authorized_plates.keys():
            if self.plates_similar(normalized_plate, authorized_plate):
                return True
        
        return False
    
    def plates_similar(self, plate1: str, plate2: str, threshold: float = 0.8) -> bool:
        """Check if two plates are similar (handle OCR errors)"""
        similarity = SequenceMatcher(None, plate1, plate2).ratio()
        return similarity >= threshold
    
    def log_access_attempt(self, plate_number: str, authorized: bool, confidence: float):
        """Log access attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "plate_number": plate_number,
            "authorized": authorized,
            "confidence": confidence,
            "gate_action": "OPENED" if authorized else "DENIED"
        }
        self.access_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]
        
        # Save to file
        self.save_access_log()
    
    def save_access_log(self):
        """Save access log to file"""
        with open("access_log.json", 'w', encoding='utf-8') as f:
            json.dump(self.access_log, f, ensure_ascii=False, indent=2)
    
    def control_gate(self, action: str):
        """Control gate/door (simulate hardware control)"""
        if action == "OPEN":
            print(f"🚪 GATE OPENING... ({datetime.now().strftime('%H:%M:%S')})")
            self.gate_status = "OPENING"
            
            # Simulate gate opening time
            time.sleep(2)
            
            self.gate_status = "OPEN"
            print(f"✅ GATE OPENED ({datetime.now().strftime('%H:%M:%S')})")
            
            # Auto-close after 10 seconds
            threading.Timer(10.0, self.auto_close_gate).start()
            
        elif action == "CLOSE":
            print(f"🚪 GATE CLOSING... ({datetime.now().strftime('%H:%M:%S')})")
            self.gate_status = "CLOSING"
            time.sleep(2)
            self.gate_status = "CLOSED"
            print(f"🔒 GATE CLOSED ({datetime.now().strftime('%H:%M:%S')})")
    
    def auto_close_gate(self):
        """Automatically close the gate"""
        if self.gate_status == "OPEN":
            self.control_gate("CLOSE")
    
    def process_vehicle(self, image: np.ndarray) -> Dict:
        """Process vehicle and control access"""
        # Detect license plate
        plate_text, confidence, region = self.detector.detect_license_plate(image)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "plate_detected": plate_text,
            "confidence": confidence,
            "region": region,
            "authorized": False,
            "gate_action": "DENIED",
            "owner_info": None
        }
        
        if plate_text and confidence > 0.6:
            # Check authorization
            is_auth = self.is_authorized(plate_text)
            result["authorized"] = is_auth
            
            if is_auth:
                # Get owner info
                normalized_plate = re.sub(r'\s+', '', plate_text.upper())
                owner_info = self.authorized_plates.get(normalized_plate)
                result["owner_info"] = owner_info
                result["gate_action"] = "OPENED"
                
                # Open gate
                threading.Thread(target=self.control_gate, args=("OPEN",)).start()
                
                print(f"✅ ACCESS GRANTED")
                print(f"   Plate: {plate_text}")
                print(f"   Owner: {owner_info.get('owner', 'Unknown') if owner_info else 'Unknown'}")
                print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ ACCESS DENIED")
                print(f"   Plate: {plate_text}")
                print(f"   Reason: Not authorized")
                print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log the attempt
            self.log_access_attempt(plate_text, is_auth, confidence)
        else:
            print(f"⚠️  NO PLATE DETECTED")
            print(f"   Confidence too low: {confidence:.2f}")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return result

# Initialize systems
detector = AdvancedLicensePlateDetector()
access_control = AccessControlSystem()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class VehicleLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plate_text = db.Column(db.String(100))
    vendor = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(100))
    province = db.Column(db.String(100))
    category = db.Column(db.String(100))
    image_filename = db.Column(db.String(100))
    video_filename = db.Column(db.String(100))
    status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuthorizedVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(50), default="Car")
    access_level = db.Column(db.String(20), default="full")
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False)
    authorized = db.Column(db.Boolean, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    gate_action = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    owner_info = db.Column(db.Text)  # JSON string
    entry_type = db.Column(db.String(10), default="ENTRY")  # ENTRY or EXIT

class VehicleStatus(db.Model):
    """Track current status of vehicles in the premises"""
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False, unique=True)
    status = db.Column(db.String(10), nullable=False)  # INSIDE, OUTSIDE
    entry_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # Duration in minutes
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    owner_info = db.Column(db.Text)
    
class SystemStats(db.Model):
    """System statistics for dashboard"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    total_entries = db.Column(db.Integer, default=0)
    total_exits = db.Column(db.Integer, default=0)
    authorized_entries = db.Column(db.Integer, default=0)
    unauthorized_attempts = db.Column(db.Integer, default=0)
    vehicles_inside = db.Column(db.Integer, default=0)
    peak_occupancy = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/admin_camera")
def admin_camera():
    return render_template("admin_camera.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, password_hash=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('dynamic_register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('dynamic_login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Handle video upload
        if 'video' in request.files and request.files['video'].filename:
            return handle_video_upload()
        
        # Handle manual form submission
        plate_text = request.form.get('plate_text', '')
        province = request.form.get('province', '')
        brand = request.form.get('brand', '')
        model = request.form.get('model', '')
        category = request.form.get('category', '')
        image = request.files.get('image')
        
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_log = VehicleLog(
                user_id=session['user_id'],
                plate_text=plate_text,
                vendor=brand,
                model=model,
                color='-',
                province=province,
                category=category,
                image_filename=filename,
                status='entry'
            )
            db.session.add(new_log)
            db.session.commit()
            flash('Vehicle submitted successfully!')
    
    plates = VehicleLog.query.filter_by(user_id=session['user_id']).order_by(VehicleLog.timestamp.desc()).all()
    return render_template('dynamic_dashboard.html', plates=plates, username=session['username'])

def handle_video_upload():
    """Handle video file upload and processing"""
    video_file = request.files['video']
    if not video_file or not video_file.filename:
        flash('No video file selected')
        return redirect(url_for('dashboard'))
    
    # Save video file
    filename = secure_filename(video_file.filename)
    video_path = os.path.join(app.config['VIDEO_FOLDER'], filename)
    video_file.save(video_path)
    
    # Process video for license plate detection with access control
    cap = cv2.VideoCapture(video_path)
    results = []
    frame_count = 0
    frame_skip = 30
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_skip == 0:
            # Use access control system to process the frame
            access_result = access_control.process_vehicle(frame)
            
            if access_result['plate_detected'] and access_result['confidence'] > 0.6:
                # Save the cropped plate image
                crop_filename = None
                if access_result['region']:
                    x, y, w, h = access_result['region']
                    padding = 10
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(frame.shape[1] - x, w + 2 * padding)
                    h = min(frame.shape[0] - y, h + 2 * padding)
                    crop = frame[y:y+h, x:x+w]
                    
                    crop_filename = f"plate_{session['user_id']}_{frame_count}_{access_result['confidence']:.2f}.jpg"
                    crop_path = os.path.join(app.config['UPLOAD_FOLDER'], crop_filename)
                    cv2.imwrite(crop_path, crop)
                
                # Save to vehicle log
                new_log = VehicleLog(
                    user_id=session['user_id'],
                    plate_text=access_result['plate_detected'],
                    vendor=detector.predict_vehicle_type(frame),
                    video_filename=filename,
                    image_filename=crop_filename,
                    status='authorized' if access_result['authorized'] else 'unauthorized'
                )
                db.session.add(new_log)
                
                # Save to access log
                access_log = AccessLog(
                    plate_number=access_result['plate_detected'],
                    authorized=access_result['authorized'],
                    confidence=access_result['confidence'],
                    gate_action=access_result['gate_action'],
                    owner_info=json.dumps(access_result['owner_info']) if access_result['owner_info'] else None
                )
                db.session.add(access_log)
                
                results.append(access_result)
        
        frame_count += 1
    
    cap.release()
    
    db.session.commit()
    flash(f'Video processed successfully! Found {len(results)} license plates.')
    return redirect(url_for('dashboard'))

@app.route('/process-video', methods=['POST'])
def process_video():
    """AJAX endpoint for video processing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        video_file = request.files['video']
        if not video_file or not video_file.filename:
            return jsonify({'error': 'No video file'}), 400
        
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['VIDEO_FOLDER'], filename)
        video_file.save(video_path)
        
        results = detector.process_video_file(video_path)
        
        processed_results = []
        for i, result in enumerate(results):
            if result['plate_text'] != 'UNKNOWN':
                crop_filename = None
                if result['plate_crop'] is not None:
                    crop_filename = f"plate_{session['user_id']}_{i}_{result['timestamp']:.1f}.jpg"
                    crop_path = os.path.join(app.config['UPLOAD_FOLDER'], crop_filename)
                    cv2.imwrite(crop_path, result['plate_crop'])
                
                log_entry = VehicleLog(
                    user_id=session['user_id'],
                    plate_text=result['plate_text'],
                    vendor=result['vehicle_type'],
                    video_filename=filename,
                    image_filename=crop_filename,
                    status='unknown'
                )
                db.session.add(log_entry)
                
                processed_results.append({
                    'plate_text': result['plate_text'],
                    'vehicle_type': result['vehicle_type'],
                    'timestamp': result['timestamp'],
                    'id': log_entry.id
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Video processed successfully! Found {len(processed_results)} license plates.',
            'results': processed_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    plates = VehicleLog.query.order_by(VehicleLog.timestamp.desc()).all()
    access_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(50).all()
    authorized_vehicles = AuthorizedVehicle.query.filter_by(is_active=True).all()
    
    # Get today's stats
    today = datetime.utcnow().date()
    stats = SystemStats.query.filter_by(date=today).first()
    if not stats:
        stats = SystemStats(date=today)
        db.session.add(stats)
        db.session.commit()
    
    # Get vehicles currently inside
    vehicles_inside = VehicleStatus.query.filter_by(status="INSIDE").all()
    
    return render_template('enhanced_admin_dashboard.html', 
                         plates=plates, 
                         access_logs=access_logs, 
                         authorized_vehicles=authorized_vehicles,
                         stats=stats,
                         vehicles_inside=vehicles_inside)

@app.route('/admin/authorized-vehicles', methods=['GET', 'POST'])
def manage_authorized_vehicles():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        plate_number = request.form.get('plate_number', '').upper().replace(' ', '')
        owner_name = request.form.get('owner_name', '')
        vehicle_type = request.form.get('vehicle_type', 'Car')
        access_level = request.form.get('access_level', 'full')
        
        if plate_number and owner_name:
            # Check if already exists
            existing = AuthorizedVehicle.query.filter_by(plate_number=plate_number).first()
            if existing:
                flash('Vehicle already authorized!')
            else:
                new_vehicle = AuthorizedVehicle(
                    plate_number=plate_number,
                    owner_name=owner_name,
                    vehicle_type=vehicle_type,
                    access_level=access_level
                )
                db.session.add(new_vehicle)
                
                # Also add to access control system
                access_control.add_authorized_plate(plate_number, owner_name, vehicle_type, access_level)
                
                db.session.commit()
                flash('Vehicle authorized successfully!')
        else:
            flash('Please fill all required fields')
    
    authorized_vehicles = AuthorizedVehicle.query.filter_by(is_active=True).order_by(AuthorizedVehicle.registered_date.desc()).all()
    return render_template('authorized_vehicles.html', vehicles=authorized_vehicles)

@app.route('/admin/access-logs')
def view_access_logs():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False)
    
    return render_template('access_logs.html', logs=logs)

@app.route('/admin/remove-vehicle/<int:vehicle_id>', methods=['POST'])
def remove_authorized_vehicle(vehicle_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    vehicle = AuthorizedVehicle.query.get_or_404(vehicle_id)
    vehicle.is_active = False
    db.session.commit()
    flash('Vehicle removed from authorized list')
    return redirect(url_for('manage_authorized_vehicles'))

@app.route('/test-gate-control', methods=['POST'])
def test_gate_control():
    """Test endpoint for gate control - for testing purposes"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    # Simulate a detected license plate for testing
    test_plate = request.form.get('test_plate', 'ABC123')
    
    # Create a dummy image for testing
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Check if plate is authorized and simulate gate control
    is_authorized = False
    authorized_vehicles = AuthorizedVehicle.query.filter_by(is_active=True).all()
    
    for vehicle in authorized_vehicles:
        if vehicle.plate_number == test_plate:
            is_authorized = True
            break
    
    # Log the test attempt
    log_entry = AccessLog(
        plate_number=test_plate,
        authorized=is_authorized,
        confidence=0.95,  # High confidence for test
        gate_action="OPENED" if is_authorized else "DENIED"
    )
    db.session.add(log_entry)
    db.session.commit()
    
    if is_authorized:
        # Simulate gate opening
        flash(f'✅ ACCESS GRANTED for {test_plate} - Gate Opening!')
        print(f"🚪 TEST: Gate opening for authorized vehicle {test_plate}")
    else:
        flash(f'❌ ACCESS DENIED for {test_plate} - Not authorized')
        print(f"❌ TEST: Access denied for unauthorized vehicle {test_plate}")
    
    return redirect(url_for('admin_dashboard'))

def update_vehicle_status(plate_number: str, entry_type: str, authorized: bool, owner_info: str = None):
    """Update vehicle entry/exit status"""
    vehicle_status = VehicleStatus.query.filter_by(plate_number=plate_number).first()
    
    if entry_type == "ENTRY" and authorized:
        if not vehicle_status:
            # New vehicle entry
            vehicle_status = VehicleStatus(
                plate_number=plate_number,
                status="INSIDE",
                entry_time=datetime.utcnow(),
                owner_info=owner_info
            )
            db.session.add(vehicle_status)
        else:
            # Update existing vehicle
            vehicle_status.status = "INSIDE"
            vehicle_status.entry_time = datetime.utcnow()
            vehicle_status.exit_time = None
            vehicle_status.last_updated = datetime.utcnow()
            
    elif entry_type == "EXIT" and vehicle_status:
        # Vehicle exit
        vehicle_status.status = "OUTSIDE"
        vehicle_status.exit_time = datetime.utcnow()
        vehicle_status.last_updated = datetime.utcnow()
        
        # Calculate duration
        if vehicle_status.entry_time:
            duration = (vehicle_status.exit_time - vehicle_status.entry_time).total_seconds() / 60
            vehicle_status.duration = int(duration)
    
    # Update system stats
    today = datetime.utcnow().date()
    stats = SystemStats.query.filter_by(date=today).first()
    if not stats:
        stats = SystemStats(date=today)
        db.session.add(stats)
    
    if entry_type == "ENTRY":
        stats.total_entries += 1
        if authorized:
            stats.authorized_entries += 1
        else:
            stats.unauthorized_attempts += 1
    elif entry_type == "EXIT":
        stats.total_exits += 1
    
    # Update current occupancy
    current_inside = VehicleStatus.query.filter_by(status="INSIDE").count()
    stats.vehicles_inside = current_inside
    if current_inside > stats.peak_occupancy:
        stats.peak_occupancy = current_inside
        
    stats.last_updated = datetime.utcnow()
    db.session.commit()

@app.route('/api/vehicle_status')
@login_required
def api_vehicle_status():
    """API endpoint for real-time vehicle status"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
        
    vehicles_inside = VehicleStatus.query.filter_by(status="INSIDE").all()
    recent_activity = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(5).all()
    
    today = datetime.utcnow().date()
    stats = SystemStats.query.filter_by(date=today).first()
    
    return jsonify({
        'vehicles_inside': [{
            'plate_number': v.plate_number,
            'entry_time': v.entry_time.isoformat() if v.entry_time else None,
            'duration_minutes': v.duration or 0,
            'owner_info': json.loads(v.owner_info) if v.owner_info else None
        } for v in vehicles_inside],
        'recent_activity': [{
            'plate_number': log.plate_number,
            'entry_type': log.entry_type,
            'authorized': log.authorized,
            'timestamp': log.timestamp.isoformat(),
            'gate_action': log.gate_action
        } for log in recent_activity],
        'stats': {
            'total_entries': stats.total_entries if stats else 0,
            'total_exits': stats.total_exits if stats else 0,
            'vehicles_inside': stats.vehicles_inside if stats else 0,
            'peak_occupancy': stats.peak_occupancy if stats else 0,
            'authorized_entries': stats.authorized_entries if stats else 0,
            'unauthorized_attempts': stats.unauthorized_attempts if stats else 0
        }
    })

@app.route('/simulate_entry_exit', methods=['POST'])
@login_required
def simulate_entry_exit():
    """Simulate vehicle entry/exit for testing"""
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('login'))
    
    plate_number = request.form.get('plate_number', '').strip().upper()
    entry_type = request.form.get('entry_type', 'ENTRY')
    
    if not plate_number:
        flash('Please provide a license plate number')
        return redirect(url_for('admin_dashboard'))
    
    # Check if authorized
    authorized_vehicle = AuthorizedVehicle.query.filter_by(
        plate_number=plate_number, is_active=True
    ).first()
    
    is_authorized = authorized_vehicle is not None
    owner_info = None
    
    if is_authorized:
        owner_info = json.dumps({
            'owner': authorized_vehicle.owner_name,
            'vehicle_type': authorized_vehicle.vehicle_type,
            'phone': authorized_vehicle.phone_number
        })
    
    # Log the event
    log_entry = AccessLog(
        plate_number=plate_number,
        authorized=is_authorized,
        confidence=0.95,
        gate_action="OPENED" if is_authorized else "DENIED",
        entry_type=entry_type,
        owner_info=owner_info
    )
    db.session.add(log_entry)
    
    # Update vehicle status
    update_vehicle_status(plate_number, entry_type, is_authorized, owner_info)
    
    if is_authorized:
        action = "entered" if entry_type == "ENTRY" else "exited"
        flash(f'✅ Vehicle {plate_number} {action} successfully!')
    else:
        flash(f'❌ Unauthorized vehicle {plate_number} denied access!')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create directories
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['VIDEO_FOLDER']):
        os.makedirs(app.config['VIDEO_FOLDER'])
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_password = generate_password_hash('admin123')
            admin_user = User(username='admin', password_hash=admin_password, is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created (admin/admin123)")
    
    app.run(debug=True)
