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
    flowrate=0              # Litres per second
    totalclicks=0

    def killThread(self):
        self.threadRunning=False

    def startThreads(self):
        self.threadRunning=True
        self.threadSensor.start()
        self.threadVolume.start()

    def calculateFlow(self,count):
        currenttime=datetime.datetime.now()
        delta=currenttime-self.lasttime
        lasttime=currenttime
        litresperminute=((1000000/delta.microseconds)/self.clicksperlitre)*count*60
        return litresperminute

    def returnFlowRate(self):
        if self.threadRunning:
            return round(self.flowrate/60,2)
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

    def __init__(self,gpio,autostart):
        self.sensorgpio=gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpio,GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Create the two references for the threads. Importantly these are not started here, they are stated with startThreads
        self.threadSensor = threading.Thread(target=self.sensorThreadClicks)
        self.threadSensor.daemon=True

        self.threadVolume = threading.Thread(target=self.sensorThreadVolume)
        self.threadVolume.daemon=True

        if autostart:
            self.startThreads()
            
        pass
    
    def sensorThreadClicks(self):                       # This thread monitors for the GPIO to be triggered by each "click" of the hall effect
        self.lasttime=datetime.datetime.now()           # sensor. It then increments the clickcount used by other functions
        try:
            logging.info("sensorThreadClicks - GPIO "+str(self.sensorgpio)+" Running")
            minicount=0
            while self.threadRunning:
                GPIO.wait_for_edge(self.sensorgpio, GPIO.FALLING)
                self.totalclicks+=1
                minicount+=1
                if minicount>100:
                    logging.info("sensorThreadClicks - GPIO "+str(self.sensorgpio)+" Running")
                    minicount=0

        except RuntimeError:
            logging.info("sensorThreadClicks - GPIO "+str(self.sensorgpio)+" Runtime Error")

        logging.info("sensorThreadClicks - GPIO "+str(self.sensorgpio)+" Stopped")

    def sensorThreadVolume(self):                       # This thread calculates the current flow rate, it updates the value once a second.
        logging.info("sensorThreadVolume - GPIO "+str(self.sensorgpio)+" Running")
        while self.threadRunning:
            previouscount=self.totalclicks
            time.sleep(0.5)
            clicksdone=self.totalclicks-previouscount
            if clicksdone<0:            # This catches negative numbers in case clicks were reset since the volume was last calculated
                clicksdone=0
            self.flowrate=self.calculateFlow(clicksdone)
            logging.info("sensorThreadVolume - "+str(self.sensorgpio)+", "+str(self.flowrate)+" L/m "+str(self.totalclicks)+" total clicks")
        logging.info("sensorThreadVolume - GPIO "+str(self.sensorgpio)+" Running")


