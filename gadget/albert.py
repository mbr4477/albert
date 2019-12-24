#!/usr/bin/env python3

import os
import sys
import time

from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor, MediumMotor
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import ColorSensor
 
from workstation import Workstation

# Define the speeds for each joint
SPEEDS = [50, 15, 50]

# Define the should down and wrist horizontal rotations
DOWN = -0.97
HORZ = 1.23
LID_VBIAS = 0.18
STRIPE_BIAS = 0.07 # amount to center over the stripe

# Keypoints
# VERT - gripper vertical, dish horizontal
# HORZ - gripper horizontal, dish vertical
KP_UP_VERT = [0, 0]
KP_UP_HORZ = [0, HORZ]
KP_DOWN_VERT = [DOWN, 0]
KP_DOWN_HORZ = [DOWN, HORZ]
KP_DOWN_HORZ_LID = [DOWN + LID_VBIAS, HORZ]

# Gripper Constants
GRIP_WIDE = -0.20
GRIP_NARROW = -0.075
GRIP_CLOSED = 0.075

STERILE_COLOR = ColorSensor.COLOR_RED
STORE_COLOR = ColorSensor.COLOR_YELLOW
STATION_COLOR = ColorSensor.COLOR_BLUE
VALID_COLORS = [STERILE_COLOR, STORE_COLOR, STATION_COLOR]

MOVE_PAUSE = 0.5

class ALBERT(object):
    def __init__(self):
        # ev3dev initialization
        self.leds = Leds()
        self.sound = Sound()
        self.arm_base = LargeMotor(OUTPUT_D)
        self.arm_shoulder  = LargeMotor(OUTPUT_C)
        self.arm_wrist = LargeMotor(OUTPUT_B)
        self.arm_gripper = MediumMotor(OUTPUT_A)
        self.station = Workstation()
        self.color_sensor = ColorSensor(INPUT_1)
        self.find_indicator()
        self.rotate_base(STATION_COLOR)
        self.reset_all_motors()

    def find_indicator(self):
        ''' Search for a valid color indicator. '''
        if self.color_sensor.color in VALID_COLORS:
            return
        self.arm_base.on(10)
        while self.color_sensor.color not in VALID_COLORS:
            pass
        self.arm_base.stop()
    
    def reset_all_motors(self):
        ''' Reset all motor tach counts. '''
        self.arm_base.reset()
        self.arm_shoulder.reset()
        self.arm_wrist.reset()
        self.arm_gripper.reset()

    def rotate_base(self, color):
        '''
        Rotate from one color indicator to another.
        Color order is:
            YELLOW <--> BLUE   <--> RED
            STORE  <--> STATION <--> STERILE
        '''
        current_color = self.color_sensor.color
        if current_color == color:
            return
        direction = 1
        if (current_color == STATION_COLOR and color == STERILE_COLOR) or current_color == STORE_COLOR:
            direction = -1
        self.arm_base.on(SPEEDS[0]*direction, block=False)
        while self.color_sensor.color != color:
            pass
        self.arm_base.stop()
        self.arm_base.on_for_rotations(SPEEDS[0], direction*STRIPE_BIAS)

    def make_plate(self):
        ''' Sequence to make a plate. '''
        self.get_plate()
        self.lift_lid()
        self.swab_plate()
        self.lower_lid()
        self.store_plate()

    def check_plate(self):
        ''' Sequence to check plate. '''
        self.get_plate(from_storage=True)
        self.move_to_keypoint(KP_UP_HORZ)
        refl = self.station.check_status()
        self.move_to_keypoint(KP_DOWN_HORZ)
        self.store_plate()
        return refl

    def get_plate(self, from_storage=False):
        ''' 
        Sequence to get a plate and place it in the workstation.
        Post-conditions
            Gripper: WIDE
            Arm:     DOWN
            Base:    STATION
        '''
        src = STORE_COLOR if from_storage else STERILE_COLOR
        self.move_to_keypoint(KP_UP_HORZ)
        self.rotate_base(src)
        self.set_gripper(GRIP_NARROW)
        self.move_to_keypoint(KP_DOWN_HORZ)
        self.set_gripper(GRIP_CLOSED)
        self.move_to_keypoint(KP_UP_HORZ)
        self.rotate_base(STATION_COLOR)
        self.move_to_keypoint(KP_UP_VERT)
        self.move_to_keypoint(KP_DOWN_VERT)
        self.set_gripper(GRIP_WIDE)
        self.move_to_keypoint(KP_DOWN_HORZ)
        
    def lift_lid(self):
        '''
        Lift the dish lid.
        Pre-condition
            Gripper: WIDE
            Arm:     DOWN
            Base:    STATION
        Post-condition
            Gripper: CLOSED
            Arm:     UP
        '''
        self.move_to_keypoint(KP_DOWN_HORZ_LID)
        self.set_gripper(GRIP_CLOSED)
        self.move_to_keypoint(KP_UP_HORZ)
    
    def lower_lid(self):
        '''
        Lower the dish lid.
        Pre-condition
            Gripper: CLOSED
            Arm:     UP
            Base:    STATION
        Post-condition
            Gripper: WIDE
            Arm:     DOWN
        '''
        self.move_to_keypoint(KP_DOWN_HORZ_LID)
        self.set_gripper(GRIP_WIDE)
        
    def swab_plate(self):
        ''' Call the Workstation swab routine. '''
        self.station.swab()

    def store_plate(self):
        ''' Sequence to store a plate. '''
        self.move_to_keypoint(KP_DOWN_VERT)
        self.set_gripper(GRIP_CLOSED)
        self.move_to_keypoint(KP_UP_HORZ)
        self.rotate_base(STORE_COLOR)
        self.move_to_keypoint(KP_DOWN_HORZ)
        self.set_gripper(GRIP_NARROW)
        self.move_to_keypoint(KP_UP_VERT)
        self.rotate_base(STATION_COLOR)
        self.set_gripper(GRIP_CLOSED)

    def move_to_keypoint(self, keypoint):
        ''' Move the should/wrist to a keypoint.'''
        # keypoint is [shoulder, wrist] with unit of rotations
        self.arm_shoulder.on_to_position(SPEEDS[1], keypoint[0] * self.arm_shoulder.count_per_rot)
        self.arm_wrist.on_to_position(SPEEDS[2], keypoint[1] * self.arm_wrist.count_per_rot)
        # pause to let things settle
        time.sleep(MOVE_PAUSE)

    def set_gripper(self, position):
        ''' Set the gripper position. '''
        self.arm_gripper.on_to_position(25, self.arm_gripper.count_per_rot * position)
        time.sleep(MOVE_PAUSE)

if __name__ == "__main__":
    # Test Code
    albert = ALBERT()
    albert.make_plate()