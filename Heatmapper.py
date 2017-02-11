#!/usr/bin/python
"""
Heatmapper gui and interpolator code
"""

import sys
from iwlist_parser import scanner
import matplotlib.pyplot as pp
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pylab import imread
from scipy.interpolate import Rbf
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg


class HeatMapperMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(HeatMapperMainWindow, self).__init__(parent)
        self.prepare()
        self.createwidgets()
        self.layoutwidgets()
        self.createconnections()

    def prepare(self):
        self.setWindowTitle("Heatmapper")
        self.openfname = None
        self.customlayoutpresence = False
        self.placeholder = open('placeholder.png')
        self.heatmapdict = {'x':[],'y':[]}
        self.scantimes = 0
        self.bssid = set([])
        self.essid = set([])
        self.essidtobssid = {}
        self.appw = 1200
        self.apph = 800
        self.canvasw = 1050
        self.canvash = 700

    def createwidgets(self):

        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        importAction = QAction(QIcon('import.png'), 'Import', self)
        importAction.setShortcut('Ctrl+I')
        importAction.setStatusTip('Import layout')
        importAction.triggered.connect(self.importplan)

        saveAction = QAction(QIcon('save.png'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Heatmap')
        saveAction.triggered.connect(self.saveheatmap)

        self.statusBar()

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(importAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addAction(exitAction)

        self.centralwidget = QWidget()

        self.imagewidget = FigureCanvasQTAgg(self.createimage(self.placeholder))

        self.dropselect = QComboBox()
        self.dropselect.addItems(['BSSID', 'ESSID'])

        self.apssidlist = QListWidget()
        self.clearbutton = QPushButton('CLEAR')

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

    def layoutwidgets(self):
        self.setCentralWidget(self.centralwidget)
        self.imagewidget.setFixedSize(QSize(self.canvasw,self.canvash))
        self.hbox.addWidget(self.imagewidget)
        self.vbox.addWidget(self.dropselect)
        self.vbox.addWidget(self.apssidlist)
        self.vbox.addWidget(self.clearbutton)
        self.hbox.addLayout(self.vbox)
        self.hbox.addStretch(1)
        self.centralwidget.setLayout(self.hbox)
        self.showMaximized()
        self.setFixedSize(self.appw, self.apph)

    def createconnections(self):
        self.dropselect.activated.connect(self.updateQlist)
        self.clearbutton.clicked.connect(self.clearlist)
        self.apssidlist.itemClicked.connect(self.updateheatmapbyselect)

    def updateheatmapbycoords(self, event):
        if self.customlayoutpresence:
            x = event.pos().x()
            y = event.pos().y()
            if x in self.heatmapdict['x']:
                position = self.heatmapdict['x'].index(x)
                if y in self.heatmapdict['y'] and self.heatmapdict['y'].index(y) == position:
                    return
            self.scantimes += 1
            self.preparedicts(x, y, scanner())
            self.preparerssi()
            self.updateQlist()
            if self.scantimes > 1:
                self.hbox.removeWidget(self.imagewidget)
                self.imagewidget.hide()
                self.imagewidget.setParent(None)
                heatmapfig = self.rbfheatmap(self.openfname)
                self.imagewidget = FigureCanvasQTAgg(heatmapfig)
                pp.close(heatmapfig)
                self.imagewidget.setFixedSize(QSize(self.canvasw,self.canvash))
                self.hbox.insertWidget(0, self.imagewidget)
                self.imagewidget.setFocusPolicy(Qt.ClickFocus)
                self.imagewidget.setFocus()
                self.imagewidget.mousePressEvent = self.updateheatmapbycoords

    def updateheatmapbyselect(self):
        self.preparerssi()
        if self.scantimes > 1:
            self.hbox.removeWidget(self.imagewidget)
            self.imagewidget.hide()
            self.imagewidget.setParent(None)
            heatmapfig = self.rbfheatmap(self.openfname)
            self.imagewidget = FigureCanvasQTAgg(heatmapfig)
            pp.close(heatmapfig)
            self.imagewidget.setFixedSize(QSize(self.canvasw,self.canvash))
            self.hbox.insertWidget(0, self.imagewidget)
            self.imagewidget.setFocusPolicy(Qt.ClickFocus)
            self.imagewidget.setFocus()
            self.imagewidget.mousePressEvent = self.updateheatmapbycoords

    def updateQlist(self):
        self.apssidlist.clear()
        if self.dropselect.currentText() == 'ESSID':
            self.apssidlist.addItems(list(self.essid))
        else:
            self.apssidlist.addItems(list(self.bssid))

    def createimage(self, image):
        layout = imread(image)
        image_width = len(layout[0])
        image_height = len(layout)
        fig = pp.figure(frameon=False)
        fig.set_size_inches(image_width/100, image_height/100)
        ax = pp.Axes(fig, [0.,0.,1.,1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        pp.imshow(layout)
        return fig

    def importplan(self):
        fd = QFileDialog.getOpenFileName(self, 'Open file',
                '/home/alex/projects/diplom/wifi-heatmap-master/input')
        if not fd:
            return
        self.openfname = fd
        self.hbox.removeWidget(self.imagewidget)
        self.imagewidget.hide()
        self.imagewidget.setParent(None)
        layoutfig = self.createimage(str(self.openfname))
        self.imagewidget = FigureCanvasQTAgg(layoutfig)
        pp.close(layoutfig)
        self.hbox.insertWidget(0,self.imagewidget)
        self.imagewidget.setFocusPolicy(Qt.ClickFocus)
        self.imagewidget.setFocus()
        self.imagewidget.mousePressEvent = self.updateheatmapbycoords
        self.imagewidget.setFixedSize(QSize(self.canvasw,self.canvash))
        self.customlayoutpresence = True

    def rbfheatmap(self, openfname, save=False):
        layout = imread(str(openfname))

        rbfx = self.heatmapdict['x']
        rbfy = self.heatmapdict['y']
        rssi = self.rssiforrbf

        image_width = len(layout[0])
        image_height = len(layout)

        grid_width = self.canvasw
        grid_height = self.canvash

        num_x = image_width / 4
        num_y = num_x / (image_width / image_height)

        x = np.linspace(0, grid_width, num_x)
        y = np.linspace(0, grid_height, num_y)

        gx, gy = np.meshgrid(x, y)
        gx, gy = gx.flatten(), gy.flatten()

        # create interpolator instance
        rbf = Rbf(rbfx, rbfy, rssi, function='linear')
        z = rbf(gx, gy)
        z = z.reshape((num_y, num_x))

        # Render the interpolated data to the plot
        fig = pp.figure(frameon=False)
        fig.set_size_inches(image_width/100, image_height/100)
        ax = pp.Axes(fig, [0.,0.,1.,1.])
        ax.set_axis_off()
        fig.add_axes(ax)

        #add plan to figure
        pp.imshow(layout)

        #overlay semitransparent heatmap over plan
        ax.imshow(z, vmin=-85, vmax=-25, extent=(0, image_width, image_height, 0), cmap='RdYlGn',
                     alpha=0.7, aspect='auto')

        if save:
            pp.savefig(str(save), dpi=100)

        return fig

    def preparedicts(self, x, y, scandict):
        self.heatmapdict['x'].append(x)
        self.heatmapdict['y'].append(y)
        for item in scandict.keys():
            if not item in self.heatmapdict.keys():
                self.heatmapdict[item] = [-85]*(self.scantimes - 1)
            if scandict[item]['essid']not in self.essidtobssid:
                self.essidtobssid[scandict[item]['essid']] = set([item])
            else:
                self.essidtobssid[scandict[item]['essid']].add(item)
        for item in self.heatmapdict.keys():
            if not item in scandict.keys():
                if item is not 'x':
                    if item is not 'y':
                        self.heatmapdict[item].append(-85)
        for key, val in scandict.iteritems():
            self.heatmapdict[key].append(int(val['quality']))
        for key in self.heatmapdict.keys():
            if key is not 'x':
                if key is not 'y':
                    self.bssid.add(key)
        for i in self.bssid:
            if i in scandict.keys():
                self.essid.add(scandict[i]['essid'])

    def preparerssi(self):
        self.rssiforrbf = []
        dictforrbf = {}
        selectedessid = None
        selectedbssid = None

        if self.dropselect.currentText() == 'ESSID':
            if self.apssidlist.currentItem():
                selectedessid = str(self.apssidlist.currentItem().text())
            else:
                selectedbssid = self.bssid
        else:
            if self.apssidlist.currentItem():
                selectedbssid = str(self.apssidlist.currentItem().text())
                selectedbssid = [selectedbssid]
            else:
                selectedbssid = self.bssid
        if selectedessid:
            for item in self.essidtobssid[selectedessid]:
                dictforrbf[item] = self.heatmapdict[item]
        else:
            for i in selectedbssid:
                dictforrbf[i] = self.heatmapdict[i]

        length = len(dictforrbf[dictforrbf.keys()[0]])
        for num in range(0,length):
            max = -200
            for key in dictforrbf.keys():
                if max < dictforrbf[key][num]:
                    max = dictforrbf[key][num]
            self.rssiforrbf.append(max)

    def clearlist(self):
         for i in range(self.apssidlist.count()):
            item = self.apssidlist.item(i)
            self.apssidlist.setItemSelected(item, False)

    def saveheatmap(self):
        if self.openfname:
            savefname = QFileDialog.getSaveFileName(self, 'Save Heatmap',
                                                    '/home/alex/projects/diplom/wifi-heatmap-master/input')
            self.rbfheatmap(self.openfname, savefname)

def main():

    app = QApplication(sys.argv)
    ex = HeatMapperMainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
