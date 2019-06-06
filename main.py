import os
os.environ['KIVY_GL_BACKEND'] = 'gl'    #   to get around the dreaded segmentation fault

import logging
logging.basicConfig(filename='beerpi.log', filemode='w', level=logging.DEBUG)
logging.info("STARTING BEERPI")
logging.info("===============\n")


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.screenmanager import *
from kivy.lang import Builder
from functools import partial


import threading
import time
import ConfigParser


import pihealth
import probeclass
import configclass
import elementclass

from beerpiconstants import *

#
# Global Variables
# ==================
# Used as globals as less overheads and in will be updated by using multiple threads.

glob_config = configclass.BeerConfig() # must be defined first, as values in here used in other declarations.

glob_pihealth = pihealth.PiHealth()
glob_beerProbes = probeclass.BeerProbesOS()

glob_element = []

for tempElement in LIST_ELEMENTS_ID:
    glob_element.append(elementclass.ElementControlClass(int(glob_config.valElement[tempElement].gpio)))


#
# KIVY
#

class BeerRightBar:
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


class DefaultRightBar(Widget):
    pass


class ConfigRightBar(Widget):
    pass


class BeerStatus(Screen):
    piTempLabel = StringProperty()
    hltTempLabel = StringProperty()
    boilTempLabel = StringProperty()
    hltSetTempLabel = StringProperty()
    boilSetTempLabel = StringProperty()
    tempLabel=ListProperty(["",""])
    settempLabel=ListProperty(["",""])
    elementIDS=["hltelementbutton","boilelementbutton"]

    def update(self, dt):
        self.piTempLabel = glob_pihealth.piTempStr

        for elementID in LIST_ELEMENTS_ID:  #   Update actual temperature labels
            self.tempLabel[elementID] = glob_beerProbes.returnStrProbeValFromName(glob_config.valElement[elementID].sensorName)
            logging.info("Temp Label %s updated to %s" % (elementID, glob_beerProbes.returnStrProbeValFromName(glob_config.valElement[elementID].sensorName)))
        for elementID in LIST_ELEMENTS_ID:  #   Update target temperature labels
            self.settempLabel[elementID]=str(glob_config.valElement[elementID].targetTemp)
            logging.info("Temp Label %s updated to %s" % (elementID, glob_config.valElement[elementID].targetTemp))


        #   Update the element control buttons
        for elementID in LIST_ELEMENTS_ID:
            self.setElement(elementID,glob_config.valElement[elementID].elementOn)
        pass

    def setElement(self,elementID,status):
        logging.info("Setting Element status ID=%s, status=%s" % (elementID,status) )
        if status:
            glob_config.valElement[elementID].elementOn=True
            self.ids[ self.elementIDS[elementID] ].text="ELEMENT CONTROL ON"
            self.ids[ self.elementIDS[elementID] ].background_color = 0.4, 0.1, 0.1, 1
        else:
            glob_config.valElement[elementID].elementOn=False
            self.ids[ self.elementIDS[elementID] ].text="ELEMENT CONTROL OFF"
            self.ids[ self.elementIDS[elementID] ].background_color = 0.1, 0.1, 0.2, 1

    def addhlt(self, *args):
        logging.info("Incrementing HLT Temperature Settings")
        glob_config.valElement[DEF_HLT].targetTemp +=1
        glob_config.valElement[DEF_HLT].taperTemp +=1

    def subhlt(self, *args):
        logging.info("Decrementing HLT Temperature Settings")
        glob_config.valElement[DEF_HLT].targetTemp -=1
        glob_config.valElement[DEF_HLT].taperTemp -=1

    def toggleHLTElement(self, *args):
        logging.info("Toggling HLT Element")
        if glob_config.valElement[DEF_HLT].elementOn:
            self.setElement(DEF_HLT,False)
        else:
            self.setElement(DEF_HLT,True)
        pass

    def toggleBoilElement(self, *args):
        logging.info("Toggling Boil Element")
        if glob_config.valElement[DEF_BOIL].elementOn:
                self.setElement(DEF_BOIL,False)
        else:
            self.setElement(DEF_BOIL,True)
        pass

    def __init__(self, **kwargs):
        super(BeerStatus, self).__init__(**kwargs)
        self.menu = DefaultRightBar()
        self.add_widget(self.menu)


