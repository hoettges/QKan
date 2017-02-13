from PyQt4.QtGui import *
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
class Presenter():
    fig=None
    ax=None
    def __init__(self):
        self.fig = plt.figure()


    def __del__(self):
        del self.fig

    def addLine(self,x,y,color='b',name=""):
        self.ax = self.fig.add_subplot(111)
        self.ax.plot_date(x, y, '{}-'.format(color),label=name)
    def makeCanvas(self):
        return FigureCanvas(self.fig)

    def getWidget(self):
        qw = QWidget()
        canv = FigureCanvas(self.fig)
        canv.setParent(qw)
        NavigationToolbar(canv, qw, True)
        plt.legend()
        plt.gcf().autofmt_xdate()
        formatter = matplotlib.dates.DateFormatter('%H:%M')
        plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
        return qw

    def setAxLabels(self,x,y):
        plt.xlabel(x)
        plt.ylabel(y)