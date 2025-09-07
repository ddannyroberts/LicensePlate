#!/usr/bin/env python3
"""
Script to capture screenshot of the enhanced admin dashboard
"""
import time
import subprocess
import sys

def capture_dashboard():
    """Capture dashboard screenshot using browser automation"""
    try:
        # Try to install selenium if not available
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            print("📦 Installing selenium for screenshot capture...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'selenium'])
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

        print("📸 Capturing Enhanced Admin Dashboard...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"❌ Chrome driver not available: {e}")
            print("🔧 Please install ChromeDriver or use Safari to view:")
            print("   http://127.0.0.1:5000")
            return False
        
        try:
            # Navigate to login page
            driver.get('http://127.0.0.1:5000')
            print("🌐 Navigated to login page")
            
            # Wait for login form and login
            wait = WebDriverWait(driver, 10)
            
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            print("🔑 Logged in successfully")
            
            # Wait for dashboard to load
            time.sleep(2)
            
            # Navigate to admin dashboard
            driver.get('http://127.0.0.1:5000/admin/dashboard')
            print("📊 Navigated to admin dashboard")
            
            # Wait for dashboard content to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "stat-card")))
            time.sleep(3)  # Wait for any dynamic content
            
            # Take screenshot
            screenshot_path = "dashboard_screenshot.png"
            driver.save_screenshot(screenshot_path)
            
            print(f"✅ Screenshot saved as: {screenshot_path}")
            print("📱 Dashboard captured successfully!")
            
            # Get page title for verification
            title = driver.title
            print(f"📄 Page title: {title}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error capturing dashboard: {e}")
            return False
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Failed to capture dashboard: {e}")
        print("🌐 Please manually open: http://127.0.0.1:5000")
        print("🔑 Login with: admin / admin123")
        print("📊 Go to Admin Dashboard to see the enhanced interface")
        return False

def show_dashboard_info():
    """Show dashboard information and features"""
    print("🚗 Enhanced Admin Dashboard Features:")
    print("=" * 50)
    print("📊 REAL-TIME STATISTICS:")
    print("  • Vehicles Inside (current)")
    print("  • Total Entries Today")
    print("  • Total Exits Today")
    print("  • Authorized Entries")
    print("  • Access Denied Count")
    print("  • Peak Occupancy")
    
    print("\\n🚪 ENTRY/EXIT TRACKING:")
    print("  • Live vehicle status monitoring")
    print("  • Entry/Exit simulation")
    print("  • Duration tracking")
    print("  • Real-time updates every 5 seconds")
    
    print("\\n📱 LIVE FEATURES:")
    print("  • Real-time data refresh")
    print("  • Live activity feed")
    print("  • System status indicator")
    print("  • Responsive dashboard")
    
    print("\\n🌐 ACCESS INFO:")
    print("  URL: http://127.0.0.1:5000")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == "__main__":
    print("📸 Dashboard Screenshot Capture Tool")
    print("=" * 40)
    
    show_dashboard_info()
    print()
    
    # Try to capture screenshot
    success = capture_dashboard()
    
    if not success:
        print("\\n💡 Manual Access Instructions:")
        print("1. Open browser and go to: http://127.0.0.1:5000")
        print("2. Login with admin / admin123")
        print("3. You'll see the enhanced dashboard with:")
        print("   - Real-time statistics cards")
        print("   - Live vehicle tracking")
        print("   - Entry/Exit simulation")
        print("   - Activity monitoring")
    
    print("\\n✨ Dashboard is ready for testing!")