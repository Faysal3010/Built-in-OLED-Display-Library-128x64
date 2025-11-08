# ==========================================================
# Faysal_SSD1306.py
# Author: Faysal Mahmud
# GitHub: https://github.com/Faysal3010
# Compatible with SSD1306 OLED 128x32 and 128x64 (I2C)
# ==========================================================

from machine import I2C, Pin
import time

SET_CONTRAST = 0x81
DISPLAY_ALL_ON_RESUME = 0xA4
DISPLAY_ALL_ON = 0xA5
NORMAL_DISPLAY = 0xA6
INVERT_DISPLAY = 0xA7
DISPLAY_OFF = 0xAE
DISPLAY_ON = 0xAF
SET_DISPLAY_OFFSET = 0xD3
SET_COM_PINS = 0xDA
SET_VCOM_DETECT = 0xDB
SET_DISPLAY_CLOCK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_MULTIPLEX = 0xA8
SET_LOW_COLUMN = 0x00
SET_HIGH_COLUMN = 0x10
SET_START_LINE = 0x40
MEMORY_MODE = 0x20
COLUMN_ADDR = 0x21
PAGE_ADDR = 0x22
COM_SCAN_INC = 0xC0
COM_SCAN_DEC = 0xC8
SEG_REMAP = 0xA0
CHARGE_PUMP = 0x8D
EXTERNAL_VCC = 0x1
SWITCH_CAP_VCC = 0x2


class Faysal_SSD1306:
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.width * self.pages)
        self.init_display()

    # ---------- Low Level Write Functions ----------
    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, b'\x00' + bytearray([cmd]))

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40' + buf)

    # ---------- Display Initialization ----------
    def init_display(self):
        self.write_cmd(DISPLAY_OFF)
        self.write_cmd(SET_DISPLAY_CLOCK_DIV)
        self.write_cmd(0x80)
        self.write_cmd(SET_MULTIPLEX)
        self.write_cmd(self.height - 1)
        self.write_cmd(SET_DISPLAY_OFFSET)
        self.write_cmd(0x00)
        self.write_cmd(SET_START_LINE | 0x00)
        self.write_cmd(CHARGE_PUMP)
        self.write_cmd(0x14)
        self.write_cmd(MEMORY_MODE)
        self.write_cmd(0x00)
        self.write_cmd(SEG_REMAP | 0x1)
        self.write_cmd(COM_SCAN_DEC)
        self.write_cmd(SET_COM_PINS)
        self.write_cmd(0x12 if self.height == 64 else 0x02)
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(0xCF)
        self.write_cmd(SET_PRECHARGE)
        self.write_cmd(0xF1)
        self.write_cmd(SET_VCOM_DETECT)
        self.write_cmd(0x40)
        self.write_cmd(DISPLAY_ALL_ON_RESUME)
        self.write_cmd(NORMAL_DISPLAY)
        self.write_cmd(DISPLAY_ON)
        self.fill(0)
        self.show()

    # ---------- Core Display Control ----------
    def fill(self, color):
        fill_byte = 0xFF if color else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = fill_byte

    def pixel(self, x, y, color):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        page = y // 8
        shift = y % 8
        index = x + self.width * page
        if color:
            self.buffer[index] |= (1 << shift)
        else:
            self.buffer[index] &= ~(1 << shift)

    def text(self, string, x, y, color=1):
        from framebuf import FrameBuffer, MONO_VLSB
        fb = FrameBuffer(self.buffer, self.width, self.height, MONO_VLSB)
        fb.text(string, x, y, color)

    # ---------- Display Update ----------
    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 + page)
            self.write_cmd(SET_LOW_COLUMN | 0x02)  
            self.write_cmd(SET_HIGH_COLUMN | 0x10)
            start = self.width * page
            end = start + self.width
            self.write_data(self.buffer[start:end])

    # ---------- Extra Features ----------
    def invert(self, invert=True):
        self.write_cmd(INVERT_DISPLAY if invert else NORMAL_DISPLAY)

    def poweroff(self):
        self.write_cmd(DISPLAY_OFF)

    def poweron(self):
        self.write_cmd(DISPLAY_ON)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def scroll(self, start=0, stop=None):
        if stop is None:
            stop = self.pages - 1
        self.write_cmd(0x26) 
        self.write_cmd(0x00)
        self.write_cmd(start)
        self.write_cmd(0x00)
        self.write_cmd(stop)
        self.write_cmd(0x00)
        self.write_cmd(0xFF)
        self.write_cmd(0x2F) 

    def stop_scroll(self):
        self.write_cmd(0x2E)

