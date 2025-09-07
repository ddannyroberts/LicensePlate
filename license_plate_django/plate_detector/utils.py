import cv2
import numpy as np
import easyocr
import os
from django.conf import settings

class LicensePlateDetector:
    def __init__(self):
        self.model = None
        self.class_names = []
        self.reader = easyocr.Reader(['th', 'en'])
        self.load_vehicle_model()
    
    def load_vehicle_model(self):
        try:
            from keras.models import load_model
            model_path = os.path.join(settings.BASE_DIR, "keras_Model.h5")
            labels_path = os.path.join(settings.BASE_DIR, "labels.txt")
            
            if os.path.exists(model_path) and os.path.exists(labels_path):
                self.model = load_model(model_path, compile=False)
                with open(labels_path, "r") as f:
                    self.class_names = f.readlines()
        except ImportError:
            print("Keras not installed, vehicle type detection disabled")
            self.model = None
    
    def detect_plate_and_crop(self, image):
        """Enhanced OCR function with better preprocessing"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply image enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Convert back to BGR for EasyOCR
        enhanced_bgr = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
        
        results = self.reader.readtext(enhanced_bgr)
        
        best_text = "UNKNOWN"
        best_crop = None
        best_confidence = 0
        
        for (bbox, text, prob) in results:
            # Filter by confidence and text length
            if prob > 0.3 and len(text) >= 4:
                # Additional filtering for Thai/English license plates
                text_upper = text.upper().replace(' ', '')
                
                # Basic license plate pattern matching
                if self._is_valid_license_plate(text_upper) and prob > best_confidence:
                    best_confidence = prob
                    best_text = text_upper
                    
                    # Crop the detected region
                    (tl, tr, br, bl) = bbox
                    tl, br = tuple(map(int, tl)), tuple(map(int, br))
                    
                    # Add some padding
                    h, w = image.shape[:2]
                    x1 = max(0, tl[0] - 10)
                    y1 = max(0, tl[1] - 10)
                    x2 = min(w, br[0] + 10)
                    y2 = min(h, br[1] + 10)
                    
                    best_crop = image[y1:y2, x1:x2]
        
        return best_text, best_crop
    
    def _is_valid_license_plate(self, text):
        """Check if text looks like a valid license plate"""
        import re
        
        # Remove common OCR errors
        text = text.replace('O', '0').replace('I', '1').replace('S', '5')
        
        # Thai license plate patterns
        thai_patterns = [
            r'^[\u0E00-\u0E7F]{1,3}\s*\d{1,4}$',  # Thai characters + numbers
            r'^\d{1,3}[\u0E00-\u0E7F]{1,3}\d{1,4}$',  # Number + Thai + Number
        ]
        
        # International license plate patterns
        intl_patterns = [
            r'^[A-Z]{1,3}\d{1,4}$',  # Letters + numbers
            r'^\d{1,3}[A-Z]{1,3}\d{1,4}$',  # Mixed pattern
            r'^[A-Z0-9]{4,8}$',  # General alphanumeric
        ]
        
        all_patterns = thai_patterns + intl_patterns
        
        for pattern in all_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def predict_vehicle_type(self, image):
        """Predict vehicle type using the trained model"""
        if self.model is None:
            return "Unknown"
        
        try:
            resized = cv2.resize(image, (224, 224))
            image_np = np.asarray(resized, dtype=np.float32).reshape(1, 224, 224, 3)
            image_np = (image_np / 127.5) - 1
            
            prediction = self.model.predict(image_np, verbose=0)
            index = np.argmax(prediction)
            
            if index < len(self.class_names):
                vehicle_type = self.class_names[index].strip().split()[-1]
                confidence = float(prediction[0][index])
                return vehicle_type if confidence > 0.5 else "Unknown"
            
        except Exception as e:
            print(f"Error in vehicle type prediction: {e}")
        
        return "Unknown"
    
    def process_video_frame(self, frame):
        """Process a single video frame for license plate detection"""
        h, w = frame.shape[:2]
        
        # Focus on bottom 40% of the frame where license plates usually are
        plate_area = frame[int(h * 0.6):, :]
        
        # Detect plate in the focused area
        plate_text, plate_crop = self.detect_plate_and_crop(plate_area)
        
        # Predict vehicle type from full frame
        vehicle_type = self.predict_vehicle_type(frame)
        
        return {
            'plate_text': plate_text,
            'plate_crop': plate_crop,
            'vehicle_type': vehicle_type,
            'full_frame': frame
        }
    
    def process_video_file(self, video_path, progress_callback=None):
        """Process entire video file and extract license plates"""
        cap = cv2.VideoCapture(video_path)
        results = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Process every 10th frame to reduce processing time
        frame_skip = 10
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                result = self.process_video_frame(frame)
                if result['plate_text'] != "UNKNOWN":
                    result['timestamp'] = frame_count / cap.get(cv2.CAP_PROP_FPS)
                    results.append(result)
                
                if progress_callback:
                    progress_callback(frame_count / total_frames * 100)
            
            frame_count += 1
        
        cap.release()
        return results