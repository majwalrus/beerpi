from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.screenmanager import *
from kivy.lang import Builder
from functools import partial

import os
import threading
import time
import ConfigParser


import pihealth
import probeclass
import configclass
import elementclass
#
# Global Variables
# ==================
# Used as globals as less overheads and in will be updated by using multiple threads.

glob_config = configclass.BeerConfig() # must be defined first, as values in here used in other declarations.

glob_pihealth = pihealth.PiHealth()
glob_beerProbes = probeclass.BeerProbes()
glob_hltElement = elementclass.ElementControlClass(int(glob_config.gpioHLT))
glob_boilElement = elementclass.ElementControlClass(int(glob_config.gpioBoil))

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

    def update(self, dt):
        self.piTempLabel = glob_pihealth.piTempStr
        self.hltTempLabel = glob_beerProbes.returnStrProbeValFromName(glob_config.sensorHLT)
        self.boilTempLabel = glob_beerProbes.returnStrProbeValFromName(glob_config.sensorBoil)

        self.hltSetTempLabel = str(glob_config.valHLTTargetTemp)
        self.boilSetTempLabel = str(glob_config.valBoilTargetTemp)
        self.setHLTElement(glob_config.boolHLTElementOn)
        self.setBoilElement(glob_config.boolBoilElementOn)
        pass

    def setHLTElement(self,status):
        if status:
            glob_config.boolHLTElementOn=True
            self.ids['hltelementbutton'].text="ELEMENT CONTROL ON"
            self.ids['hltelementbutton'].background_color = 0.3, 0.1, 0.1, 1
        else:
            glob_config.boolHLTElementOn=False
            self.ids['hltelementbutton'].text = "ELEMENT CONTROL OFF"
            self.ids['hltelementbutton'].background_color = 0.1, 0.1, 0.2, 1

    def setBoilElement(self,status):
        if status:
            glob_config.boolBoilElementOn=True
            self.ids['boilelementbutton'].text="ELEMENT CONTROL ON"
            self.ids['boilelementbutton'].background_color = 0.3, 0.1, 0.1, 1
        else:
            glob_config.boolBoilElementOn=False
            self.ids['boilelementbutton'].text = "ELEMENT CONTROL OFF"
            self.ids['boilelementbutton'].background_color = 0.1, 0.1, 0.2, 1


    def addhlt(self, *args):
        glob_config.valHLTTargetTemp +=1
        glob_config.valHLTTaperTemp=glob_config.valHLTTargetTemp-1

    def subhlt(self, *args):
        glob_config.valHLTTargetTemp +=-1
        glob_config.valHLTTaperTemp=glob_config.valHLTTargetTemp-1

    def toggleHLTElement(self, *args):
        if glob_config.boolHLTElementOn:
            self.setHLTElement(False)
        else:
            self.setHLTElement(True)
        pass

    def toggleBoilElement(self, *args):
        if glob_config.boolBoilElementOn:
            self.setBoilElement(False)
        else:
            self.setBoilElement(True)
        pass

    def __init__(self, **kwargs):
        super(BeerStatus, self).__init__(**kwargs)
        self.menu = DefaultRightBar()
        self.add_widget(self.menu)


class BeerHLT(Screen):

    def update(self, dt):
        pass


class BeerBoil(Screen):

    def update(self, dt):
        pass


class BeerConfig(Screen):

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerConfig, self).__init__(**kwargs)
        self.menu = ConfigRightBar()
        self.add_widget(self.menu)

