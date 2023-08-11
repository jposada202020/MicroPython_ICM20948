# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya

import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

i2c = I2C(1, sda=Pin(2), scl=Pin(3))
icm = icm20948.ICM20948(i2c)


while True:
    accx, accy, accz = icm.acceleration
    gyrox, gyroy, gyroz = icm.gyro
    print(f"x: {accx}m/s², y: {accy},m/s² z: {accz}m/s²")
    print(f"x: {gyrox}°/s, y: {gyroy}°/s, z: {gyroz}°/s")
    print()
    time.sleep(1)
