# Connect to Wi-Fi using the networks listed in secrets.py.
import network
import time
import secrets

# Statuses that mean this network won't work, so move on to the next one
_FAILED = (network.STAT_WRONG_PASSWORD, network.STAT_NO_AP_FOUND, network.STAT_CONNECT_FAIL)


def connect(timeout_s=15):
    """Return (ssid, ip), or None if no network could be joined."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # This board's antenna can't complete the login at full power (fails as "wrong password")
    wlan.config(txpower=8.5)
    if wlan.isconnected():
        return wlan.config("ssid"), wlan.ifconfig()[0]

    for ssid, password in secrets.WIFI_NETWORKS:
        wlan.disconnect()
        time.sleep(0.5)
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if wlan.status() in _FAILED or time.time() - start > timeout_s:
                break
            time.sleep(0.2)
        if wlan.isconnected():
            return ssid, wlan.ifconfig()[0]
    return None
