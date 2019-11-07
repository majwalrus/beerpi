from beerpiconstants import *
from gpiozero import Energenie

class pumpClass:

    pumpName = ""
    def __init__(self,pumpMethod,plugId,pumpName):
        self.pumpMethod=pumpMethod
        self.plugId=plugId
        self.status=0

        if self.pumpMethod==PUMP_METHOD_ENERGENIE:
            self.energenieObj=Energenie(self.plugId)

    def sendCommand(self,command):
        if self.pumpMethod==PUMP_METHOD_ENERGENIE:
            if command==1:
                self.energenieObj.on()
            else:
                self.energenieObj.off()

    def setStatus(self,setStatus):
        if not setStatus==self.status:
            self.status=setStatus
            self.sendCommand(self.status)

    def getStatus(self):
        return self.status

    def getMethod(self):
        return self.pumpMethod

    def getId(self):
        return self.plugId

    def safeShutdown(self):
        if self.pumpMethod==PUMP_METHOD_ENERGENIE:
            self.energenieObj.Off()

    def togglePump(self):
        if self.status==1:
            self.setStatus(0)
        else:
            self.setStatus(1)

