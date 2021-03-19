import time
import datetime
import glob
import os
import RPi.GPIO as GPIO
import threading

import logging

import configclass

from beerpiconstants import *

class HallEffectClass:
    sensorgpio=0;
    threadRunning=False
    lasttime=0
    clicksperlitre=560      # this will depend on the hall effect monitor used. Might need to declare in constructor.
    clickcount=5
    flowrate=0
    totalclicks=0

    def killThread(self):
        self.threadRunning=False

    def startThread(self):
        self.threadRunning=True
        self.threadSensor.start()

    def calculateFlow(self,count):
        currenttime=datetime.datetime.now()
        delta=currenttime-self.lasttime
        lasttime=currenttime
        litresperminute=((1000000/delta.microseconds)/self.clicksperlitre)*count*60
        return litresperminute

    def returnFlowRate(self):
        if self.threadRunning:
            return self.flowrate
        else:
            return False
    
    def returnTotalClicks(self):
        if self.threadRunning:
            return self.totalclicks
        else:
            return False

    def returnVolume(self):
        if self.threadRunning:
            return self.totalclicks/self.clicksperlitre
        else:
            return False

    def resetClicks(self):
        self.totalclicks=0
        return

    def __init__(self,gpio):
        self.sensorgpio=gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpio,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.threadSensor = threading.Thread(target=self.sensorThreadFunction)
        self.threadSensor.daemon=True
        pass
    
    def sensorThreadFunction(self):
        self.lasttime=datetime.datetime.now()

        while self.threadRunning:
            logging.info("sensorThread - GPIO "+str(self.sensorgpio)+" Running")
            count=0
            while (count<self.clickcount):      # Does a certain number of loops before calculating flow rate. Note clicks always updated.
                GPIO.wait_for_edge(self.sensorgpio, GPIO.FALLING)
                count+=1
                self.totalclicks+=1
            flow=self.calculateFlow(count)
            self.flowrate=flow
            logging.info("sensorThread - "+str(self.sensorgpio)+", "+str(flow*60)+" L/m "+str(self.totalclicks)+" total clicks")

        logging.info("sensorThread - GPIO "+str(self.sensorgpio)+" Stopped")
        

