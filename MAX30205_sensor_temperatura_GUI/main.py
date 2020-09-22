from PyQt5 import QtCore, QtGui, QtWidgets
from threading import *
import sys
import time
import random

import smbus

from gui import Ui_MainWindow
from state import State

state = State()

class I2CThread(Thread):
    def __init__(self, state):
        Thread.__init__(self)
        self.state = state
        self.is_running = True
        self.start()

    def run(self):
        while self.is_running:
            if(self.state.start == True):
                #self.state.append_value(random.random()*40)
                self.state.append_value(self.leerTemp())
            time.sleep(1)

    def leerTemp(self):
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

i2c_thread = I2CThread(state)

def close_threads():
    i2c_thread.is_running = False
    i2c_thread.join()

app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(close_threads)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow(state)
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec_())
