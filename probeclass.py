import time
import glob
import os

# Class BeerTempProbe
#  This handles an individual probe




class BeerTempProbe:
    name =""
    devfolder =""
    datafile =""
    probeval=0
    probevalstr=""

    def __init__(self, n, fld, fil):
        self.name=n
        self.devfolder=fld
        self.datafile=fil

    def readRaw(self):
        f = open(self.datafile, 'r')
        lines = f.readlines()
        f.close()
        return lines
        
    def updateProbe(self):
        lines=self.readRaw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.readRaw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            tempstr = lines[1][equals_pos+2:]
            tempc = float(tempstr) / 1000.0
            self.probeval=round(tempc,1)
            self.probevalstr=str(self.probeval)
            

# Class BeerProbes
#   This class handles all of the 1wire probes, and is used to update them and get the
#   values from the individual probes by passing their device name.

class BeerProbes:
    probeList = []
    w1_devdir = '/sys/bus/w1/devices/'

    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        w1_devfolders=glob.glob(self.w1_devdir+'28*')

        for w1_dev in w1_devfolders:
            tmp_probe = BeerTempProbe(w1_dev[len(self.w1_devdir):],w1_dev,w1_dev+'/w1_slave')
            self.probeList.append(tmp_probe)

    def countProbes(self):
        tx=0
        for tmp_probe in self.probeList:
            tx+=1
        return tx

    def dumpData(self):
        for tmp_probe in self.probeList:
            print ("Name: " + tmp_probe.name + " Folder: " + tmp_probe.devfolder + " DataFile: " + tmp_probe.datafile + " Temp: " + str(tmp_probe.probeval))

    def updateProbes(self):
        for tmp_probe in self.probeList:
            tmp_probe.updateProbe()

    def returnStrProbeVal(self, probenum):
        tx=0
        for tmp_probe in self.probeList:
            if probenum==tx:
                return tmp_probe.probevalstr
            tx+=1
        return "false"

    def returnFloatProbeVal(self, probenum):
        tx=0
        for tmp_probe in self.probeList:
            if probenum==tx:
                return tmp_probe.probeval
        return -1

    def getProbeNumber(self, probename):
        tx=0
        for tmp_probe in self.probeList:
            if tmp_probe.name==probename:
                return tx
            tx+=1
        return -99

    def returnStrProbeValFromName(self,probename):
        probenum=self.getProbeNumber(probename)
        if probenum==-99:
            return "false"
        return self.returnStrProbeVal(probenum)

    def readNamedProbe(self, probename):
        for tmp_probe in self.probeList:
            if tmp_probe.name==probename:
                return tmp_probe.probeval
        return -1

'''
demonstration code

bp = BeerProbes()

bp.updateProbes()
bp.dumpData()

print "\r\n\n"

tst_name=bp.probeList[1].name
tst_val=bp.readNamedProbe(tst_name)

print (tst_name + " - " + str(tst_val))
'''
