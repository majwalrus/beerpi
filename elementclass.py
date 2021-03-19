import time
import glob
import os
import RPi.GPIO as GPIO

import logging
logging.basicConfig(filename='beerpi.log',level=logging.DEBUG)
from beerpiconstants import *


class ElementControlClass:
    mainPower = 10  # The intensity of the element when under taperTemp
    taperPower = 7  # Lower intensity to this when over targetTemp but under targetTemp
    overPower = 0   # Intensity of element when over targetTemp

    targetTemp = 76
    taperTemp = 75

    elementGPIO = 0

    name = ""

    def __init__(self,gpio):
        #if gpio==0:
        #    return False

        self.elementGPIO=gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(int(self.elementGPIO),GPIO.OUT)
        GPIO.output(int(self.elementGPIO),GPIO.LOW)

        pass

    def checkGPIOValid(self):
        if self.elementGPIO<0:
            logging.warning("ERROR: checkGPIOValid - invalid GPIO assignment")
            return False    #   more detailed checking at a later date
        return True

    def switchOn(self):
        if not self.checkGPIOValid():
            return False
        GPIO.output(int(self.elementGPIO), GPIO.HIGH)

    def switchOff(self):
        if not self.checkGPIOValid():
            return False
        GPIO.output(int(self.elementGPIO), GPIO.LOW)

    def setTaperPower(self,pow):
        if pow>10:
            return False
        if pow<0:
            return False
        self.taperPower=pow
        return True

    def setOverPower(self,pow):
        if pow>10:
            return False
        if pow<0:
            return False
        self.overPower=pow
        return True

    def setMainPower(self,pow):
        if pow>10:
            return False
        if pow<0:
            return False
        self.mainPower=pow
        return True

    def setTargetTemp(self,temp):
        if temp>105:
            return False
        if temp<0:
            return False
        self.targetTemp=temp
        return True

    def setTaperTemp(self,temp):
        if temp>105:
            return False
        if temp<0:
            return False
        self.taperTemp=temp
        return True

    def elementControl(self,time,temp):
        power=self.returnPower(temp)
        elementstate=self.returnPowerState(time,power)
        if elementstate:
            self.switchOn()
        else:
            self.switchOff()


    def returnPower(self,temp):
        if temp<self.targetTemp and temp<self.taperTemp:
            return self.mainPower
        if temp>self.targetTemp:
            return self.overPower
        if temp>self.taperTemp and temp<self.targetTemp:
            return self.taperPower
        return 0

    def returnPowerState(self,time,pow):                #   there are simpler ways to code this, but this provides
        if pow>10 or time>10 or pow<1 or time<1:        #   the smoothest power curve I could think off currently.
            return False
        if pow>0 and time==1:   # if cycle 1 and if power is more than 1 then element must be on
            return True
        if pow==10:             # if power is at max then element must be on
            return True

        if pow==2 and (time==6):
            return True
        if pow==3 and (time==5 or time==8):
            return True
        if pow==4 and (time==4 or time==6 or time==9):
            return True
        if pow==5 and (time==3 or time==5 or time==7 or time==9):
            return True
        if pow==6 and not (time==2 or time==5 or time==7 or time==10):
            return True
        if pow==7 and not (time==4 or time==7 or time==10):
            return True
        if pow==8 and not (time==5 or time==10):
            return True
        if pow==9 and not time==10:
            return True
        return False

    def dumpData(self):
        print "GPIO: "+str(self.elementGPIO)+"\n"
        print "Main Power: "+str(self.mainPower)+"\n"
        print "Taper Power: "+str(self.taperPower)+"\n"
        print "Over Power: "+str(self.overPower)+"\n"
        print "Target Temp: "+str(self.targetTemp)+"\n"
        print "Taper Temp: "+str(self.taperTemp)+"\n"