class BeerCalibrate(Screen):      # # Placeholder, may be used in the future but after changes to the status screen maybe not

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerSensors,self).__init__(**kwargs)
        self.menu = ConfigRightBar()            # Ensure the config menu is displayed
        self.add_widget(self.menu)
        self.add_widget(Label(text="Calibrate Sensore",top=self.top+220))
        self.add_widget(Label(text="Total Temperature Probes : "+str(glob_beerProbes.countProbes()),top=self.top+190))


class BeerOff(Screen):     # Power off screen

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerOff, self).__init__(**kwargs)
        self.menu = DefaultRightBar()
        self.add_widget(self.menu)

    def confirmShutdown(self, *args):   # function that is called when YES is clicked on shutdown screen
        logging.info("Shutdown Called..")
        for tmpElement in glob_element: #   switch off all elements
            logging.info("Element %s off" % tmpElement)
            tmpElement.switchOff()
        from subprocess import call
        call("sudo poweroff", shell=True)   # shutdown the Pi

        pass


class BeerConfig(Screen):   # Main config screen, very little on it but does have the config menu to the right

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerConfig, self).__init__(**kwargs)
        self.menu = ConfigRightBar()
        self.add_widget(self.menu)

class BeerSensors(Screen):  # The config screen for the temperature probes, this needs to dynamically create labels and
                            # and buttons allowing the user to select which probe is in the relevant kettle / RIMS etc.
    arr_LabelProbe=[]
    arr_LabelAssignHLT=[]
    arr_LabelAssignBoil=[]
    arr_ButtonHLT=[]
    arr_ButtonBoil=[]
    tmp_LabelVal=StringProperty()
    tmp_Label=Label()
    tmp_Button=Button()


    def update(self,dt):

        num=0
        for tmp_probe in glob_beerProbes.probeList:     # Updates the array of Kivy labels to have the correct info
            self.tmp_LabelVal=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr
            self.arr_LabelProbe[num].text=self.tmp_LabelVal
            num+=1
        num=0
        for tmp_probe in glob_beerProbes.probeList:
            self.arr_LabelAssignHLT[num].text = ""
            self.arr_LabelAssignBoil[num].text = ""
            if tmp_probe.name==glob_config.valElement[DEF_HLT].sensorName:
                self.arr_LabelAssignHLT[num].text="HLT"
            if tmp_probe.name==glob_config.valElement[DEF_BOIL].sensorName:
                self.arr_LabelAssignBoil[num].text="Boil"
            num+=1

    def hltAssign(self,num, *args): # function that is called when an HLT select button is pressed
        glob_config.valElement[DEF_HLT].sensorName=glob_beerProbes.probeList[num].name
        glob_config.updateConfigFile()
        pass

    def boilAssign(self,num, *args):    # function that is called when a boil select button is pressed
        glob_config.valElement[DEF_BOIL].sensorName=glob_beerProbes.probeList[num].name
        glob_config.updateConfigFile()
        pass

    def __init__(self, **kwargs):
        super(BeerSensors,self).__init__(**kwargs)
        self.menu = ConfigRightBar()            # Ensure the config menu is displayed
        self.add_widget(self.menu)
        self.add_widget(Label(text="Sensor Setup",top=self.top+220))
        self.add_widget(Label(text="Total Temperature Probes : "+str(glob_beerProbes.countProbes()),top=self.top+190))


        num=0
        for tmp_probe in glob_beerProbes.probeList:     # Create an array of labels for all the probes found
            self.arr_LabelProbe.append(Label(text=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr+" INIT", top=self.top + 90 - (num*40),x=self.x-250))
            self.arr_LabelAssignHLT.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-120))
            self.arr_LabelAssignBoil.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-80))

            self.add_widget(self.arr_LabelProbe[num])   # Now display the labels
            self.add_widget(self.arr_LabelAssignHLT[num])
            self.add_widget(self.arr_LabelAssignBoil[num])

            # Create the HLT and Boil selection buttons
            self.arr_ButtonHLT.append(Button(text="Set HLT", top=415 - (num*40), x=self.x+360, size=(65,30), size_hint=(None,None) ))
            self.arr_ButtonHLT[num].bind(on_press=partial(self.hltAssign,num))
            self.arr_ButtonBoil.append(Button(text="Set Boil", top=415 - (num*40), x=self.x+450, size=(65,30), size_hint=(None,None) ))
            self.arr_ButtonBoil[num].bind(on_press=partial(self.boilAssign,num))
            self.add_widget(self.arr_ButtonHLT[num])
            self.add_widget(self.arr_ButtonBoil[num])
            num+=1


