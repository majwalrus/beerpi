import os
import logging
import time
import RPi.GPIO as GPIO

logging.basicConfig(filename='halleffect.log',level=logging.DEBUG)
logging.info("STARTING HALLEFFECT")
logging.info("===============\n")

os.environ['KIVY_GL_BACKEND'] = 'gl'    #   to get around the dreaded segmentation fault

import halleffectclass
import configclass

from beerpiconstants import *

glob_config = configclass.BeerConfig() # must be defined first, as values in here used in other declarations.

halltest = halleffectclass.HallEffectClass(19)


def main():
    try:
        halltest.startThread()
        logging.info("Program Started ...")
        while True:
            time.sleep(0.5)
            pass
    except KeyboardInterrupt:
        halltest.killThread()
        GPIO.cleanup()
        exit(0)


if __name__ == '__main__':
    main()
