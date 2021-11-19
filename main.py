import os
#os.environ['KIVY_GL_BACKEND'] = 'gl'    #   to get around the dreaded segmentation fault if this is an issue.

import logging
logging.basicConfig(filename='beerpi.log', filemode='w', level=logging.DEBUG)
logging.info("STARTING BEERPI")
logging.info("===============\n")


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty, ListProperty
from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.screenmanager import *
from kivy.lang import Builder
from functools import partial
from gpiozero import Energenie

from kivy.core.window import Window # Switch off mouse cursor.
Window.show_cursor = False

import threading
import time
from kivy.config import ConfigParser
import signal

import globalclass

from beerpiconstants import *

#
# Global Variables
# ==================
# Used as globals as less overheads and in will be updated by using multiple threads. This has now been lumped into one class
# for future functionality.
#

globalobj = globalclass.GlobalClass()

#
# KIVY
#

class BeerRightBar:                     #   Deprecated, left in for now
    def defaultBar(self, menuCanvas):
        pass

    def configBar(self, menuCanvas):
        pass

    def drawMenuBar(self, menuBar, menuCanvas):
        switcher = {
            "default": self.defaultBar,
            "config": self.configBar
        }
        func = switcher.get(menuBar, lambda: self.defaultBar)
        func(menuCanvas)

class TopActionBar(Widget):
    piTempLabel = StringProperty()

    def update(self,dt):
        self.piTempLabel = globalobj.pihealth.piTempStr #+ " C"
        self.ids[ "piTempButton" ].text=self.piTempLabel
        logging.info("ActionButton piTempButton updated to %s" % self.piTempLabel)

        pass

    pass

class DefaultRightBar(Widget):
    pass


class ConfigRightBar(Widget):
    pass

class BeerMain(FloatLayout):
    pass

#
#   Main Status Screen
#

