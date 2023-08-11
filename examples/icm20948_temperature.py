# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

i2c = I2C(1, sda=Pin(2), scl=Pin(3))
icm = icm20948.ICM20948(i2c)

_ = icm.temperature  # Dummy read to initialize the sensor
time.sleep(0.05)


while True:
    print(f"Temperature: {icm.temperature}°C")
    print()
    time.sleep(1)
