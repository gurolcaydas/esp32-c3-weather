# esp32-oled

MicroPython climate node for the **HW-675** board (ESP32-C3 with a 0.42" 72×40 OLED). It reads a DHT11, shows temperature and humidity on the screen, and uploads readings to [caydas.cloud](https://caydas.cloud/climate).

## Hardware

| Part | Pin |
|---|---|
| OLED (SSD1306, I2C 0x3C) | SDA = GPIO5, SCL = GPIO6 (on board) |
| DHT11 `S` / DATA | GPIO4 |
| DHT11 `+` / `-` | 3.3V / GND |

## Files

| File | Purpose |
|---|---|
| `main.py` | Display loop and upload schedule |
| `oled.py` | SSD1306 wrapper for the 72×40 panel (column offset 28) |
| `wifi.py` | Connects to the networks in `secrets.py`, at reduced TX power |
| `climate.py` | Posts readings to the caydas.cloud climate API |
| `devices/*.py` | Per-board name, copied to the board as `device.py` |
| `secrets.example.py` | Template for `secrets.py` (Wi-Fi + API key, git-ignored) |

## Setup

1. Flash MicroPython (`ESP32_GENERIC_C3`) with esptool:

   ```bash
   esptool --port /dev/cu.usbmodemXXXX erase-flash
   esptool --port /dev/cu.usbmodemXXXX --baud 460800 write-flash 0 ESP32_GENERIC_C3-<version>.bin
   ```

2. Install the screen driver and copy the code, choosing the board's file from `devices/`:

   ```bash
   cp secrets.example.py secrets.py   # then fill it in
   mpremote mip install ssd1306
   mpremote cp oled.py wifi.py secrets.py climate.py main.py : + cp devices/balcony.py :device.py + reset
   ```

## Notes

- **Wi-Fi:** these boards fail to log in at full transmit power (reported as "wrong password"), so `wifi.py` sets 8.5 dBm.
- **HTTPS:** the TLS handshake to caydas.cloud takes ~5 s on the C3, so the upload timeout is 20 s.
- **Upload interval:** 300 s by default; the server can change it via `config.interval` in its response.
