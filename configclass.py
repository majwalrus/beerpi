from kivy.config import ConfigParser
import os

import logging
logging.basicConfig(filename='beerpi.log',level=logging.DEBUG)

from beerpiconstants import *

class ValFlow:
    gpio=0

    def __init__(self,gpio):
        self.gpio=gpio

class ValElement:
    mainPower=0
    taperPower=0
    overPower=0
    targetTemp=0
    taperTemp=0
    sensorName=""
    gpio=0
    elementOn=0
    maxTemp=0

    def __init__(self,mainpower,taperpower,overpower,elementon,targettemp,tapertemp,maxtemp,sensorname,tgpio):
        self.mainPower=mainpower
        self.taperPower=taperpower
        self.overPower=overpower
        self.elementOn=elementon
        self.targetTemp=targettemp
        self.taperTemp=tapertemp
        self.sensorName=sensorname
        self.maxTemp=maxtemp
        self.gpio=tgpio
        logging.info("ValElement created - %s" % self.dumpData())

    def dumpData(self):
        strdump="mainPower=%s, taperPower=%s, overPower=%s, elementOn=%s, targetTemp=%s, taperTemp=%s, sensorName=%s, gpio=%s.\n"  % (self.mainPower,self.taperPower,self.overPower,self.elementOn,self.targetTemp,self.taperTemp,self.sensorName,self.gpio)
        return strdump

    def incTaperPower(self):
        self.taperPower+=1
        if self.taperPower>100:
            self.taperPower=100
        return True

    def decTaperPower(self):
        self.taperPower-=1
        if self.taperPower<0:
            self.taperPower=0
        return True

    def __str__(self):
        return self.dumpData()

    def __repr__(self):
        return self.dumpData()


class BeerConfig:

    configFile = './beer.ini'

    valElement = []
    valFlow = []

    config = ConfigParser(allow_no_value=True)

    def __init__(self):
        if not os.path.isfile(self.configFile):     # check config file exists
            self.createDefaultFile()                # it doesn't, so write the default file and continue
            logging.warning("No config file found. Created using default settings.")
        self.loadConfigFile()                       # now read the config file
        logging.info("Config File Loaded")

    def createDefaultFile(self):
        self.config.read(self.configFile)

        self.config.setall("DEFAULT", {'mainpower':'100', 'taperpower':'60', 'overpower':'0', 'targettemp':'100', 'tapertemp':'97', 'maxtemp':'2'})

        self.config.add_section("HLT")              # HLT value section
        self.config.setall("HLT",{'targettemp':'76', 'tapertemp':'72', 'taperpower':'50', 'gpio':'6'})
        
        self.config.add_section("Boil")             # Boil value section
        self.config.setall("Boil",{'targettemp':'100', 'tapertemp':'96', 'taperpower':'70', 'gpio':'5'})

        self.config.add_section("RIMS")             # RIMS value section
        self.config.setall("RIMS",{'targettemp':'65', 'tapertemp':'67', 'taperpower':'0', 'gpio':'13', 'enabled':'auto', 'maxtemp':'2'})

        self.config.add_section("Mash")             # Mash value section, dummy for monitoring only
        self.config.setall("Mash",{'targettemp':'0', 'tapertemp':'0', 'taperpower':'0', 'gpio':'0'})


        self.config.add_section("Flow")
        for tempFlowID in LIST_FLOW_ID:
            self.config.set("Flow",LIST_FLOW[tempFlowID],str(LIST_FLOW_GPIO[tempFlowID]))

        self.config.add_section("Sensors")          # Sensors  value section

        for tempElement in LIST_ELEMENTS:
            self.config.set("Sensors",tempElement,"")

        self.config.add_section("Calibration")      # Sensors calibration section (TODO)

        self.config.write()                         # Now write the default value file

    def getConfig(self,section,value,fallback):
        if not self.config.has_section(section):            # check section exists, this stops exception errors
            logging.info("Config Section - "+section+" does not exist, creating")
            self.config.add_section(section)                # it doesn't so add it for future reference
            self.config.set(section,value,fallback)         # now add the value and fallback
            return fallback                                 # return fallback
        else:
            logging.info("Config Section - "+section+" found")
            if not self.config.has_option(section,value):   # check value exists
                logging.info("Config Value - "+section+":"+value+" not found")
                self.config.set(section, value, fallback)   # it doesn't so add it and set it to fallback
                return fallback
            else:
                logging.info("Config Value - "+section+":"+value+" found")
                return self.config.get(section,value)  # value exists so attempt to get value, if not fallback


    def loadConfigFile(self):
        self.config.read(self.configFile)

        for tempElement in LIST_ELEMENTS:
            tMainPower=int(self.getConfig(tempElement,"mainpower","10"))
            tTaperPower=int(self.getConfig(tempElement,"taperpower","6"))
            tOverPower=int(self.getConfig(tempElement,"overpower","2"))
            tTargetTemp=int(self.getConfig(tempElement,"targettemp","100"))
            tTaperTemp=int(self.getConfig(tempElement,"tapertemp","97"))
            tMaxTemp=int(self.getConfig(tempElement,"maxtemp","2"))
            tSensor=self.getConfig("Sensors",tempElement,"")
            tGPIO=self.getConfig(tempElement,"gpio","0")
            self.valElement.append(ValElement(tMainPower,tTaperPower,tOverPower,False,tTargetTemp,tTaperTemp,tMaxTemp,tSensor,tGPIO))

        for tempFlow in LIST_FLOW:
            self.valFlow.append(ValFlow(int(self.getConfig("Flow",tempFlow,"0"))))

        for tempArr in self.valElement:
            print(tempArr)

    def updateConfigFile(self):
        self.config.read(self.configFile)   # Read original file 
                                            # (quirk of using kivy, as write uses the last read file, this in case we ever have more than
                                            # one configuration file at a later date.

        # Update sensor settings in configparser
        self.config.set("Sensors","hlt",self.valElement[DEF_HLT].sensorName)
        self.config.set("Sensors","boil",self.valElement[DEF_BOIL].sensorName)
        self.config.set("Sensors","rims",self.valElement[DEF_RIMS].sensorName)
        self.config.set("Sensors","mash",self.valElement[DEF_MASH].sensorName)

        # Now write the new file
        self.config.write()

    def returnConfigVal(self,value,id):
        if value=="TaperPower":
            if id==DEF_HLT:
                return self.valHLTTaperPower
            if id==DEF_BOIL:
                return self.val





