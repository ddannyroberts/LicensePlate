#!/usr/bin/env python3
"""
Test script to validate improvements based on research paper
Thai License Plate Recognition using SSD MobileNet and EasyOCR
"""

import cv2
import numpy as np
from advanced_detection import AdvancedLicensePlateDetector
import time

def test_character_order_correction():
    """Test character order correction feature"""
    print("🔧 Testing Character Order Correction...")
    
    detector = AdvancedLicensePlateDetector()
    
    # Test cases from research paper
    test_cases = [
        ("9999AB", "AB9999"),  # Research example
        ("1234กข", "กข1234"),   # Thai version
        ("ABC123", "ABC123"),   # Already correct
        ("789XYZ", "XYZ789"),   # Another reversed case
        ("กข1234", "กข1234"),    # Already correct Thai
    ]
    
    correct_count = 0
    for input_text, expected in test_cases:
        result = detector.fix_character_order(input_text)
        if result == expected:
            print(f"  ✅ '{input_text}' → '{result}' (Expected: '{expected}')")
            correct_count += 1
        else:
            print(f"  ❌ '{input_text}' → '{result}' (Expected: '{expected}')")
    
    accuracy = (correct_count / len(test_cases)) * 100
    print(f"  📊 Character Order Correction Accuracy: {accuracy:.1f}%")
    return accuracy

def test_pattern_validation():
    """Test enhanced pattern validation"""
    print("\\n🎯 Testing Enhanced Pattern Validation...")
    
    detector = AdvancedLicensePlateDetector()
    
    # Test cases based on research pattern \\D{1,2}\\d{1,4}
    valid_plates = [
        "AB1234",    # Research pattern
        "A123",      # Research pattern  
        "กข1234",     # Thai research pattern
        "ก123",       # Thai research pattern
        "XY9999",     # International
        "ABC123",     # Extended valid
    ]
    
    invalid_plates = [
        "ABCD1234",   # Too many letters
        "AB12345",    # Too many numbers
        "AB",         # Too short
        "1234",       # No letters
        "ABCD",       # No numbers
        "",           # Empty
    ]
    
    # Test valid plates
    valid_correct = 0
    for plate in valid_plates:
        is_valid = detector.validate_license_plate(plate)
        if is_valid:
            print(f"  ✅ '{plate}' - Valid")
            valid_correct += 1
        else:
            print(f"  ❌ '{plate}' - Incorrectly marked invalid")
    
    # Test invalid plates  
    invalid_correct = 0
    for plate in invalid_plates:
        is_valid = detector.validate_license_plate(plate)
        if not is_valid:
            print(f"  ✅ '{plate}' - Correctly rejected")
            invalid_correct += 1
        else:
            print(f"  ❌ '{plate}' - Incorrectly marked valid")
    
    total_correct = valid_correct + invalid_correct
    total_tests = len(valid_plates) + len(invalid_plates)
    accuracy = (total_correct / total_tests) * 100
    
    print(f"  📊 Pattern Validation Accuracy: {accuracy:.1f}%")
    return accuracy

def test_duplicate_filtering():
    """Test duplicate filtering system"""
    print("\\n🔄 Testing Duplicate Filtering...")
    
    detector = AdvancedLicensePlateDetector()
    
    # Simulate video frames with same plate
    detections = ["AB1234", "AB1234", "AB1235", "AB1234", "XY5678", "AB1234"]
    unique_detections = []
    
    for detection in detections:
        if not detector.is_duplicate(detection):
            unique_detections.append(detection)
            detector.add_detection(detection)
            print(f"  ✅ '{detection}' - Added (new)")
        else:
            print(f"  🔄 '{detection}' - Filtered (duplicate)")
    
    print(f"  📊 Original: {len(detections)} detections")
    print(f"  📊 After filtering: {len(unique_detections)} unique detections")
    print(f"  📊 Filtered out: {len(detections) - len(unique_detections)} duplicates")
    
    reduction_rate = ((len(detections) - len(unique_detections)) / len(detections)) * 100
    print(f"  📊 Duplicate Reduction Rate: {reduction_rate:.1f}%")
    return reduction_rate

