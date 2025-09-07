import cv2
import numpy as np
import easyocr
import re
from datetime import datetime
import time
import threading
import json
from typing import List, Tuple, Optional, Dict
from difflib import SequenceMatcher

class AdvancedLicensePlateDetector:
    def __init__(self):
        self.reader = easyocr.Reader(['th', 'en'])
        self.confidence_threshold = 0.6
        self.min_area = 1000
        self.aspect_ratio_range = (2, 8)
        
        # Thai license plate patterns (improved based on research)
        self.thai_patterns = [
            r'^[\u0E01-\u0E5B]{1,2}\d{1,4}$',  # Research pattern: \D{1,2}\d{1,4}
            r'^[\u0E01-\u0E5B]{1,3}\s*\d{1,4}$',  # Thai chars + numbers
            r'^\d{1,3}[\u0E01-\u0E5B]{1,3}\d{1,4}$',  # Num + Thai + Num
            r'^[\u0E01-\u0E5B]{2}\s*\d{4}$',  # 2 Thai + 4 digits
        ]
        
        # International patterns (improved based on research)
        self.intl_patterns = [
            r'^[A-Z]{1,2}\d{1,4}$',  # Research pattern: \D{1,2}\d{1,4}
            r'^[A-Z]{2,3}\s*\d{3,4}$',  # AA 123, ABC 1234
            r'^\d{1,3}[A-Z]{1,3}\d{1,4}$',  # 1A23, 12AB34
            r'^[A-Z0-9]{5,8}$',  # General alphanumeric
        ]
        
        # Store previous detections for duplicate filtering
        self.previous_detections = []
        self.similarity_threshold = 1.0  # 100% similarity for duplicates

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
        """Clean and standardize extracted text with improved logic from research"""
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^\u0E01-\u0E5BA-Z0-9\s]', '', text.upper())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Common OCR error corrections (more conservative)
        corrections = {
            'O': '0', 'Q': '0',  # Only obvious cases
            'I': '1',  # Only when clearly 1
            'Z': '2',  # Only obvious Z->2 cases
        }
        
        for wrong, correct in corrections.items():
            cleaned = cleaned.replace(wrong, correct)
        
        # Fix character order based on research (e.g., "9999AB" -> "AB9999")
        cleaned = self.fix_character_order(cleaned)
        
        return cleaned
    
    def fix_character_order(self, text: str) -> str:
        """Fix character order for tilted plates (research finding)"""
        # Check if text matches research pattern \D{1,2}\d{1,4}
        research_pattern = r'^[A-Z\u0E01-\u0E5B]{1,2}\d{1,4}$'
        if re.match(research_pattern, text):
            return text  # Already correct
        
        # Check if it's reversed (digits first, then characters)  
        # Support both 1-2 and 1-3 characters for better coverage
        reversed_pattern = r'^\d{1,4}[A-Z\u0E01-\u0E5B]{1,3}$'
        if re.match(reversed_pattern, text):
            # Extract digits and characters
            digits = re.findall(r'\d+', text)
            chars = re.findall(r'[A-Z\u0E01-\u0E5B]+', text)
            if digits and chars:
                # Swap order: "9999AB" -> "AB9999" or "789XYZ" -> "XYZ789"
                return chars[0] + digits[0]
        
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two license plate texts"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def is_duplicate(self, current_text: str) -> bool:
        """Check if current detection is duplicate based on research method"""
        for prev_text in self.previous_detections[-5:]:  # Check last 5 detections
            if self.calculate_similarity(current_text, prev_text) >= self.similarity_threshold:
                return True
        return False
    
    def add_detection(self, text: str):
        """Add detection to history for duplicate filtering"""
        if not self.is_duplicate(text):
            self.previous_detections.append(text)
            # Keep only recent detections to save memory
            if len(self.previous_detections) > 10:
                self.previous_detections.pop(0)

    def validate_license_plate(self, text: str) -> bool:
        """Enhanced validation based on research patterns"""
        if len(text) < 4 or len(text) > 8:  # Stricter length limit
            return False
        
        # Primary check: Research pattern \D{1,2}\d{1,4}
        research_pattern = r'^[A-Z\u0E01-\u0E5B]{1,2}\d{1,4}$'
        if re.match(research_pattern, text):
            return True
        
        # Stricter pattern checks to reject invalid long plates
        # Reject plates with too many characters or numbers
        char_count = len(re.findall(r'[A-Z\u0E01-\u0E5B]', text))
        num_count = len(re.findall(r'\d', text))
        
        if char_count > 3 or num_count > 4:  # Too many chars/numbers
            return False
        
        # Check against other valid patterns
        valid_patterns = [
            r'^[A-Z\u0E01-\u0E5B]{2,3}\s*\d{3,4}$',  # Standard format
            r'^\d{1,3}[A-Z\u0E01-\u0E5B]{1,2}\d{1,4}$',  # Mixed format
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, text):
                return True
        
        # Final heuristic checks
        has_letter = bool(re.search(r'[A-Z\u0E01-\u0E5B]', text))
        has_number = bool(re.search(r'\d', text))
        
        return has_letter and has_number and len(text) <= 7

    def detect_license_plate(self, image: np.ndarray) -> Tuple[str, float, Tuple[int, int, int, int]]:
        """Enhanced detection method with research-based improvements"""
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
                        # Check for duplicates (research method)
                        if not self.is_duplicate(candidate_text):
                            best_text = candidate_text
                            best_confidence = conf
                            # Calculate bounding box
                            points = np.array(bbox, dtype=np.int32)
                            x, y, w, h = cv2.boundingRect(points)
                            best_region = (x, y, w, h)
        except Exception:
            pass
        
        # Method 2: Contour-based detection
        plate_candidates = self.detect_license_plate_contours(image)
        
        for region in plate_candidates:
            text, conf = self.extract_text_from_region(image, region)
            if conf > best_confidence and conf > self.confidence_threshold:
                if self.validate_license_plate(text) and not self.is_duplicate(text):
                    best_text = text
                    best_confidence = conf
                    best_region = region
        
        # Add valid detection to history
        if best_text and best_confidence > self.confidence_threshold:
            self.add_detection(best_text)
        
        return best_text, best_confidence, best_region


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
        from difflib import SequenceMatcher
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


