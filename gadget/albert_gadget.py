#!/usr/bin/env python3
import os
import sys
import time
import logging
import json
import random
import threading

from enum import Enum
from agt import AlexaGadget
from albert import ALBERT

from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, SpeedPercent, MediumMotor

# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
logger = logging.getLogger(__name__)

class MindstormsGadget(AlexaGadget):
    """
    A Mindstorms gadget that performs experiments based on voice commands.
    """

    def __init__(self):
        """
        Performs Alexa Gadget initialization routines and ev3dev resource allocation.
        """
        super().__init__()

        # Ev3dev initialization
        self.leds = Leds()
        self.sound = Sound()
        self.albert = ALBERT()
        self.plate_counter = 0

    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param device_addr: the address of the device we connected to
        """
        self.leds.set_color("LEFT", "GREEN")
        self.leds.set_color("RIGHT", "GREEN")
        logger.info("{} connected to Echo device".format(self.friendly_name))

    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param device_addr: the address of the device we disconnected from
        """
        self.leds.set_color("LEFT", "BLACK")
        self.leds.set_color("RIGHT", "BLACK")
        logger.info("{} disconnected from Echo device".format(self.friendly_name))

    def on_custom_mindstorms_gadget_control(self, directive):
        """
        Handles the Custom.Mindstorms.Gadget control directive.
        :param directive: the custom directive with the matching namespace and name
        """
        try:
            payload = json.loads(directive.payload.decode("utf-8"))
            print("Control payload: {}".format(payload), file=sys.stderr)
            control_type = payload["type"]
            if control_type == "make_plate":
                # make the plate
                self.albert.make_plate()
                self.plate_counter += 1
                self.send_custom_event('Custom.Mindstorms.Gadget', 'plate_finished', {
                    'plate_number': self.plate_counter
                })
            elif control_type == "check_plate":
                # check the plate
                # will need plate number
                number = int(payload["plate_number"])
                if number > self.plate_counter:
                    self.send_custom_event('Custom.Mindstorms.Gadget', 'plate_status', {
                        'plate_number': -1
                    })
                else:
                    refl = self.albert.check_plate()
                    self.send_custom_event('Custom.Mindstorms.Gadget', 'plate_status', {
                        'plate_number': number,
                        'reflectivity': round(refl, 2)
                    })

        except KeyError:
            print("Missing expected parameters: {}".format(directive), file=sys.stderr)

if __name__ == '__main__':
    gadget = MindstormsGadget()

    # Set LCD font and turn off blinking LEDs
    os.system('setfont Lat7-Terminus12x6')
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")

    # Startup sequence
    gadget.sound.play_song((('C4', 'e'), ('D4', 'e'), ('E5', 'q')))
    gadget.leds.set_color("LEFT", "GREEN")
    gadget.leds.set_color("RIGHT", "GREEN")

    # Gadget main entry point
    gadget.main()

    # Shutdown sequence
    gadget.sound.play_song((('E5', 'e'), ('C4', 'e')))
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")