class BeerStatus(Screen):
    hltTempLabel = StringProperty()
    boilTempLabel = StringProperty()
    hltSetTempLabel = StringProperty()
    boilSetTempLabel = StringProperty()
    mashoutSetTempLabel = StringProperty()
    rimsoutSetTempLabel = StringProperty()
    pidValue = NumericProperty()
    pidLabel = StringProperty()
    tempLabel=ListProperty(["","","",""])
    settempLabel=ListProperty(["","","",""])
    elementIDS=["hltelementbutton","boilelementbutton","rimselementbutton"]     # list of the IDS for the element control buttons
    pumpIDS=["pump1button","pump2button"]                                       # list of the IDS for the pump control buttons
    flowLabel=ListProperty(["",""])
    firstupdate=True

    def update(self, dt):
        if self.firstupdate:
            self.initPump()
            self.firstupdate=False

        self.pidValue = globalobj.element[DEF_BOIL].taperPower
        self.pidLabel = str(globalobj.element[DEF_BOIL].taperPower) + " %"
        for elementID in LIST_ELEMENTS_ID:  #   Update actual temperature labels
            probeTemp = globalobj.beerprobes.returnStrProbeValFromName(globalobj.config.valElement[elementID].sensorName)
            if probeTemp == "false":
                probeTemp = "--"
            self.tempLabel[elementID] = probeTemp
            logging.info("Temp Label %s updated to %s" % (elementID, globalobj.beerprobes.returnStrProbeValFromName(globalobj.config.valElement[elementID].sensorName)))
        for elementID in LIST_ELEMENTS_ID:  #   Update target temperature labels
            self.settempLabel[elementID]=str(globalobj.config.valElement[elementID].targetTemp)
            logging.info("Temp Label %s updated to %s" % (elementID, globalobj.config.valElement[elementID].targetTemp))


        #   Update the element control buttons
        for elementID in LIST_ELEMENTS_ID:
            if not globalobj.element[elementID].autoControlElement:
                continue
            self.setElement(elementID,globalobj.config.valElement[elementID].elementOn)

        #   Update flow labels
        for flowID in LIST_FLOW_ID:
            flowrate=round(globalobj.flow[flowID].returnFlowRate(),2)
            self.flowLabel[flowID]=str(flowrate)
            logging.info("Flow Label %s updated to %s" % (flowID, flowrate))

        self.menu.update(dt)
        pass


    def setElement(self,elementID,status):
        logging.info("Setting Element status ID=%s, status=%s" % (elementID,status) )
        if status:
            globalobj.config.valElement[elementID].elementOn=True
            self.ids[ self.elementIDS[elementID] ].text="ELEMENT CONTROL ON"
            self.ids[ self.elementIDS[elementID] ].background_color = 0.4, 0.1, 0.1, 1
        else:
            globalobj.config.valElement[elementID].elementOn=False
            self.ids[ self.elementIDS[elementID] ].text="ELEMENT CONTROL OFF"
            self.ids[ self.elementIDS[elementID] ].background_color = 0.1, 0.1, 0.2, 1

    def addhlt(self, *args):
        logging.info("Incrementing HLT Temperature Settings")
        globalobj.config.valElement[DEF_HLT].targetTemp +=1
        globalobj.config.valElement[DEF_HLT].taperTemp +=1

    def subhlt(self, *args):
        logging.info("Decrementing HLT Temperature Settings")
        globalobj.config.valElement[DEF_HLT].targetTemp -=1
        globalobj.config.valElement[DEF_HLT].taperTemp -=1

    def addboil(self, *args):
        logging.info("Incrementing Boil PID Settings")
        globalobj.config.valElement[DEF_BOIL].incTaperPower()

    def subboil(self, *args):
        logging.info("Decrementing Boil PID Settings")
        globalobj.config.valElement[DEF_BOIL].decTaperPower()

    def addrims(self, *args):
        logging.info("Incrementing RIMS target temperature")
        globalobj.config.valElement[DEF_RIMS].targetTemp+=1

    def subrims(self, *args):
        logging.info("Decrementing RIMS target temperature")
        globalobj.config.valElement[DEF_RIMS].targetTemp-=1

    def toggleHLTElement(self, *args):
        logging.info("Toggling HLT Element")
        if globalobj.config.valElement[DEF_HLT].elementOn:
            self.setElement(DEF_HLT,False)
        else:
            self.setElement(DEF_HLT,True)
        pass

    def toggleBoilElement(self, *args):
        logging.info("Toggling Boil Element")
        if globalobj.config.valElement[DEF_BOIL].elementOn:
                self.setElement(DEF_BOIL,False)
        else:
            self.setElement(DEF_BOIL,True)
        pass

    def toggleRIMSElement(self, *args):
        logging.info("Toggling RIMS Element")
        if globalobj.config.valElement[DEF_RIMS].elementOn:
                self.setElement(DEF_RIMS,False)
        else:
            self.setElement(DEF_RIMS,True)
        pass

    def __init__(self, **kwargs):
        super(BeerStatus, self).__init__(**kwargs)
        self.menu = TopActionBar()
        self.add_widget(self.menu)

    def initPump(self):
        pumpID=0
        for tpump in globalobj.pump:
            if not tpump.pumpEnabled:
                pumpID+=1
                continue
            else:
                tpump.setStatus(0)
                self.ids[ self.pumpIDS[pumpID] ].text="%s OFF" % tpump.pumpName
                self.ids[ self.pumpIDS[pumpID] ].background_color = 0.1, 0.1, 0.2, 1
                pumpID+=1


    def setPump(self,pumpID,status):
        logging.info("Setting Pump status ID=%s, status=%s" % (pumpID,status) )
        if status:
            self.ids[ self.pumpIDS[pumpID] ].text="%s ON" % globalobj.pump[pumpID].pumpName
            self.ids[ self.pumpIDS[pumpID] ].background_color = 0.4, 0.1, 0.1, 1
        else:
            self.ids[ self.pumpIDS[pumpID] ].text="%s OFF" % globalobj.pump[pumpID].pumpName
            self.ids[ self.pumpIDS[pumpID] ].background_color = 0.1, 0.1, 0.2, 1

    def togglePump(self, *args):
        logging.info("Toggling Pump %s" % args[0])
        globalobj.pump[args[0]].togglePump()
        self.setPump(args[0],globalobj.pump[args[0]].getStatus())