class BeerScreenManagement(ScreenManager):
    pass


class SimpleApp(App):   # The app class for the kivy side of the project
    screenmanager = Builder.load_file("main.kv")

    def update(self, dt):   # Update, and make sure passes on to the various Kivy screens so they get updated.
        statusscreen = self.screenmanager.get_screen('Status')
        statusscreen.update(dt)

        sensorscreen = self.screenmanager.get_screen('Sensors')
        sensorscreen.update(dt)

    def build(self):
        Clock.schedule_interval(self.update, 1)
        return self.screenmanager


#
#
#

def checkElementData(): # This ensures that the element classes have the correct data in case of changes


    for elementID in LIST_ELEMENTS_ID:
        glob_element[elementID].setMainPower(glob_config.valElement[elementID].mainPower)
        glob_element[elementID].setTaperPower(glob_config.valElement[elementID].taperPower)
        glob_element[elementID].setOverPower(glob_config.valElement[elementID].overPower)
        glob_element[elementID].setTargetTemp(glob_config.valElement[elementID].targetTemp)
        glob_element[elementID].setTaperTemp(glob_config.valElement[elementID].taperTemp)

    #glob_element[DEF_HLT].setMainPower(glob_config.valHLTMainPower)
    #glob_element[DEF_HLT].setTaperPower(glob_config.valHLTTaperPower)
    #glob_element[DEF_HLT].setOverPower(glob_config.valHLTOverPower)
    #glob_element[DEF_BOIL].setMainPower(glob_config.valBoilMainPower)
    #glob_element[DEF_BOIL].setTaperPower(glob_config.valBoilTaperPower)
    #glob_element[DEF_BOIL].setOverPower(glob_config.valBoilOverPower)

    #glob_element[DEF_HLT].setTargetTemp(glob_config.valHLTTargetTemp)
    #glob_element[DEF_HLT].setTaperTemp(glob_config.valHLTTaperTemp)

    #glob_element[DEF_BOIL].setTargetTemp(glob_config.valBoilTargetTemp)
    #glob_element[DEF_BOIL].setTaperTemp(glob_config.valBoilTaperTemp)



#
# THREADS
#  These are used to do the intermittent monitoring and updating global values to reduce overhead of the
#  main program calling slow processes all the time.

def piHealthThread():
    while True:
        time.sleep(5)                   # this observes the temperature of the Pi and may monitor CPU usage
        glob_pihealth.getPiTemp()       # in the future, and indeed may even control a cooling fan.

def tempProbeThread():                  # this updates and caches the data from the temperature probes in the global
    while True:                         # values which the rest of the project uses.
        glob_beerProbes.updateProbes()

def checkProbeValid(probename):
    if glob_beerProbes.returnStrProbeValFromName(probename) == "":
        logging.warning("checkProbeValid - Blank Probe Name")
        return False
    if glob_beerProbes.returnStrProbeValFromName(probename) == "false":
        logging.warning("checkProbeValid - False returned from beerprobes")
        return False
    return True


def elementThreadControl():             # This controls the elements, it has 10 cycles of which the SSR controlling
    timer=1                             # the relevant element will be feathered if necessary, so if set at 50%
    while True:                         # it will be switched off and on every second.
        checkElementData()

        for elementID in LIST_ELEMENTS_ID:                  #   Check each element in turn
            if glob_config.valElement[elementID].elementOn: #   Is the element switch on?
                                                            #   Is the sensor data valid?
                if checkProbeValid(glob_config.valElement[elementID].sensorName):
                                                            #   Yes, so send timer info onto element control
                    glob_element[elementID].elementControl(timer,float(glob_beerProbes.returnStrProbeValFromName(glob_config.valElement[elementID].sensorName)))
                else:                                       #   No, make sure switch off
                    glob_element[elementID].switchOff()

        time.sleep(0.5)
        timer+=1
        if timer>10:
            timer=1
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

    logging.info("Starting Kivy App...")
    SimpleApp().run()
