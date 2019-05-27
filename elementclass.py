import time
import glob
import os
import RPi.GPIO as GPIO

class ElementControlClass:
    mainPower = 10  # The intensity of the element when under taperTemp
    taperPower = 6  # Lower intensity to this when over targetTemp but under targetTemp
    overPower = 0   # Intensity of element when over targetTemp

    targetTemp = 76
    taperTemp = 75

    elementGPIO = 0

    name = ""

    def __init__(self,gpio):
        if gpio==0:
            return False

        self.elementGPIO=gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(int(self.elementGPIO),GPIO_OUT)
        pass

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

    def returnPower(self,temp):
        if temp<self.targetTemp and temp<self.taperTemp:
            return self.mainPower
        if temp>self.targetTemp:
            return self.overPower
        if temp>self.taperTemp and temp<self.targetTemp:
            return self.taperPower
        return 0

    def returnPowerState(self,time,pow):
        if pow>10 or time>10 or pow<1 or time<1:
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
        if pow==7 and not (time==4 or time==7 or time==10)
            return True
        if pow==8 and not (time==5 or time==10)
            return True
        if pow==9 and not time==10
            return True
        return False