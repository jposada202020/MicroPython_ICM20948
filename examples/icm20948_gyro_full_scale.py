# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
icm = icm20948.ICM20948(i2c)

icm.gyro_full_scale = icm20948.FS_250_DPS

while True:
    for gyro_full_scale in icm20948.gyro_full_scale_values:
        print("Current Gyro full scale setting: ", icm.gyro_full_scale)
        for _ in range(10):
            gyrox, gyroy, gyroz = icm.gyro
            print("x:{:.2f}°/s, y:{:.2f}°/s, z:{:.2f}°/s".format(gyrox, gyroy, gyroz))
            print()
            time.sleep(0.5)
        icm.gyro_full_scale = gyro_full_scale