#
#   Sensor Calibration Screen (TODO)
#

class BeerCalibrate(Screen):

    class SensorRow(EventDispatcher):
        probeNumber=0
        labelStrSensorName=StringProperty()
        labelStrSensorAssign=StringProperty()
        labelStrSensorIce=StringProperty()
        labelStrSensorBoil=StringProperty()



        def __init__(self,name,num,parent):
            self.labelStrSensorName=name
            self.labelStrSensorAssign=""
            self.probeNumber=num

            if globalobj.beerprobes.probeList[num].calLow==-99:
                globalobj.beerprobes.probeList[num].calLow=0.0
            self.labelStrSensorIce=str(globalobj.beerprobes.probeList[num].calLow)

            if globalobj.beerprobes.probeList[num].calHigh==-99:
                globalobj.beerprobes.probeList[num].calHigh=100.0
            self.labelStrSensorBoil=str(globalobj.beerprobes.probeList[num].calHigh)

            self.checkAssignments()

            self.labelSensorName = Label(text=self.labelStrSensorName, top=parent.top + 90 - (num*40),x=parent.x-280)
            parent.add_widget(self.labelSensorName)
            self.labelSensorAssign = Label(text=self.labelStrSensorAssign, top=parent.top + 90 - (num*40),x=parent.x-150)
            parent.add_widget(self.labelSensorAssign)
            self.labelSensorIce = Label(text=self.labelStrSensorIce, top=parent.top + 90 - (num*40),x=parent.x)
            parent.add_widget(self.labelSensorIce)
            self.labelSensorBoil = Label(text=self.labelStrSensorBoil, top=parent.top + 90 - (num*40),x=parent.x+120)
            parent.add_widget(self.labelSensorBoil)

            parent.add_widget(Button(text="+", top=415 - (num*40), x=parent.x+335, size=(30,30), size_hint=(None,None), on_press=partial(parent.incrementIce,num)))
            parent.add_widget(Button(text="-", top=415 - (num*40), x=parent.x+425, size=(30,30), size_hint=(None,None), on_press=partial(parent.decrementIce,num)))

            parent.add_widget(Button(text="+", top=415 - (num*40), x=parent.x+455, size=(30,30), size_hint=(None,None), on_press=partial(parent.incrementBoil,num)))
            parent.add_widget(Button(text="-", top=415 - (num*40), x=parent.x+545, size=(30,30), size_hint=(None,None), on_press=partial(parent.decrementBoil,num)))

        def checkAssignments(self):
            for elementID in LIST_ELEMENTS_ID:
                if self.labelStrSensorName == globalobj.config.valElement[elementID].sensorName:
                    self.labelStrSensorAssign = LIST_ELEMENTS[elementID]

        def dumpData(self):
            strdump="SensorName = %s, SensorAssign = %s, SensorIce = %s, SensorBoil = %s" % (self.labelStrSensorName,self.labelStrSensorAssign,self.labelStrSensorIce,self.labelStrSensorBoil)
            return strdump

        def __str__(self):
            return self.dumpData()

        def update(self,parent):
            self.checkAssignments()
            self.labelSensorAssign.text = self.labelStrSensorAssign
            self.labelSensorIce.text = str(globalobj.beerprobes.probeList[self.probeNumber].calLow)
            self.labelSensorBoil.text = str(globalobj.beerprobes.probeList[self.probeNumber].calHigh)


    listSensorRow = []

    def update(self, dt):
        for sensorRow in self.listSensorRow:
            sensorRow.update(self)

    def incrementIce(self,num,*args):
        globalobj.beerprobes.probeList[num].calLow=round(globalobj.beerprobes.probeList[num].calLow+0.1,1)
        logging.info("Decrementing Ice : %s" % (globalobj.beerprobes.probeList[num].calLow))

    def decrementIce(self,num,*args):
        globalobj.beerprobes.probeList[num].calLow=round(globalobj.beerprobes.probeList[num].calLow-0.1,1)
        logging.info("Decrementing Ice : %s" % (globalobj.beerprobes.probeList[num].calLow))

    def incrementBoil(self,num,*args):
        globalobj.beerprobes.probeList[num].calHigh=round(globalobj.beerprobes.probeList[num].calHigh+0.1,1)
        logging.info("Decrementing Boil : %s" % (globalobj.beerprobes.probeList[num].calHigh))

    def decrementBoil(self,num,*args):
        globalobj.beerprobes.probeList[num].calHigh=round(globalobj.beerprobes.probeList[num].calHigh-0.1,1)
        logging.info("Decrementing Boil : %s" % (globalobj.beerprobes.probeList[num].calHigh))


    def __init__(self, **kwargs):
        super(BeerCalibrate,self).__init__(**kwargs)
        self.menu = ConfigRightBar()            # Ensure the config menu is displayed
        self.add_widget(self.menu)
        self.add_widget(Label(text="Calibrate Sensors",top=self.top+220))
        self.add_widget(Label(text="Total Temperature Probes : "+str(globalobj.beerprobes.countProbes()),top=self.top+190))

        num=0
        for tmp_probe in globalobj.beerprobes.probeList:     # Goes through each probe and creates a new SensorRow class
            logging.info("tmp_probe name: %s" % (tmp_probe.name))
            tempSR=self.SensorRow(tmp_probe.name,num,self)
            self.listSensorRow.append(self.SensorRow(tmp_probe.name,num,self))
            logging.info("Sensor Row Class Vals : %s" % (self.listSensorRow[num]))
            num+=1



