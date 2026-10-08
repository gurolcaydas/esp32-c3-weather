# Connect to Wi-Fi using the networks listed in secrets.py, preferring the strongest one.
import network
import time
import secrets

# Statuses that mean this network won't work, so move on to the next one
_FAILED = (network.STAT_WRONG_PASSWORD, network.STAT_NO_AP_FOUND, network.STAT_CONNECT_FAIL)

WEAK_RSSI = -75      # below this, look for a stronger known network
SWITCH_MARGIN = 10   # only switch if the other network is at least this many dB stronger


def _by_signal(wlan):
    """Known networks as [(ssid, password, rssi)], strongest first; unseen ones last."""
    seen = {}
    for ssid, _, _, rssi, *_ in wlan.scan():
        ssid = ssid.decode()
        seen[ssid] = max(rssi, seen.get(ssid, -999))
    known = [(s, p, seen.get(s, -999)) for s, p in secrets.WIFI_NETWORKS]
    return sorted(known, key=lambda n: -n[2])


def connect(timeout_s=15):
    """Return (ssid, ip), or None if no network could be joined.

    Safe to call repeatedly: if already connected with a good signal it returns at once,
    and if the signal is weak it moves to a clearly stronger known network.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # This board's antenna can't complete the login at full power (fails as "wrong password")
    wlan.config(txpower=8.5)

    if wlan.isconnected():
        current = wlan.config("ssid")
        rssi = wlan.status("rssi")
        if rssi >= WEAK_RSSI:
            return current, wlan.ifconfig()[0]
        best = _by_signal(wlan)[0]
        if best[0] == current or best[2] < rssi + SWITCH_MARGIN:
            return current, wlan.ifconfig()[0]
        print("wifi: %s at %d dBm, switching to %s at %d dBm" % (current, rssi, best[0], best[2]))

    for ssid, password, _ in _by_signal(wlan):
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
