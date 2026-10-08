# Send readings to the caydas.cloud climate API (see ESP32_CLIMATE_API.md).
import requests
import secrets
from device import DEVICE_ID, LOCATION  # per-board, from devices/<name>.py

API_URL = "https://caydas.cloud/api/climate"
TIMEOUT_S = 20  # TLS handshake with caydas.cloud alone takes ~5s on the C3
DEFAULT_INTERVAL_S = 300


def post(temperature, humidity, rssi=None):
    """Return the server's requested interval in seconds, or None if the upload failed."""
    payload = {
        "device_id": DEVICE_ID,
        "location": LOCATION,
        "temperature": float(temperature),
        "humidity": float(humidity),
    }
    if rssi is not None:
        payload["wifi_rssi"] = rssi
    try:
        r = requests.post(
            API_URL,
            json=payload,
            headers={"X-API-Key": secrets.CLIMATE_API_KEY},
            timeout=TIMEOUT_S,
        )
        try:
            if r.status_code != 201:
                print("climate: HTTP", r.status_code, r.text)
                return None
            return r.json().get("config", {}).get("interval") or DEFAULT_INTERVAL_S
        finally:
            r.close()
    except Exception as e:
        print("climate: upload failed", repr(e))
        return None
