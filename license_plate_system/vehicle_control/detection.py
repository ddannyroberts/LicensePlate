import cv2
import numpy as np
import easyocr
import re
import threading
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from difflib import SequenceMatcher
import json
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import io

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
        
        # Vehicle type model (optional - if available)
        self.vehicle_model = None
        self.class_names = []
        self.load_vehicle_model()

    def load_vehicle_model(self):
        """Load vehicle classification model if available"""
        try:
            from keras.models import load_model
            model_path = os.path.join(settings.BASE_DIR, "keras_Model.h5")
            labels_path = os.path.join(settings.BASE_DIR, "labels.txt")
            
            if os.path.exists(model_path) and os.path.exists(labels_path):
                self.vehicle_model = load_model(model_path, compile=False)
                with open(labels_path, "r") as f:
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

    def save_detection_image(self, image: np.ndarray, filename: str) -> str:
        """Save detection image to Django media storage"""
        try:
            # Convert numpy array to image bytes
            success, buffer = cv2.imencode('.jpg', image)
            if success:
                image_bytes = buffer.tobytes()
                image_file = ContentFile(image_bytes, name=filename)
                
                # Save to Django storage
                filename = default_storage.save(f'detections/{filename}', image_file)
                return filename
        except Exception as e:
            print(f"Error saving detection image: {e}")
        
        return None

class DjangoAccessControlSystem:
    """Django-integrated access control system"""
    
    def __init__(self):
        self.detector = AdvancedLicensePlateDetector()
        self.gate_status = "CLOSED"
    
    def process_vehicle_frame(self, image: np.ndarray, user=None) -> Dict:
        """Process a single frame for vehicle detection and access control"""
        from .models import AuthorizedVehicle, AccessLog, GateControlLog
        
        # Detect license plate
        plate_text, confidence, region = self.detector.detect_license_plate(image)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "plate_detected": plate_text,
            "confidence": confidence,
            "region": region,
            "authorized": False,
            "gate_action": "denied",
            "owner_info": None,
            "vehicle_type": None
        }
        
        if plate_text and confidence > 0.6:
            # Get vehicle type
            result["vehicle_type"] = self.detector.predict_vehicle_type(image)
            
            # Check authorization
            try:
                vehicle = AuthorizedVehicle.objects.get(
                    plate_number=plate_text.replace(' ', '').upper(),
                    is_active=True
                )
                
                # Check if not expired
                if not vehicle.is_expired():
                    result["authorized"] = True
                    result["gate_action"] = "opened"
                    result["owner_info"] = {
                        "owner": vehicle.owner_name,
                        "vehicle_type": vehicle.get_vehicle_type_display(),
                        "access_level": vehicle.get_access_level_display(),
                    }
                    
                    # Save detection image
                    if region:
                        x, y, w, h = region
                        padding = 10
                        x = max(0, x - padding)
                        y = max(0, y - padding)
                        w = min(image.shape[1] - x, w + 2 * padding)
                        h = min(image.shape[0] - y, h + 2 * padding)
                        crop = image[y:y+h, x:x+w]
                        
                        filename = f"plate_{plate_text}_{int(confidence*100)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        saved_filename = self.detector.save_detection_image(crop, filename)
                        
                        # Create access log
                        access_log = AccessLog.objects.create(
                            plate_number=plate_text,
                            authorized=True,
                            confidence=confidence,
                            gate_action='opened',
                            vehicle=vehicle,
                            processed_by=user,
                            owner_info=result["owner_info"],
                            detection_image=saved_filename
                        )
                        
                        # Log gate operation
                        GateControlLog.objects.create(
                            operation='open',
                            triggered_by=user,
                            related_access_log=access_log,
                            notes=f"Auto-opened for {plate_text}"
                        )
                        
                        # Simulate gate opening
                        self.simulate_gate_control("OPEN")
                        
                        print(f"✅ ACCESS GRANTED: {plate_text} - {vehicle.owner_name}")
                    
            except AuthorizedVehicle.DoesNotExist:
                # Unauthorized vehicle
                result["authorized"] = False
                result["gate_action"] = "denied"
                
                # Still log the attempt
                access_log = AccessLog.objects.create(
                    plate_number=plate_text,
                    authorized=False,
                    confidence=confidence,
                    gate_action='denied',
                    processed_by=user
                )
                
                print(f"❌ ACCESS DENIED: {plate_text} - Not authorized")
        
        else:
            print(f"⚠️ NO PLATE DETECTED - Confidence: {confidence:.2f}")
        
        return result
    
    def simulate_gate_control(self, action: str):
        """Simulate gate control operations"""
        if action == "OPEN":
            print(f"🚪 GATE OPENING... ({datetime.now().strftime('%H:%M:%S')})")
            self.gate_status = "OPENING"
            
            # Simulate opening time
            threading.Timer(2.0, self._gate_opened).start()
            
            # Auto-close after 10 seconds
            threading.Timer(12.0, lambda: self.simulate_gate_control("CLOSE")).start()
            
        elif action == "CLOSE":
            print(f"🚪 GATE CLOSING... ({datetime.now().strftime('%H:%M:%S')})")
            self.gate_status = "CLOSING"
            threading.Timer(2.0, self._gate_closed).start()
    
    def _gate_opened(self):
        self.gate_status = "OPEN"
        print(f"✅ GATE OPENED ({datetime.now().strftime('%H:%M:%S')})")
    
    def _gate_closed(self):
        self.gate_status = "CLOSED"
        print(f"🔒 GATE CLOSED ({datetime.now().strftime('%H:%M:%S')})")
    
    def process_video_file(self, video_path: str, user=None, callback=None):
        """Process entire video file for license plate detection"""
        from .models import VehicleDetection, AccessLog
        
        results = []
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        frame_skip = 30  # Process every 30th frame
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                # Process frame
                frame_result = self.process_vehicle_frame(frame, user)
                
                if frame_result['plate_detected'] and frame_result['confidence'] > 0.6:
                    frame_result['timestamp_seconds'] = frame_count / cap.get(cv2.CAP_PROP_FPS)
                    results.append(frame_result)
                
                # Call progress callback if provided
                if callback:
                    progress = (frame_count / total_frames) * 100
                    callback(progress, len(results))
            
            frame_count += 1
        
        cap.release()
        return results

# Global detector instance
detector_instance = DjangoAccessControlSystem()