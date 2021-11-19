import time
import glob
import os
import RPi.GPIO as GPIO
import math


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
    isRIMS = False
    rimsflowrate = 0
    maxTemp = 0
    rimsmashout = 0

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
        logging.info("elementClass - GPIO %s switched on" % (self.elementGPIO))
        GPIO.output(int(self.elementGPIO), GPIO.HIGH)

    def switchOff(self):
        if not self.autoControlElement:
            return False
        if not self.checkGPIOValid():
            return False
        logging.info("elementClass - GPIO %s switched off" % (self.elementGPIO))
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

    def setMaxTemp(self, temp):
        self.maxTemp=temp
        return True

    def elementControl(self,time,temp):
        logging.info("elementControl: time %s, temp %s, isRIMS %s" % (time,temp, self.isRIMS))
        if not self.autoControlElement:
            return False
        if self.isRIMS:
            self.elementRIMSControl(time,temp)
            return
        power=self.returnPower(temp)
        #logging.info("elementControl: power %s" % (power))
        elementstate=self.returnPowerState(time,power)
        if elementstate:
            self.switchOn()
        else:
            self.switchOff()


    def returnPower(self,temp):
        logging.info("returnPower - temp %s" % (temp))
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
        logging.info("returnPowerState - time %s, pow %s" % (time,pow))
        if pow>100 or time>(self.totalcycles-1) or pow<1 or time<0:
            return False
        if pow==100:
            return True
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
    
    def setRIMS(self,isRIMS):
        self.isRIMS = isRIMS
        return True

    def setRIMSFlowRate(self,flowrate):
        self.rimsflowrate=float(flowrate)
        return True

    def setRIMSMashOut(self,temp):
        self.rimsmashout=float(temp)
        return True

    def elementRIMSControl(self,time,temp):
        
        t_ambient = DEFAULT_AMBIENT_TEMPERATURE

        h_air = 50      #   approximated

        r_pipe          = (((CONST_PIPEOUTER+CONST_PIPEINSULATION)/1000) * math.log(CONST_PIPEOUTER / CONST_PIPEINNER)) / (2 * CONST_PIPEK)

        if CONST_PIPEINSULATION==0:
            r_insulation=0
        else:
            r_insulation    = (((CONST_PIPEOUTER+CONST_PIPEINSULATION)/1000) * math.log((CONST_PIPEOUTER+CONST_PIPEINSULATION) / CONST_PIPEOUTER)) / (2 * CONST_INSULATIONK)

        r_overall       = r_pipe+r_insulation+(1/h_air)
        Q               = (temp - t_ambient) / +r_overall
        heat_loss       = math.pi * ((CONST_PIPEOUTER+CONST_PIPEINSULATION)/1000) * Q
        logging.info("RIMS calcs: Q = %s, r_pipe = %s, r_insulation = %s, r_overall = %s," % (Q,r_pipe,r_insulation,r_overall))
        logging.info("RIMS Heat Loss Calculation = %s" % (heat_loss))

        if self.rimsflowrate==0:    #   Safety mechanism, if the wort is not flowing ensure the element is off
            logging.info("RIMS wort flow not detected, element switched off")
            self.switchOff()
            return        

        energy_required = self.rimsflowrate * 1000 * 4.2 * (self.maxTemp + self.targetTemp - temp)
        logging.info("RIMS Water Energy Required = %s" % (energy_required))

        if temp>self.targetTemp:
            logging.info("RIMS - mash at or above required temperature, element off")
            self.switchOff()
            return

        if self.rimsmashout>(self.maxTemp + self.targetTemp):
            logging.info("RIMS - mash out over max temp, element off")
            self.switchOff()
            return


        total_energy = energy_required + heat_loss
        element_strength = CONST_ELEMENTSTRENGTH
        
        if element_strength<total_energy:
            logging.info("RIMS - total energy required more than 100 percent so element switched on")
            self.switchOn()
        else:
            pow = round((total_energy / CONST_ELEMENTSTRENGTH) * 100,0)
            if pow==0:
                self.switchOff()
                return
            if self.returnPowerState(time, pow):
                self.switchOn()
            else:
                self.switchOff()
        return