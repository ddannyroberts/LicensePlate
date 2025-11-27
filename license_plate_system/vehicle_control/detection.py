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

# Global detector instance (lazy loading to avoid startup delays and memory issues)
_detector_instance = None
_lock = threading.Lock()

def get_detector():
    """Get or create detector instance (lazy loading to avoid startup delays)"""
    global _detector_instance
    if _detector_instance is None:
        with _lock:
            # Double-check pattern to avoid race conditions
            if _detector_instance is None:
                _detector_instance = AdvancedLicensePlateDetector()
    return _detector_instance