class BeerOff(Screen):     # Power off screen

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerOff, self).__init__(**kwargs)
        self.menu = DefaultRightBar()
        self.add_widget(self.menu)

    def confirmShutdown(self, *args):   # function that is called when YES is clicked on shutdown screen
        logging.info("Shutdown Called..")
        for tmpElement in globalobj.element: #   switch off all elements
            logging.info("Element %s off" % tmpElement)
            tmpElement.switchOff()
        for tmpPump in globalobj.pump:
            logging.info("Pump %s off" % tmpPump)
            tmpPump.safeShutdown()
        from subprocess import call
        call("sudo poweroff", shell=True)   # shutdown the Pi

        pass

class BeerConfig(Screen):   # No longer used

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerConfig, self).__init__(**kwargs)
        self.menu = TopActionBar()
        self.add_widget(self.menu)

class BeerSensors(Screen):  # The config screen for the temperature probes, this needs to dynamically create labels and
                            # and buttons allowing the user to select which probe is in the relevant kettle / RIMS etc.
    arr_LabelProbe=[]
    arr_LabelAssignHLT=[]
    arr_LabelAssignBoil=[]
    arr_LabelAssignRIMS=[]
    arr_LabelAssignMash=[]
    arr_ButtonHLT=[]
    arr_ButtonBoil=[]
    arr_ButtonRIMS=[]
    arr_ButtonMash=[]
    tmp_LabelVal=StringProperty()
    tmp_Label=Label()
    tmp_Button=Button()


    def update(self,dt):

        num=0
        for tmp_probe in globalobj.beerprobes.probeList:     # Updates the array of Kivy labels to have the correct info
            self.tmp_LabelVal=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr
            self.arr_LabelProbe[num].text=self.tmp_LabelVal
            num+=1
        num=0
        for tmp_probe in globalobj.beerprobes.probeList:
            self.arr_LabelAssignHLT[num].text = ""
            self.arr_LabelAssignBoil[num].text = ""
            self.arr_LabelAssignRIMS[num].text = ""
            self.arr_LabelAssignMash[num].text = ""
            if tmp_probe.name==globalobj.config.valElement[DEF_HLT].sensorName:
                self.arr_LabelAssignHLT[num].text="HLT"
            if tmp_probe.name==globalobj.config.valElement[DEF_BOIL].sensorName:
                self.arr_LabelAssignBoil[num].text="Boil"
            if tmp_probe.name==globalobj.config.valElement[DEF_RIMS].sensorName:
                self.arr_LabelAssignRIMS[num].text="Mash Out"
            if tmp_probe.name==globalobj.config.valElement[DEF_MASH].sensorName:
                self.arr_LabelAssignMash[num].text="Mash Ret"
            num+=1

    def hltAssign(self,num, *args): # function that is called when an HLT select button is pressed
        globalobj.config.valElement[DEF_HLT].sensorName=globalobj.beerprobes.probeList[num].name
        globalobj.config.updateConfigFile()
        pass

    def boilAssign(self,num, *args):    # function that is called when a boil select button is pressed
        globalobj.config.valElement[DEF_BOIL].sensorName=globalobj.beerprobes.probeList[num].name
        globalobj.config.updateConfigFile()
        pass

    def rimsAssign(self,num, *args):    # function that is called when a boil select button is pressed
        globalobj.config.valElement[DEF_RIMS].sensorName=globalobj.beerprobes.probeList[num].name
        globalobj.config.updateConfigFile()
        pass

    def mashAssign(self,num, *args):    # function that is called when a boil select button is pressed
        globalobj.config.valElement[DEF_MASH].sensorName=globalobj.beerprobes.probeList[num].name
        globalobj.config.updateConfigFile()
        pass

    def __init__(self, **kwargs):
        super(BeerSensors,self).__init__(**kwargs)
        self.menu = TopActionBar()
        self.add_widget(self.menu)
        self.add_widget(Label(text="Sensor Setup",top=self.top+185))
        self.add_widget(Label(text="Total Temperature Probes : "+str(globalobj.beerprobes.countProbes()),top=self.top+170))


        num=0
        for tmp_probe in globalobj.beerprobes.probeList:     # Create an array of labels for all the probes found
            self.arr_LabelProbe.append(Label(text=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr+" INIT", top=self.top + 90 - (num*40),x=self.x-310))
            self.arr_LabelAssignHLT.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-190))
            self.arr_LabelAssignBoil.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-150))
            self.arr_LabelAssignRIMS.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-90))
            self.arr_LabelAssignMash.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-10))

            self.add_widget(self.arr_LabelProbe[num])   # Now display the labels
            self.add_widget(self.arr_LabelAssignHLT[num])
            self.add_widget(self.arr_LabelAssignBoil[num])
            self.add_widget(self.arr_LabelAssignRIMS[num])
            self.add_widget(self.arr_LabelAssignMash[num])

            # Create the HLT and Boil selection buttons
            self.arr_ButtonHLT.append(Button(text="Set HLT", top=415 - (num*40), x=self.x+430, size=(75,30), size_hint=(None,None) ))
            self.arr_ButtonHLT[num].bind(on_press=partial(self.hltAssign,num))
            self.arr_ButtonBoil.append(Button(text="Set Boil", top=415 - (num*40), x=self.x+510, size=(75,30), size_hint=(None,None) ))
            self.arr_ButtonBoil[num].bind(on_press=partial(self.boilAssign,num))
            self.arr_ButtonRIMS.append(Button(text="Set Mash Out", top=415 - (num*40), x=self.x+590, size=(95,30), size_hint=(None,None) ))
            self.arr_ButtonRIMS[num].bind(on_press=partial(self.rimsAssign,num))
            self.arr_ButtonMash.append(Button(text="Set Mash Ret", top=415 - (num*40), x=self.x+690, size=(95,30), size_hint=(None,None) ))
            self.arr_ButtonMash[num].bind(on_press=partial(self.mashAssign,num))
            self.add_widget(self.arr_ButtonHLT[num])
            self.add_widget(self.arr_ButtonBoil[num])
            self.add_widget(self.arr_ButtonRIMS[num])
            self.add_widget(self.arr_ButtonMash[num])
            num+=1

