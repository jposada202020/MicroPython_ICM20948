# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

i2c = I2C(sda=Pin(8), scl=Pin(9))  # Correct I2C pins for UM FeatherS2
icm = icm20948.ICM20948(i2c)


while True:
    print(f"Temperature: {icm.temperature}°C")
    print()
    time.sleep(1)