class BeerSensors(Screen):

    arr_LabelProbe=[]
    arr_LabelAssignHLT=[]
    arr_LabelAssignBoil=[]
    arr_ButtonHLT=[]
    arr_ButtonBoil=[]
    tmp_LabelVal=StringProperty()
    tmp_Label=Label()
    tmp_Button=Button()
    lab_hltProbe=Label()
    lab_boilProbe=Label()


    def update(self,dt):

        num=0
        for tmp_probe in glob_beerProbes.probeList:
            self.tmp_LabelVal=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr
            self.arr_LabelProbe[num].text=self.tmp_LabelVal
            num+=1
        self.lab_hltProbe.text="HLT Probe : "+glob_config.sensorHLT
        self.lab_boilProbe.text="Boil Probe : "+glob_config.sensorBoil
        num=0
        for tmp_probe in glob_beerProbes.probeList:
            self.arr_LabelAssignHLT[num].text = ""
            self.arr_LabelAssignBoil[num].text = ""
            if tmp_probe.name==glob_config.sensorHLT:
                self.arr_LabelAssignHLT[num].text="HLT"
            if tmp_probe.name==glob_config.sensorBoil:
                self.arr_LabelAssignBoil[num].text="Boil"
            num+=1

        pass

    def hltAssign(self,num, *args):
        glob_config.sensorHLT=glob_beerProbes.probeList[num].name
        glob_config.updateConfigFile()
        pass

    def boilAssign(self,num, *args):
        glob_config.sensorBoil=glob_beerProbes.probeList[num].name
        glob_config.updateConfigFile()
        pass

    def __init__(self, **kwargs):
        super(BeerSensors,self).__init__(**kwargs)
        self.menu = ConfigRightBar()
        self.add_widget(self.menu)
        self.add_widget(Label(text="Sensor Setup",top=self.top+220))
        self.add_widget(Label(text="Total Temperature Probes : "+str(glob_beerProbes.countProbes()),top=self.top+190))

        self.lab_hltProbe = Label(text="HLT Probe : "+glob_config.sensorHLT, top=self.top + 160)
        self.lab_boilProbe = Label(text="Boil Probe : "+glob_config.sensorBoil, top=self.top + 130)

        #self.add_widget(self.lab_hltProbe)
        #self.add_widget(self.lab_boilProbe)


        num=0
        for tmp_probe in glob_beerProbes.probeList:
            self.arr_LabelProbe.append(Label(text=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr+" INIT", top=self.top + 90 - (num*40),x=self.x-250))
            self.arr_LabelAssignHLT.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-120))
            self.arr_LabelAssignBoil.append(Label(text="None INIT", top=self.top + 90 - (num*40),x=self.x-80))
            self.add_widget(self.arr_LabelProbe[num])
            self.add_widget(self.arr_LabelAssignHLT[num])
            self.add_widget(self.arr_LabelAssignBoil[num])
            self.arr_ButtonHLT.append(Button(text="Set HLT", top=415 - (num*40), x=self.x+360, size=(65,30), size_hint=(None,None) ))
            self.arr_ButtonHLT[num].bind(on_press=partial(self.hltAssign,num))
            self.arr_ButtonBoil.append(Button(text="Set Boil", top=415 - (num*40), x=self.x+450, size=(65,30), size_hint=(None,None) ))
            self.arr_ButtonBoil[num].bind(on_press=partial(self.boilAssign,num))
            self.add_widget(self.arr_ButtonHLT[num])
            self.add_widget(self.arr_ButtonBoil[num])
            num+=1


class BeerScreenManagement(ScreenManager):
    pass


class SimpleApp(App):
    screenmanager = Builder.load_file("main.kv")

    def update(self, dt):
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

def checkElementData():
    glob_hltElement.setMainPower(glob_config.valHLTMainPower)
    glob_hltElement.setTaperPower(glob_config.valHLTTaperPower)
    glob_hltElement.setOverPower(glob_config.valHLTOverPower)
    glob_boilElement.setMainPower(glob_config.valBoilMainPower)
    glob_boilElement.setTaperPower(glob_config.valBoilTaperPower)
    glob_boilElement.setOverPower(glob_config.valBoilOverPower)

    glob_hltElement.setTargetTemp(glob_config.valHLTTargetTemp)
    glob_hltElement.setTaperTemp(glob_config.valHLTTaperTemp)

    glob_boilElement.setTargetTemp(glob_config.valBoilTargetTemp)
    glob_boilElement.setTaperTemp(glob_config.valBoilTaperTemp)

    #print "HLT:\n"
    #glob_hltElement.dumpData()
    #print "Boil:\n"
    #glob_boilElement.dumpData()



#
# THREADS
#  These are used to do the intermittent monitoring and updating global values to reduce overhead of the
#  main program calling slow processes all the time.

def piHealthThread():
    while True:
        time.sleep(5)
        glob_pihealth.getPiTemp()

def tempProbeThread():
    while True:
        print("Calling updateProbes")
        glob_beerProbes.updateProbes()
        #time.sleep(0.5)


def elementThreadControl(): #   Actions element class
    timer=1
    while True:
        #print "\nCheck Element Thread\n"
        checkElementData()
        if glob_config.boolHLTElementOn:
            if not (glob_beerProbes.returnStrProbeValFromName(glob_config.sensorHLT)=="" or glob_beerProbes.returnStrProbeValFromName(glob_config.sensorHLT)=="false"):
                #print glob_beerProbes.returnStrProbeValFromName(glob_config.sensorHLT)+" : "+str(timer)+"\n"
                glob_hltElement.elementControl(timer,float(glob_beerProbes.returnStrProbeValFromName(glob_config.sensorHLT)))
        else:
            glob_hltElement.switchOff()

        if glob_config.boolBoilElementOn:
            if not (glob_beerProbes.returnStrProbeValFromName(glob_config.sensorBoil)=="" or glob_beerProbes.returnStrProbeValFromName(glob_config.sensorBoil)=="false"):
                #print glob_beerProbes.returnStrProbeValFromName(glob_config.sensorBoil)+" : "+str(timer)+"\n"
                glob_boilElement.elementControl(timer,float(glob_beerProbes.returnStrProbeValFromName(glob_config.sensorBoil)))
        else:
            glob_boilElement.switchOff()
        time.sleep(1)
        timer+=1
        if timer>10:
            timer=1
#
# MAIN
#  This is the main startup code. This will start the relevant threads, run the startup config code and
#  then start the Kivy App.

if __name__ == '__main__':

    #print(glob_config.valHLTTargetTemp)

    threadTemp = threading.Thread(target=tempProbeThread)
    threadTemp.daemon=True
    threadTemp.start()

    #threadHealth = threading.Thread(target=piHealthThread)
    #threadHealth.daemon=True
    #threadHealth.start()

    #threadHealth = threading.Thread(target=elementThreadControl)
    #threadHealth.daemon=True
    #threadHealth.start()

    SimpleApp().run()