class BeerScreenManagement(ScreenManager):
    pass

class SimpleApp(App):   # The app class for the kivy side of the project
    screenmanager = Builder.load_file("main.kv")
    
    configjson = '''
    [   
        {
            "type"      :   "title",
            "title"     :   "Hot Liquor Tank (HLT) Settings"
        },
        {
            "type"      :   "numeric",
            "title"     :   "Taper Temperature",
            "desc"      :   "Default temperature the software starts to taper the element power. This starts before the target temperature to reduce overshoots.",
            "section"   :   "HLT",
            "key"       :   "tapertemp"
        },
        {
            "type"      :   "numeric",
            "title"     :   "Tapered Power",
            "desc"      :   "Default percentage power to use when taper temperature hit.",
            "section"   :   "HLT",
            "key"       :   "taperpower"
        },
        {
            "type"  :   "title",
            "title" :   "Boil Settings"
        },
        {
            "type"      :   "numeric",
            "title"     :   "Taper Temperature",
            "desc"      :   "Default temperature the software starts to taper the element power. This starts before the boil starts to reduce the risk of a boil over.",
            "section"   :   "Boil",
            "key"       :   "tapertemp"
        },
        {
            "type"      :   "numeric",
            "title"     :   "Tapered Power",
            "desc"      :   "Default percentage power to use when taper temperature hit and throughout the boil.",
            "section"   :   "Boil",
            "key"       :   "taperpower"
        },
        {
            "type" : "title",
            "title" : "Recirculation Infusion Mash System (RIMS) Settings"
        },
        {
            "type" : "bool",
            "title" : "Enable RIMS",
            "desc" : "Enable RIMS subsystem within software",
            "section" : "RIMS",
            "key" : "enabled",
            "values" : ["0","auto"]
        },
        {
            "type"      :   "numeric",
            "title"     :   "Target Temperature",
            "desc"      :   "Default setting for the system to aim for in the mash.",
            "section"   :   "RIMS",
            "key"       :   "targettemp"
        },
                {
            "type"      :   "numeric",
            "title"     :   "Max Temperature",
            "desc"      :   "Default setting for the system to ensure the mash is never heated more than this amount over the target temperature.",
            "section"   :   "RIMS",
            "key"       :   "maxtemp"
        }


        
    ]
    '''

    def update(self, dt):   # Update, and make sure passes on to the various Kivy screens so they get updated.
        statusscreen = self.screenmanager.get_screen('Status')
        statusscreen.update(dt)

        sensorscreen = self.screenmanager.get_screen('Sensors')
        sensorscreen.update(dt)

        calibratescreen = self.screenmanager.get_screen('Calibrate')
        calibratescreen.update(dt)

        #topactionbar = self.wid

    def build(self):
        Clock.schedule_interval(self.update, 1)
        self.icon='/home/pi/programming/beerpi/onyx_32px_icon.png'
        logging.info("APP LOGO: %s" %self.get_application_icon()) 
        return self.screenmanager

    def build_settings(self,settings):
        settings.add_json_panel('Settings',globalobj.config.config, data=self.configjson)


