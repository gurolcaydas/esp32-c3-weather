# Connect to Wi-Fi, show DHT11 temperature and humidity on the HW-675 screen,
# and upload readings to caydas.cloud.
#
# Layout (72x40):   23°C   [wifi]
#                   45%
from machine import Pin
import dht
import framebuf
import network
import time
from oled import OLED, WIDTH
import climate
import wifi

DHT_PIN = 4
READ_INTERVAL_S = 3  # DHT11 needs at least 1s between reads
SCALE = 2            # 8x8 built-in font drawn at 2x = 16px tall

# 9x7 Wi-Fi icon, one string per row
WIFI_ICON = (
    "..#####..",
    ".#.....#.",
    "#..###..#",
    ".#.....#.",
    "...###...",
    ".........",
    "....#....",
)

oled = OLED()
sensor = dht.DHT11(Pin(DHT_PIN))
wlan = network.WLAN(network.STA_IF)


def big_text(s, x, y):
    """Draw s with the built-in font scaled up; return the x just past the text."""
    w = len(s) * 8
    buf = framebuf.FrameBuffer(bytearray(w), w, 8, framebuf.MONO_VLSB)
    buf.text(s, 0, 0, 1)
    for py in range(8):
        for px in range(w):
            if buf.pixel(px, py):
                oled.fill_rect(x + px * SCALE, y + py * SCALE, SCALE, SCALE, 1)
    return x + w * SCALE


def wifi_icon(connected):
    x0 = WIDTH - len(WIFI_ICON[0])
    for y, row in enumerate(WIFI_ICON):
        for x, ch in enumerate(row):
            if ch == "#":
                oled.pixel(x0 + x, y, 1)
    if not connected:
        oled.line(x0, 6, x0 + 8, 0, 1)  # strike through when offline


def draw(temp, hum):
    oled.fill(0)
    wifi_icon(wlan.isconnected())
    if temp is None:
        big_text("--", 0, 2)
        big_text("--", 0, 22)
    else:
        x = big_text(str(temp), 0, 2)
        oled.ellipse(x + 3, 4, 2, 2, 1)  # degree sign
        big_text("C", x + 7, 2)
        big_text("%d%%" % hum, 0, 22)
    oled.show()


def upload_mark(ok):
    """Small mark under the Wi-Fi icon: up arrow = last upload OK, X = it failed."""
    x0 = WIDTH - 8
    if ok:
        oled.vline(x0 + 3, 10, 6, 1)
        oled.line(x0 + 3, 10, x0, 13, 1)
        oled.line(x0 + 3, 10, x0 + 6, 13, 1)
    else:
        oled.line(x0, 10, x0 + 6, 15, 1)
        oled.line(x0, 15, x0 + 6, 10, 1)


draw(None, None)
wifi.connect()

upload_interval_s = climate.DEFAULT_INTERVAL_S
last_upload = None  # ticks_ms of last upload attempt
upload_ok = None    # None until the first attempt

while True:
    try:
        sensor.measure()
        temp, hum = sensor.temperature(), sensor.humidity()
    except OSError:
        temp, hum = None, None

    now = time.ticks_ms()
    due = last_upload is None or time.ticks_diff(now, last_upload) >= upload_interval_s * 1000
    if temp is not None and due:
        last_upload = now
        if wifi.connect():  # reconnects if the connection dropped
            rssi = wlan.status("rssi")
            interval = climate.post(temp, hum, rssi)
        else:
            interval = None
        upload_ok = interval is not None
        if upload_ok:
            upload_interval_s = interval

    draw(temp, hum)
    if upload_ok is not None:
        upload_mark(upload_ok)
        oled.show()
    time.sleep(READ_INTERVAL_S)
