# Driver for the HW-675's 0.42" 72x40 SSD1306 OLED (I2C 0x3C, SDA=GPIO5, SCL=GPIO6).
# The panel sits in the middle of the controller's 128-column RAM, so we shift columns by 28.
from machine import I2C, Pin
import ssd1306

WIDTH = 72
HEIGHT = 40
COL_OFFSET = 28


class OLED(ssd1306.SSD1306_I2C):
    def __init__(self, i2c=None):
        i2c = i2c or I2C(0, sda=Pin(5), scl=Pin(6), freq=400_000)
        super().__init__(WIDTH, HEIGHT, i2c)
        self.write_cmd(0xAD)  # internal current reference, needed on this panel
        self.write_cmd(0x30)

    def show(self):
        self.write_cmd(0x21)  # column range
        self.write_cmd(COL_OFFSET)
        self.write_cmd(COL_OFFSET + WIDTH - 1)
        self.write_cmd(0x22)  # page range
        self.write_cmd(0)
        self.write_cmd(HEIGHT // 8 - 1)
        self.write_data(self.buffer)
