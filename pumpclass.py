from beerpiconstants import *

class pumpClass:

    def __init__(self,pumpMethod,plugId):
        self.pumpMethod=pumpMethod
        self.plugId=plugId
        self.status=0

        if self.pumpMethod==PUMP_METHOD_ENERGENIE:
            self.energenieObj=Energie(self.plugId)

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
