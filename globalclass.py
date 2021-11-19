# global class declaration
#

import os
import time
import glob

import pihealth
import probeclass
import configclass
import elementclass
import pumpclass
import halleffectclass

from beerpiconstants import *

class GlobalClass:

    

    def __init__(self):
        self.config = configclass.BeerConfig()  #   Grab config data, needs to be done first
        self.pihealth = pihealth.PiHealth()     #   Create the pihealth class object

        self.beerprobes = probeclass.BeerProbesOS()
        self.element = []
        self.pump = []
        self.flow = []

        for tempElement in LIST_ELEMENTS_ID:    # Generate the elementclass objects
            self.element.append(elementclass.ElementControlClass(int(self.config.valElement[tempElement].gpio),bool(LIST_ELEMENTS_AUTOCONTROL[tempElement])))

        self.element[DEF_RIMS].setRIMS(True)    # Set the RIMS element

        for tempEnergenie in LIST_ENERGENIE_ID: # Generate the pumpclass objects
            self.pump.append(pumpclass.pumpClass(PUMP_METHOD_ENERGENIE,tempEnergenie,"PUMP E%s" % tempEnergenie))

        for tempFlow in LIST_FLOW_ID:           # Generate the halleffectclass (flow) objects
            self.flow.append(halleffectclass.HallEffectClass(int(self.config.valFlow[tempFlow].gpio),True))

        pass