#
#
#

def checkElementData(): # This ensures that the element classes have the correct data in case of changes
    for elementID in LIST_ELEMENTS_ID:
        globalobj.element[elementID].setMainPower(globalobj.config.valElement[elementID].mainPower)
        globalobj.element[elementID].setTaperPower(globalobj.config.valElement[elementID].taperPower)
        globalobj.element[elementID].setOverPower(globalobj.config.valElement[elementID].overPower)
        globalobj.element[elementID].setTargetTemp(globalobj.config.valElement[elementID].targetTemp)
        globalobj.element[elementID].setTaperTemp(globalobj.config.valElement[elementID].taperTemp)
        globalobj.element[elementID].setMaxTemp(globalobj.config.valElement[elementID].maxTemp)

#
# THREADS
#  These are used to do the intermittent monitoring and updating global values to reduce overhead of the
#  main program calling slow processes all the time.

def piHealthThread():
    while True:
        time.sleep(5)                   # this observes the temperature of the Pi and may monitor CPU usage
        globalobj.pihealth.getPiTemp()       # in the future, and indeed may even control a cooling fan.

def tempProbeThread():                  # this updates and caches the data from the temperature probes in the global
    while True:                         # values which the rest of the project uses.
        globalobj.beerprobes.updateProbes()
        time.sleep(0.05)