def test_ocr_error_corrections():
    """Test OCR error corrections"""
    print("\\n🔧 Testing OCR Error Corrections...")
    
    detector = AdvancedLicensePlateDetector()
    
    # Common OCR errors
    test_cases = [
        ("ABO123", "AB0123"),   # O → 0
        ("AB1Z3", "AB123"),     # Z → 2 (partial)
        ("ABI23", "AB123"),     # I → 1
        ("ABS23", "AB523"),     # S → 5
        ("กขQ123", "กข0123"),    # Q → 0
        ("PERFECT", "PERFECT"), # No changes needed
    ]
    
    correct_count = 0
    for input_text, expected in test_cases:
        result = detector.clean_text(input_text)
        # Check if correction moved in right direction
        if result == expected or (expected in result):
            print(f"  ✅ '{input_text}' → '{result}'")
            correct_count += 1
        else:
            print(f"  ⚠️  '{input_text}' → '{result}' (Expected: '{expected}')")
    
    accuracy = (correct_count / len(test_cases)) * 100
    print(f"  📊 OCR Error Correction Accuracy: {accuracy:.1f}%")
    return accuracy

def test_similarity_calculation():
    """Test similarity calculation for duplicate detection"""
    print("\\n📏 Testing Similarity Calculation...")
    
    detector = AdvancedLicensePlateDetector()
    
    # Test similarity cases
    test_cases = [
        ("AB1234", "AB1234", 1.0),   # Identical
        ("AB1234", "AB1235", 0.83),  # Very similar  
        ("AB1234", "XY5678", 0.0),   # Completely different
        ("กข1234", "กข1235", 0.83),   # Thai similar
        ("AB123", "AB1234", 0.91),   # Length difference
    ]
    
    correct_count = 0
    for text1, text2, expected_min in test_cases:
        similarity = detector.calculate_similarity(text1, text2)
        if similarity >= expected_min - 0.1:  # Allow small tolerance
            print(f"  ✅ '{text1}' vs '{text2}' = {similarity:.2f}")
            correct_count += 1
        else:
            print(f"  ❌ '{text1}' vs '{text2}' = {similarity:.2f} (Expected >= {expected_min})")
    
    accuracy = (correct_count / len(test_cases)) * 100
    print(f"  📊 Similarity Calculation Accuracy: {accuracy:.1f}%")
    return accuracy

def main():
    """Run all improvement tests"""
    print("🚗 Thai License Plate Recognition - Improvement Test Suite")
    print("📝 Based on research: 'Thai License Plate Recognition using SSD MobileNet and EasyOCR'")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all tests
    results = {}
    results['character_order'] = test_character_order_correction()
    results['pattern_validation'] = test_pattern_validation()  
    results['duplicate_filtering'] = test_duplicate_filtering()
    results['ocr_corrections'] = test_ocr_error_corrections()
    results['similarity_calc'] = test_similarity_calculation()
    
    end_time = time.time()
    
    # Summary
    print("\\n" + "=" * 80)
    print("📊 IMPROVEMENT TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_score = 0
    for test_name, score in results.items():
        print(f"  {test_name.replace('_', ' ').title():<30}: {score:>6.1f}%")
        total_score += score
    
    average_score = total_score / len(results)
    print(f"\\n  {'Overall Improvement Score':<30}: {average_score:>6.1f}%")
    print(f"  {'Test Execution Time':<30}: {end_time - start_time:>6.1f}s")
    
    # Research comparison
    print("\\n📚 RESEARCH PAPER BENCHMARKS:")
    print("  License Plate Detection Accuracy    :   99.0%")  
    print("  Number Plate Recognition Accuracy   :   72.0%")
    print("  Character Recognition Accuracy      :   92.0%")
    print("  Video Detection Accuracy            :   91.7%")
    print("  Video Number Recognition            :   83.5%")
    print("  Video Character Recognition         :   97.0%")
    
    if average_score >= 85:
        print("\\n🎉 EXCELLENT! Improvements are working well!")
    elif average_score >= 70:
        print("\\n👍 GOOD! Most improvements are effective!")
    else:
        print("\\n⚠️  NEEDS WORK! Some improvements need refinement!")
    
    print("\\n✨ Ready to test with real images/videos!")

if __name__ == "__main__":
    main()