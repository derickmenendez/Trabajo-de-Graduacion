from PyQt5 import QtCore, QtGui, QtWidgets
from threading import *
import sys
import time
import random
import numpy as np

import smbus

from gui_temp import Ui_MainWindow as UITemp
from gui_max30102 import Ui_MainWindow as UIMAX30102
from gui_ecg import Ui_MainWindow as UIECG
from state import State
import hrcalc
from max30102 import MAX30102

state = State()
sensor_name = sys.argv[1]

class I2CThread(Thread):
    def __init__(self, state, sensor_name):
        Thread.__init__(self)
        self.state = state
        self.is_running = True
        self.sensor_name = sensor_name
        self.start()

    def run(self):
        if(self.sensor_name == 'MAX30102'):
            self.sensor = MAX30102()
            self.ir_data = []
            self.red_data = []
            self.bpms = []
            self.spo2s = []

        while self.is_running:
            if(self.state.start):
                if(self.sensor_name == 'temp'):
                    self.state.append_value(random.random()*5 + 25)
                    #self.state.append_value(self.modTemp())
                elif(self.sensor_name == 'ecg'):
                    self.state.append_value(random.random()*100 + 200)
                    #self.state.append_value(self.modTemp())
                elif(self.sensor_name == 'MAX30102'):
                    #self.state.append_value(random.random()*20 + 70)
                    #self.state.append_value_2(random.random()*10 + 80)
                    bpm, spo2 = self.read_max30102()
                    if(bpm > 0 and spo2 > 0):
                        self.state.append_value(bpm)
                        self.state.append_value_2(spo2)
            
            time.sleep(self.state.refreshPeriod)
        
        if(self.sensor):
            self.sensor.shutdown()

    def modTemp(self):
        bus=smbus.SMBus(1)
        address=0x48
        registro=0x00
        d=bus.read_i2c_block_data(address,registro)

        firstB=d[0]
        secondB=d[1]
        tempInt=float(firstB)
        tempDeci=float(secondB)
        tempDeci=tempDeci/float(256.0)

        tempTotal = tempInt + tempDeci
        
        #print(tempTotal)
        return(tempTotal)

    def modECG(self):
        bus=smbus.SMBus(1)
        address=0x57
        registro=0x00
        d=bus.read_i2c_block_data(address,registro,0x00)

        firstB=d[0]
        secondB=d[1]
        
        print(firstB)
        print(secondB)
        return(0)

    def read_max30102(self):
        num_bytes = self.sensor.get_data_present()
        #print('numbytes' + str(num_bytes))
        if num_bytes > 0:
            # grab all the data and stash it into arrays
            while num_bytes > 0:
                red, ir = self.sensor.read_fifo()
                num_bytes -= 1
                self.ir_data.append(ir)
                self.red_data.append(red)
                #print("{0}, {1}".format(ir, red))

            while len(self.ir_data) > 100:
                self.ir_data.pop(0)
                self.red_data.pop(0)

            if len(self.ir_data) == 100:
                bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(self.ir_data, self.red_data)
                if valid_bpm and bpm > 30 and bpm < 200 and spo2 > 50:
                    self.bpms.append(bpm)
                    while len(self.bpms) > 25:
                        self.bpms.pop(0)
                    bpm_mean = np.mean(self.bpms)
                    self.spo2s.append(spo2)
                    while len(self.spo2s) > 25:
                        self.spo2s.pop(0)
                    spo2_mean = np.mean(self.spo2s)
                    if (np.mean(self.ir_data) < 50000 and np.mean(self.red_data) < 50000):
                        bpm_mean = 0
                        #print("Finger not detected")
                    #print("BPM: {0}, SpO2: {1}".format(bpm_mean, spo2))
                    return float(bpm_mean), float(spo2_mean)
            
        return 0,0

i2cThread = I2CThread(state, sensor_name)

def close_threads():
    i2cThread.is_running = False
    i2cThread.join()

time.sleep(2)

app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(close_threads)
MainWindow = QtWidgets.QMainWindow()
if(sensor_name == 'temp'):
    ui = UITemp(state)
elif(sensor_name == 'ecg'):
    ui = UIECG(state)
elif(sensor_name == 'MAX30102'):
    ui = UIMAX30102(state)
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec_())