def checkProbeValid(probename):
    if globalobj.beerprobes.returnStrProbeValFromName(probename) == "":
        logging.warning("checkProbeValid - Blank Probe Name")
        return False
    if globalobj.beerprobes.returnStrProbeValFromName(probename) == "false":
        logging.warning("checkProbeValid - False returned from beerprobes")
        return False
    return True


def elementThreadControl():             # This controls the elements, it has 100 cycles of which the SSR controlling
    timer=0                             # the relevant element will be feathered if necessary, so if set at 50%
    while True:                         # it will be switched off and on once every second.
        checkElementData()

        for elementID in LIST_ELEMENTS_ID:                  #   Check each element in turn
            if globalobj.config.valElement[elementID].elementOn: #   Is the element switch on?
                                                            #   Is the sensor data valid?
                if checkProbeValid(globalobj.config.valElement[elementID].sensorName):
                                                            #   Yes, so send timer info onto element control
                    
                    if globalobj.element[elementID].isRIMS: #   If element is a RIMS element then set the current flowrate
                        logging.info("elementThreadControl - setting RIMS flow rate to %s" % (globalobj.flow[DEF_RIMSFLOW].returnFlowRate()))
                        globalobj.element[elementID].setRIMSFlowRate(globalobj.flow[DEF_RIMSFLOW].returnFlowRate())
                        probeTemp = globalobj.beerprobes.returnStrProbeValFromName(globalobj.config.valElement[DEF_MASH].sensorName)
                        logging.info("elementThreadControl - setting RIMS mashout temp to %s" % (probeTemp))
                        globalobj.element[elementID].setRIMSMashOut(probeTemp)



                    globalobj.element[elementID].elementControl(timer,float(globalobj.beerprobes.returnStrProbeValFromName(globalobj.config.valElement[elementID].sensorName)))
                else:                                       #   No, make sure switch off
                    globalobj.element[elementID].switchOff()
            else:
                globalobj.element[elementID].switchOff()         #   Element control off, so make sure set off

        time.sleep(0.5)
        timer+=1
        if timer>99:
            timer=0

def pumpThreadControl():             # This controls the energie plugs connected to the pumps. PLACEHOLDER IN CASE UPGRADING THE CONTROL BOARD
    while True:

        #globalobj.pump[0].setStatus(1)
        time.sleep(3)
        #globalobj.pump[0].setStatus(0)
        time.sleep(3)


#
# MAIN
#  This is the main startup code. This will start the relevant threads, run the startup config code and
#  then start the Kivy App.

if __name__ == '__main__':
    threadTemp = threading.Thread(target=tempProbeThread)
    threadTemp.daemon=True
    logging.info("Starting Probe thread ...")
    threadTemp.start()

    threadHealth = threading.Thread(target=piHealthThread)
    threadHealth.daemon=True
    logging.info("Starting Health thread ...")
    threadHealth.start()

    threadHealth = threading.Thread(target=elementThreadControl)
    threadHealth.daemon=True
    logging.info("Starting Element thread ...")
    threadHealth.start()

    threadPump = threading.Thread(target=pumpThreadControl)
    threadPump.daemon=True
    logging.info("Starting Pump thread ....")
    threadPump.start()

    logging.info("Starting Kivy App...")
    SimpleApp().run()

