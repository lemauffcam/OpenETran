# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:31:30 2017

Draws the system

@author: Matthieu
"""
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QPen, QPainter, QPolygonF, QPainterPath, QColor
from PyQt5.QtCore import pyqtSlot, Qt, QLineF, QPointF
import math

# Reads the conductors' real coordinates
def readCoordinates(self):
    grid = self.paramBox.layout()
    coord = list()
    x = list()
    y = list()

    # coord[0] will be the x coordinate, coord[1] the y coordinate
    coord.append(x)
    coord.append(y)

    for i in range(4,9):
        for j in range(1,3):
            text = grid.itemAtPosition(i,j).widget().text()

            try:
                coord[j-1].append(float(text))
            except ValueError:
                coord[j-1].append(0.0)

    return coord

# Returns the lightning striking distances
def strikeDistance(self):
    grid = self.paramBox.layout()
    slope = grid.itemAtPosition(2,1).widget().text()

    # Slope is the sine of the ground angle
    try:
        groundAngle = float(slope)

    except ValueError:
        groundAngle = 0.0

    current = grid.itemAtPosition(1,1).widget().text()
    icrit = 0.0

    try:
        icrit = float(current)
    except ValueError:
        icrit = 0.0

    # Read coorductors coordinates (set to 0m if empy field)
    coord = readCoordinates(self)

    # Maximum height of coorductor
    yc = max(coord[1])

    # Rc is the strike distance to coorductor
    rc = 10*math.pow(icrit, 0.65)

    if yc < 43:
        beta = 0.37 + 0.17 * math.log(43 - yc)
    else:
        beta = 0.55

    # Rg is the strike distance to ground
    try:
        rg = beta*rc / math.cos( math.radians(groundAngle) )
    except ZeroDivisionError:
        rg = beta*rc

    strikeDist = list()
    strikeDist.append(rg)
    strikeDist.append(rc)

    return strikeDist

# Returns the objects position and height
def readObj(self):
    grid = self.paramBox.layout()
    coord = list()
    x = list()
    y = list()

    # coord[0] will be the x coordinate, coord[1] the y coordinate
    coord.append(x)
    coord.append(y)

    for i in range(10,12):
        for j in range(1,3):
            text = grid.itemAtPosition(i,j).widget().text()

            try:
                coord[j-1].append(float(text))

            except ValueError:
                coord[j-1].append(0.0)

    return coord

def flashRate(self):
    grid = self.paramBox.layout()
    coord = readCoordinates(self)
    strikeDist = strikeDistance(self)
    obj = readObj(self)

    icrit_str = grid.itemAtPosition(1,1).widget().text()
    length_str = grid.itemAtPosition(13,1).widget().text()
    flashDens_str = grid.itemAtPosition(14,1).widget().text()

    try:
        icrit = float(icrit_str)
    except ValueError:
        icrit = 0.0

    try:
        length = float(length_str)
    except ValueError:
        length = 0.0

    try:
        flashDens = int(flashDens_str)
    except ValueError:
        flashDens = 0.0

    # Probability that the 1st stroke current is higher than the critical current
    pFlash = 1/(1 + math.pow(icrit/31, 2.6))

    flashRate = length*flashDens*pFlash

    label = grid.itemAtPosition(15,1).widget()
    label.setText(str(flashRate))

    return

class SysView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Phase view')
        self.setGeometry(100, 100, 1000, 500)

        # Phase view
        mainLayout = QGridLayout()
        paramLayout = QGridLayout()

        self.paramBox = QWidget()

        paramLayout.addWidget(QPushButton('Update view'), 0, 0)

        # Critical current and ground slope
        paramLayout.addWidget(QLabel('I crit [kA]'), 1, 0)
        paramLayout.addWidget(QLineEdit('6.2'), 1, 1)

        paramLayout.addWidget(QLabel('Ground slope [deg]'), 2, 0)
        paramLayout.addWidget(QLineEdit('0'), 2, 1)

        paramLayout.addWidget(QLabel('coorductor'), 3, 0)
        paramLayout.addWidget(QLabel('x (m)'), 3, 1)
        paramLayout.addWidget(QLabel('y (m)'), 3, 2)

        # Phase wires
        paramLayout.addWidget(QLabel('A'), 4, 0)
        paramLayout.addWidget(QLineEdit('-3.81'), 4, 1)
        paramLayout.addWidget(QLineEdit('9.63'), 4, 2)

        paramLayout.addWidget(QLabel('B'), 5, 0)
        paramLayout.addWidget(QLineEdit('0'), 5, 1)
        paramLayout.addWidget(QLineEdit('9.63'), 5, 2)

        paramLayout.addWidget(QLabel('C'), 6, 0)
        paramLayout.addWidget(QLineEdit('3.81'), 6, 1)
        paramLayout.addWidget(QLineEdit('9.63'), 6, 2)

        # Shielding wires
        paramLayout.addWidget(QLabel('S1'), 7, 0)
        paramLayout.addWidget(QLineEdit('-2.08'), 7, 1)
        paramLayout.addWidget(QLineEdit('12.73'), 7, 2)

        paramLayout.addWidget(QLabel('S2'), 8, 0)
        paramLayout.addWidget(QLineEdit('2.08'), 8, 1)
        paramLayout.addWidget(QLineEdit('12.73'), 8, 2)

        # Objects
        paramLayout.addWidget(QLabel('Object'), 9, 0)
        paramLayout.addWidget(QLabel('x (m)'), 9, 1)
        paramLayout.addWidget(QLabel('y (m)'), 9, 2)

        paramLayout.addWidget(QLabel('Left'), 10, 0)
        paramLayout.addWidget(QLineEdit('0'), 10, 1)
        paramLayout.addWidget(QLineEdit('0'), 10, 2)

        paramLayout.addWidget(QLabel('Right'), 11, 0)
        paramLayout.addWidget(QLineEdit('0'), 11, 1)
        paramLayout.addWidget(QLineEdit('0'), 11, 2)

        # Flashover rate parameters
        paramLayout.addWidget(QLabel('Flashover rate parameters'), 12, 0)
        paramLayout.addWidget(QLabel(''), 12, 1)

        paramLayout.addWidget(QLabel('Line length (km)'), 13, 0)
        paramLayout.addWidget(QLineEdit('100'), 13, 1)

        paramLayout.addWidget(QLabel('Flash density (strike/km2/y)'), 14, 0)
        paramLayout.addWidget(QLineEdit('50'), 14, 1)

        paramLayout.addWidget(QLabel('Flashover rate (per year)'), 15, 0)
        paramLayout.addWidget(QLabel(''), 15, 1)

        self.paramBox.setLayout(paramLayout)

        self.drawView = QWidget()

        mainLayout.addWidget(self.paramBox, 0, 0)
        mainLayout.addWidget(self.drawView, 0, 1)
        mainLayout.setColumnStretch(1, 2)

        self.setLayout(mainLayout)

        self.show()

        @pyqtSlot()
        def updateView():
            self.update()

        update = paramLayout.itemAtPosition(0,0).widget()
        update.pressed.connect(updateView)

    def paintEvent(self, e):
        qp = QPainter()

        qp.begin(self)

        self.drawGround(qp)

        # Calculates all coordinates and changes the scales accordingly
        coord = self.calcCoordinates()

        self.drawPhases(qp, coord)
        self.drawArcs(qp, coord)
        self.drawObject(qp, coord)

        qp.end()

        # Calculate flashover rate
        flashRate(self)

    def drawGround(self, qp):
        grid = self.paramBox.layout()
        pen = QPen(Qt.darkGreen, 20, Qt.SolidLine)

        qp.setPen(pen)

        angle = grid.itemAtPosition(2,1).widget().text()

        try:
            slope = float(angle)

        except ValueError:
            slope = 0.0

        width = self.drawView.width()
        height = self.drawView.height()
        tan = math.tan(math.radians(slope))

        qp.drawLine(QLineF(self.width() - self.drawView.width(), self.drawView.height(),
                           self.width(), height - width*tan))

    def calcCoordinates(self):
        # Drawing scale
        vScale = self.drawView.height()/50
        hScale = self.drawView.width()/50

        # Read coorductors coordinates (set to 0m if empy field)
        coord = readCoordinates(self)

        # Calculates striking distances for the arcs
        strikeDist = strikeDistance(self)

        # Reads objects coordinates
        obj = readObj(self)

        # Calculate phase wires new coordinates in screen scale
        for k in range(len(coord[0])):
            # conductor height must be positive
            if coord[1][k] < 0:
                coord[1][k] *= -1

            coord[0][k] = int(self.width() - self.drawView.width()/2 + coord[0][k]*hScale)
            coord[1][k] = int(self.drawView.height() - coord[1][k]*vScale)

        # Adds arc origin point and height/width (coord[2] is the xOrigin, coord[3] the yOrigin)
        arcOriginX = list()
        arcOriginY = list()
        arcWidth = strikeDist[1]*hScale
        arcHeight = strikeDist[1]*vScale
        for k in range(len(coord[0])):
            arcOriginX.append(int(coord[0][k] - arcWidth/2))
            arcOriginY.append(int(coord[1][k] - arcHeight/2))

        coord.append(arcOriginX)
        coord.append(arcOriginY)

        # New objects coordinates to screen scales
        for k in range(len(obj[0])):
            # object height must be positive
            if obj[1][k] < 0:
                obj[1][k] *= -1

            obj[0][k] = int(self.width() - self.drawView.width()/2 + obj[0][k]*hScale)
            obj[1][k] = int(self.drawView.height() - obj[1][k]*vScale)

#        outOfBounds = False
#
#        # Check if and arc or phase is out of bound
#        for k in range(len(coord[0])):
#            phaseOut = coord[1][k] < 0 or coord[0][k] > self.width() or coord[0][k] < self.width()-self.drawView.width()
#            arcOut = coord[3][k]-arcHeight/2 <= 0 or coord[2][k]+arcWidth > self.width() or coord[2][k] < self.width()-self.drawView.width()
##            objOut = obj[0][k] < self.width() - self.drawView.width() or obj[0][k] > self.width() or obj[1][k] < 0
#
#            if phaseOut == True or arcOut == True:
#                outOfBounds = True
#                break
#
#        while outOfBounds == True:
#            outOfBounds = False
#
#            for k in range(len(coord[0])):
#                phaseOut = coord[1][k] <= 0 or coord[0][k] > self.width() or coord[0][k] < self.width()-self.drawView.width()
#                arcOut = coord[3][k]-arcHeight <= 0 or coord[2][k]+arcWidth > self.width() or coord[2][k] < self.width()-self.drawView.width()
##                objOut = obj[0][k] < self.width() - self.drawView.width() or obj[0][k] > self.width() or obj[1][k] < 0
#
#                # If something is out of bounds, we change the scale,
#                # redraw every elements and start again.
#                if phaseOut == True or arcOut == True:
#                    vScale = 0.75 * self.drawView.height()/50
#                    hScale = 0.75 * self.drawView.width()/50
#
#                    arcWidth = strikeDist[1]*hScale
#                    arcHeight = strikeDist[1]*vScale
#
#                    for i in range(len(coord[0])):
#                        coord[0][i] = int(self.width() - self.drawView.width()/2 + coord[0][i]*hScale)
#                        coord[1][i] = int(self.drawView.height() - coord[1][i]*vScale)
#                        coord[2][i] = int(coord[0][i]-arcWidth/2)
#                        coord[3][i] = int(coord[1][i]-arcHeight/2)
#
#                    break

        # Add arc width and height for the "drawArc" function
        coord.append(arcWidth)
        coord.append(arcHeight)

        # Strike distance to ground
        coord.append(self.drawView.height() - strikeDist[0]*vScale)

        # Objects
        coord.append(obj[0])
        coord.append(obj[1])

        return coord

    def drawPhases(self, qp, coord):
        # Phase wires, red pen
        pen = QPen(Qt.red, 5, Qt.SolidLine)
        qp.setPen(pen)

        for k in range(len(coord[0])-2):
            qp.drawPoint(coord[0][k], coord[1][k])

        # Shielding wires in green
        pen = QPen(Qt.darkGreen, 5, Qt.SolidLine)
        qp.setPen(pen)

        for k in range(len(coord[0])-2, len(coord[0])):
            qp.drawPoint(coord[0][k], coord[1][k])

    def drawArcs(self, qp, coord):
        grid = self.paramBox.layout()

        angle = grid.itemAtPosition(2,1).widget().text()

        try:
            slope = float(angle)

        except ValueError:
            slope = 0.0

        for k in range(len(coord[0])):
            if k < len(coord[0])-2:
                # Phase wires in red
                qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            else:
                # Shielding wires in green
                qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))

            qp.drawArc(coord[2][k], coord[3][k], coord[4], coord[5], 0, 180*16)

        # Ground strike distance line
        rg = coord[6]

        width = self.drawView.width()
        height = self.drawView.height()
        tan = math.tan(math.radians(slope))

        qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))
        qp.drawLine(self.width() - width, height - int(rg),
                self.width(), height - int(rg) - width*tan )

    def drawObject(self, qp, coord):
        grid = self.paramBox.layout()
        angle = grid.itemAtPosition(2,1).widget().text()

        realCoord = readObj(self)

        try:
            slope = float(angle)

        except ValueError:
            slope = 0.0

        sine = math.sin(math.radians(slope))
        cos = math.cos(math.radians(slope))

        # If the object has a height of 0 we don't need to draw it
        if realCoord[1][0] > 0:
            qp.setPen(QPen(Qt.darkGreen, 5, Qt.SolidLine))

            # Left object (starts from left side until the xCoordinate)
            poly = QPolygonF()
            width = coord[7][0] - self.paramBox.width()

            # Bottom left
            point1 = QPointF(self.width() - self.drawView.width(), self.drawView.height())
            poly.append(point1)

            # Top left
            point2 = QPointF(self.width() - self.drawView.width(), coord[8][0])
            poly.append(point2)

            # Top right
            point3 = QPointF(self.width() - self.drawView.width() + cos*width,
                             coord[8][0] - sine*width)
            poly.append(point3)

            # Bottom right
            point4 = QPointF(self.width() - self.drawView.width() + cos*width,
                             self.drawView.height() - sine*width)
            poly.append(point4)

            path = QPainterPath()
            path.addPolygon(poly)

            qp.drawPolygon(poly)
            qp.fillPath(path, QColor(Qt.darkGreen))

            # Adds striking distance to object line
            qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))
            rg = coord[6]
            line = QLineF(point3.x(), point3.y() - rg,
                          point2.x(), point2.y() - rg)

            qp.drawLine(line)

        # If the object has a height of 0 we don't need to draw it
        if realCoord[1][1] > 0:
            qp.setPen(QPen(Qt.darkGreen, 5, Qt.SolidLine))

            # Right object (starts from right side until the xCoordinate)
            poly = QPolygonF()
            width = self.width()-coord[7][1]

            width2 = coord[7][1] - self.paramBox.width()

           # Bottom left
            point1 = QPointF(self.width() - self.drawView.width() + width2*cos,
                             self.drawView.height() - sine*width2)
            poly.append(point1)

            # Top left
            point2 = QPointF(self.width() - self.drawView.width() + width2*cos,
                             coord[8][1] - sine*width2)
            poly.append(point2)

            # Top right
            point3 = QPointF(self.width() - self.drawView.width() + cos*(width2 + width),
                             coord[8][1] - sine*(width+width2))
            poly.append(point3)

            # Bottom right
            point4 = QPointF(self.width() - self.drawView.width() + cos*(width2 + width),
                             self.drawView.height() - sine*(width+width2))
            poly.append(point4)

            path = QPainterPath()
            path.addPolygon(poly)

            qp.drawPolygon(poly)
            qp.fillPath(path, QColor(Qt.darkGreen))

             # Adds striking distance to object line
            qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))
            rg = coord[6]
            line = QLineF(point3.x(), point3.y() - rg,
                          point2.x(), point2.y() - rg)

            qp.drawLine(line)