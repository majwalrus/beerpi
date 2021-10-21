import time
import glob
import os
import RPi.GPIO as GPIO

import logging
logging.basicConfig(filename='beerpi.log',level=logging.DEBUG)
from beerpiconstants import *


class ElementControlClass:
    mainPower = 100  # The intensity of the element when under taperTemp
    taperPower = 70  # Lower intensity to this when over targetTemp but under targetTemp
    overPower = 0   # Intensity of element when over targetTemp

    targetTemp = 76
    taperTemp = 75
    
    totalcycles = 100   #   For PID calculations

    elementGPIO = 0
    autoControlElement = False

    name = ""

    def __init__(self,gpio,controlElement):
        #if gpio==0:
        #    return False
        
        self.autoControlElement=controlElement
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

    def powerRatios(self,power):    #   power = percentage power to apply
        tOn = (power*self.totalcycles) / 100
        tOff = ((100-power) * self.totalcycles) / 100
        if tOff>tOn:
            rOn = 1
            rOff = tOff/tOn
        else:
            rOn = tOn/tOff
            rOff = 1
        return {"tOn":tOn, "tOff":tOff, "rOn":rOn, "rOff":rOff}


    def switchOn(self):
        if not self.autoControlElement:
            return False
        if not self.checkGPIOValid():
            return False
        GPIO.output(int(self.elementGPIO), GPIO.HIGH)

    def switchOff(self):
        if not self.autoControlElement:
            return False
        if not self.checkGPIOValid():
            return False
        GPIO.output(int(self.elementGPIO), GPIO.LOW)

    def setTaperPower(self,pow):
        if pow>100:
            return False
        if pow<0:
            return False
        self.taperPower=pow
        return True

    def setOverPower(self,pow):
        if pow>100:
            return False
        if pow<0:
            return False
        self.overPower=pow
        return True

    def setMainPower(self,pow):
        if pow>100:
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
        if not self.autoControlElement:
            return False
        power=self.returnPower(temp)
        elementstate=self.returnPowerState(time,power)
        if elementstate:
            self.switchOn()
        else:
            self.switchOff()


    def returnPower(self,temp):
        if not self.autoControlElement:
            return 0
        if temp<self.targetTemp and temp<self.taperTemp:
            return self.mainPower
        if temp>self.targetTemp:
            return self.overPower
        if temp>self.taperTemp and temp<self.targetTemp:
            return self.taperPower
        return 0

    def returnPowerState(self,time,pow):                            #   Calculate the PID power state
        if pow>100 or time>(self.totalcycles-1) or pow<1 or time<0: #   
            return False
        pRatios = self.powerRatios(pow)
        print (pRatios)
        modTime = time % (pRatios['rOn']+pRatios['rOff'])
        if modTime<pRatios['rOn']:
            return True
        return False

    def dumpData(self):
        print ("GPIO: "+str(self.elementGPIO)+"\n")
        print ("Main Power: "+str(self.mainPower)+"\n")
        print ("Taper Power: "+str(self.taperPower)+"\n")
        print ("Over Power: "+str(self.overPower)+"\n")
        print ("Target Temp: "+str(self.targetTemp)+"\n")
        print ("Taper Temp: "+str(self.taperTemp)+"\n")
