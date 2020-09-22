import time

class State:
    def __init__(self):
        self.xValues = []
        self.yValues = []
        self.startTime = time.time()
        self.refreshPeriod = 1
        self.start = False

    def append_value(self, value):
        if(value > -0.001 and value < 0.001):
            return
        self.xValues.append(time.time() - self.startTime)
        self.yValues.append(value)

    def update_graph(self, graphicsView, lcdNumber):
        if(not graphicsView):
            return

        if(not self.start):
            return

        graphicsView.plot(self.xValues, self.yValues)
        if(len(self.yValues)>0):
            lcdNumber.setProperty("value", self.yValues[-1])

    def toggle_start(self, button):
        self.start = not self.start

        if(self.start):
            button.setText("Pausar")
        else:
            button.setText("Resumir")

    def clear_values(self, graphicsView, lcdNumber, button):
        self.start = False
        self.xValues = []
        self.yValues = []
        self.startTime = time.time()
        graphicsView.clear()
        lcdNumber.setProperty("value", 0.00)
        button.setText("Pausar")
        self.start = True

        
