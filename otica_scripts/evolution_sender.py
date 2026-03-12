import time

import qrcode
import requests

from otica_scripts.config import (
    EVOLUTION_API_KEY,
    EVOLUTION_API_URL,
    EVOLUTION_INSTANCE_NAME,
    MAX_MESSAGE_LENGTH,
    MESSAGE_DELAY_SECONDS,
)
from otica_scripts.store import Store


class EvolutionSender:
    """Sender for WhatsApp messages using Evolution API via HTTP."""

    def __init__(self) -> None:
        self.api_url = EVOLUTION_API_URL.rstrip("/")
        self.api_key = EVOLUTION_API_KEY
        self.instance_name = EVOLUTION_INSTANCE_NAME
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def _format_phone(self, phone: str) -> str:
        """Evolution API expects numbers without the '+' sign."""
        return phone.replace("+", "").replace("-", "").replace(" ", "")

    def _check_instance_exists(self) -> bool:
        """Check if the configured instance exists in Evolution API."""
        try:
            url = f"{self.api_url}/instance/fetchInstances"
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                instances = response.json()
                for inst in instances:
                    # check instance name in V2 (v1 was different)
                    if inst.get("name") == self.instance_name or inst.get("instance", {}).get("instanceName") == self.instance_name:
                        return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error checking Evolution instances: {e}")
            return False

    def _create_instance(self) -> dict | None:
        """Create a new instance in Evolution API."""
        try:
            url = f"{self.api_url}/instance/create"
            payload = {
                "instanceName": self.instance_name,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            if response.status_code == 201:
                return dict(response.json())
            print(f"Failed to create instance: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error creating instance: {e}")
            return None

    def _get_connection_state(self) -> str | None:
        """Get the connection state of the instance."""
        try:
            url = f"{self.api_url}/instance/connectionState/{self.instance_name}"
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Evolution v2 may return state in different paths
                instance_data = data.get("instance", {})
                if isinstance(instance_data, dict):
                    state = instance_data.get("state")
                else:
                    state = data.get("state")
                return str(state) if state is not None else None
            return None
        except requests.exceptions.RequestException:
            return None

    def _display_qr_code(self) -> bool:
        """Connect the instance and display the QR Code in the terminal."""
        try:
            url = f"{self.api_url}/instance/connect/{self.instance_name}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # base64_qr is not used currently but we keep the structure.
                _base64_qr = data.get("base64")
                code_url = data.get("code")

                if code_url:
                    qr = qrcode.QRCode(version=1, box_size=10, border=4)
                    qr.add_data(code_url)
                    qr.make(fit=True)
                    qr.print_ascii(tty=True)
                    print("\nWARNING: Please scan this QR code within 60 seconds")
                    return True

            print(f"Failed to get QR code. Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error getting QR code: {e}")
            return False

    def open_whatsapp(self) -> bool:
        """Check connection state, and connect/show QR if needed."""
        print(f"Connecting to Evolution API at {self.api_url}...")

        # 1. Test API connection
        try:
            requests.get(self.api_url, timeout=5)
        except requests.exceptions.RequestException:
            print("ERROR: Could not connect to Evolution API.")
            print("Is Docker running? Did you run 'docker-compose up -d'?")
            return False

        # 2. Ensure instance exists
        if not self._check_instance_exists():
            print(f"Creating instance '{self.instance_name}'...")
            if not self._create_instance():
                return False

        # 3. Check connection state
        state = self._get_connection_state()
        if state == "open":
            print("WhatsApp is ready (Evolution API)!")
            return True

        print(f"Instance state is '{state}'. Requesting QR Code...")
        if self._display_qr_code():
            print("Waiting for connection...")
            # Wait up to 60 seconds
            for _ in range(30):
                time.sleep(2)
                if self._get_connection_state() == "open":
                    print("\nWhatsApp is connected and ready!")
                    return True
            print("\nTimeout waiting for scan.")
        return False

    def _send_message(self, phone: str, message: str) -> bool:
        """Send message via Evolution API HTTP Request."""
        try:
            url = f"{self.api_url}/message/sendText/{self.instance_name}"
            payload = {
                "number": self._format_phone(phone),
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": False
                },
                "textMessage": {
                    "text": message
                }
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)

            if response.status_code == 201:
                print("Message sent successfully!")
                return True

            print(f"ERROR sending message: {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"ERROR sending message: {e}")
            return False

    def send_to_store(self, store: Store, message: str) -> bool:
        if len(message) > MAX_MESSAGE_LENGTH:
            print(f"Warning: Message exceeds {MAX_MESSAGE_LENGTH} characters")
        print(f"Sending via API for {store.name} ({store.phone})...")
        return self._send_message(store.phone, message)

    def send_to_all(self, stores: list[Store], message: str) -> dict[str, bool]:
        if len(message) > MAX_MESSAGE_LENGTH:
            print(f"Warning: Message exceeds {MAX_MESSAGE_LENGTH} characters")

        results = {}
        for store in stores:
            print(f"\nSending to {store.name} ({store.phone})...")
            success = self.send_to_store(store, message)
            results[store.name] = success
            if success and store != stores[-1]:
                print(f"Waiting {MESSAGE_DELAY_SECONDS}s before next message...")
                time.sleep(MESSAGE_DELAY_SECONDS)
        return results

    def close(self) -> None:
        """Nothing to close for the API, but required for interface compatibility."""
        pass