# Hardware integration functions (to be implemented based on your hardware)
class HardwareController:
    """Hardware controller for actual gate/door control"""
    
    def __init__(self):
        # Initialize hardware connections
        # Examples: GPIO pins, serial connections, network APIs
        pass
    
    def open_gate(self):
        """Open physical gate/door"""
        # Example implementations:
        
        # For Raspberry Pi GPIO:
        # import RPi.GPIO as GPIO
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(18, GPIO.OUT)
        # GPIO.output(18, GPIO.HIGH)
        
        # For Arduino serial:
        # import serial
        # ser = serial.Serial('/dev/ttyUSB0', 9600)
        # ser.write(b'OPEN_GATE\n')
        
        # For network API:
        # import requests
        # requests.post('http://gate-controller/api/open')
        
        print("🔌 Hardware: Opening gate...")
    
    def close_gate(self):
        """Close physical gate/door"""
        print("🔌 Hardware: Closing gate...")
    
    def get_gate_status(self):
        """Get current gate status from sensors"""
        # Read from sensors
        return "CLOSED"  # or "OPEN", "OPENING", "CLOSING"


if __name__ == "__main__":
    # Example usage
    access_system = AccessControlSystem()
    
    # Add some test authorized plates
    access_system.add_authorized_plate("ABC123", "John Doe", "Car")
    access_system.add_authorized_plate("กข1234", "สมชาย ใจดี", "รถเก๋ง")
    
    print("🎯 Advanced License Plate Access Control System")
    print("📋 Authorized plates loaded:", len(access_system.authorized_plates))
    print("🚪 Gate status:", access_system.gate_status)
    print("=" * 50)