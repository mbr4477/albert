#!/usr/bin/env python3
import nxt.brick
import nxt.locator
from nxt.sensor import *
import time
from nxt.motor import * 

TILT_DEGREES = 110
TILT_MOTOR_POWER = 15
PLATE_ROTATION_DEGREES = 810
ROTATE_MOTOR_POWER = 25

class Workstation(object):
    def __init__(self):
        self.brick = nxt.locator.find_one_brick(method=nxt.locator.Method(bluetooth=False))
        self.color = Color20(self.brick, PORT_4)
        self.tilt_motor = Motor(self.brick, PORT_B)
        self.rotate_motor = Motor(self.brick, PORT_C)

    def get_reflectivity(self):
        return self.color.get_reflected_light(Type.COLORRED) / 512.0

    def swab(self):
        self.tilt_motor.turn(TILT_MOTOR_POWER, TILT_DEGREES)
        self.rotate_motor.turn(ROTATE_MOTOR_POWER,PLATE_ROTATION_DEGREES)
        self.tilt_motor.turn(-TILT_MOTOR_POWER, TILT_DEGREES)

    def check_status(self):
        self.tilt_motor.turn(TILT_MOTOR_POWER, TILT_DEGREES)
        self.color.set_light_color(Type.COLORRED)
        time.sleep(1)
        refl = self.get_reflectivity()
        self.color.set_light_color(Type.COLORNONE)
        self.tilt_motor.turn(-TILT_MOTOR_POWER, TILT_DEGREES)
        return refl
                

if __name__ == '__main__':
    # Test code
    w = Workstation()
    w.check_status()