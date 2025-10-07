"""
Arduino Integration Services
Migrated from Flask Arduino functions
"""
import requests
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ArduinoService:
    """
    Arduino communication service
    Migrated from Flask Arduino functions
    """

    def __init__(self):
        self.arduino_ip = getattr(settings, 'ARDUINO_IP', '192.168.1.100')
        self.arduino_port = getattr(settings, 'ARDUINO_PORT', 80)

    def send_to_arduino(self, endpoint, data=None):
        """
        Send command to Arduino gate controller
        Migrated from Flask send_to_arduino function
        """
        try:
            url = f"http://{self.arduino_ip}:{self.arduino_port}/api/{endpoint}"

            if data:
                response = requests.post(url, json=data, timeout=5)
            else:
                response = requests.get(url, timeout=5)

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Arduino connection error: {e}")
            return {"error": f"Cannot connect to Arduino: {e}"}
        except Exception as e:
            logger.error(f"Arduino communication error: {e}")
            return {"error": f"Arduino error: {e}"}

    def open_gate(self, plate_number, owner_name="Unknown", authorized=True):
        """
        Send gate open command to Arduino with license plate info
        Migrated from Flask open_gate_arduino function
        """
        data = {
            "plate_number": plate_number,
            "owner_name": owner_name,
            "authorized": authorized,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"🚪 Sending gate command to Arduino for plate: {plate_number}")
        result = self.send_to_arduino("access/authorized", data)

        if "error" not in result:
            logger.info(f"✅ Arduino responded: {result.get('message', 'Gate opened')}")
        else:
            logger.error(f"❌ Arduino error: {result['error']}")

        return result

    def get_status(self):
        """
        Get current status from Arduino
        Migrated from Flask get_arduino_status function
        """
        return self.send_to_arduino("gate/status")

    def close_gate(self):
        """Send gate close command to Arduino"""
        return self.send_to_arduino("gate/close")

    def manual_open_gate(self, plate_number="MANUAL", owner_name="Manual Override"):
        """Manually open gate via Arduino"""
        return self.open_gate(plate_number, owner_name, True)