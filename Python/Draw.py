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
    current = grid.itemAtPosition(1,1).widget().text()

    # Slope is the sine of the ground angle
    try:
        groundAngle = float(slope)
    except ValueError:
        groundAngle = 0.0

    try:
        icrit = float(current)
    except ValueError:
        icrit = 0.0

    # Read coorductors coordinates (set to 0m if empy field)
    coord = readCoordinates(self)

    # Maximum height of coorductor
    yc = max(coord[1])

    # Rc is the strike distance to coorductor
    rc = 10.0*math.pow(icrit, 0.65)

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

# Only returns the absciss, the exposure width being a horizontal distance
def arcIntersection(x1, y1, x2, y2, rc):
    if y1 != y2:
        # y_intersection = ax_intersection + b
        a = (x1 - x2) / (y2 - y1)
        b = (y2*y2 - y1*y1 + x2*x2 - x1*x1) / (2 * (y2 - y1))

        # x is the solution of a 2nd degree equation
        A = 1 + a*a
        B = 2*a*b - 2*x1 - 2*a*y1
        C = x1*x1 + b*b - 2*b*y1 + y1*y1 - rc*rc
        det = B*B - 4*A*C

        if det > 0:
            x_inter1 = (-B + math.sqrt(det))/(2*A)
            y_inter1 = a*x_inter1 + b

            x_inter2 = (-B - math.sqrt(det))/(2*A)
            y_inter2 = a*x_inter2 + b

            # Only 1 intersection is relevant, the highest one
            # Also, it needs to be the upper half of the arc
            if y_inter2 <= y_inter1 and (y_inter2 >= y1 or y_inter2 >= y2):
               return x_inter1

            elif y_inter1 >= y_inter2 and (y_inter1 >= y1 or y_inter2 >= y2):
                return x_inter2

    else:
        x_inter = (x2 + x1) / 2
        A = 1
        B = -2*y1
        C = math.pow(x_inter - x1, 2) + y1*y1 - rc*rc
        det = B*B - 4*A*C

        if det > 0:
            y_inter1 = (-B + math.sqrt(det)) / 2
            y_inter2 = (-B - math.sqrt(det)) / 2

            if y_inter1 >= y1 or y_inter2 >= y1:
                return x_inter

def flashRate(self):
    grid = self.paramBox.layout()
    coord = readCoordinates(self)
    strikeDist = strikeDistance(self)
    obj = readObj(self)

    # Widget where the flashover rate is displayed
    label = grid.itemAtPosition(15,1).widget()

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

    expo = list() # list of exposure widths
    intersecGround = list() # Coordinates of intersections between arcs and ground strike line

    # Shielding wires coordinates
    x1 = coord[0][3]
    y1 = coord[1][3]
    x2 = coord[0][4]
    y2 = coord[1][4]
    rc = strikeDist[1] # Striking distance to conductor
    rg = strikeDist[0] # Striking distance to ground

    shield_intCoord = arcIntersection(x1, y1, x2, y2, rc)

    if shield_intCoord is None:
        label.setText('Err')
        return

    # Exposure width of the shielding wire is the horizontal distance between the arcs
    # intersection and the intersection of each arc with the line representing the striking
    # distance to ground (or object)

    # Intersections with the ground, or an object, strike line
    for k in range(len(coord[0])):
        x = coord[0][k] # wire coordinates
        y = coord[1][k]
        list1 = list()

        # Ground case
        A = 1
        B = -2*x
        C = x*x + math.pow(rg - y, 2) - rc*rc
        det = B*B - 4*A*C

        if det > 0:
            x_intG1 = (-B - math.sqrt(det)) / (2*A)
            x_intG2 = (-B + math.sqrt(det)) / (2*A)

            list1.append(x_intG1)
            list1.append(x_intG2)

        # Object case
        if obj[1][0] > 0:
            A = 1
            B = -2*x
            C = C = x*x + math.pow(rg + obj[1][0] - y, 2) - rc*rc
            det = B*B - 4*A*C

            if det > 0:
                x_intO11 = (-B - math.sqrt(det)) / (2*A)
                x_intO12 = (-B + math.sqrt(det)) / (2*A)

                # We only care about the intersection on the actual object line
                if x_intO11 <= obj[0][0] and x_intO12 <= obj[0][0]:
                    list1.append(x_intO11)
                    list1.append(x_intO12)

                elif x_intO11 > obj[0][0] and x_intO12 <= obj[0][0]:
                    list.append(x_intO12)

                elif x_intO11 <= obj[0][0] and x_intO12 > obj[0][0]:
                    list.append(x_intO11)

        # 2nd object
        if obj[1][1] > 0:
            A = 1
            B = -2*x
            C = C = x*x + math.pow(rg + obj[1][1] - y, 2) - rc*rc
            det = B*B - 4*A*C

            if det > 0:
                x_intO21 = (-B - math.sqrt(det)) / (2*A)
                x_intO22 = (-B + math.sqrt(det)) / (2*A)

                # We only care about the intersection on the actual object line
                if x_intO21 >= obj[0][1] and x_intO22 >= obj[0][1]:
                    list1.append(x_intO21)
                    list1.append(x_intO22)

                elif x_intO21 < obj[0][1] and x_intO22 >= obj[0][1]:
                    list.append(x_intO21)

                elif x_intO21 >= obj[0][1] and x_intO22 < obj[0][1]:
                    list.append(x_intO22)

        intersecGround.append(list1)

    # Phase wire exposure width
    for k in range(0,3):
        # Check if each phase arc is contained by the shielding arcs
        x1_In = ( intersecGround[k][0] >= intersecGround[3][0]  \
                and intersecGround[k][0] <= intersecGround[3][1] ) \
                or ( intersecGround[k][0] >= intersecGround[4][0]  \
                and intersecGround[k][0] <= intersecGround[4][1] )

        x2_In = ( intersecGround[k][1] >= intersecGround[3][0]  \
                and intersecGround[k][1] <= intersecGround[3][1] ) \
                or ( intersecGround[k][1] >= intersecGround[4][0]  \
                and intersecGround[k][1] <= intersecGround[4][1] )

        # If the arcs are contained within the shielding wires arcs, then the width is 0
        if x2_In == True and x1_In == True:
            expo.append(0)

        # If not it's the horizontal distance between intersection with ground/object line and
        # and a shielding arc
        else:
            x1 = coord[0][k] # Phase wire coordinates
            y1 = coord[0][k]

            # check if there's an intersection with the 1st shielding wire
            x2 = coord[0][3] # Shielding wire coordinates
            y2 = coord[1][3]

            inter1 = arcIntersection(x1, y1, x2, y2, rc)

            # 2nd shielding wire
            x2 = coord[0][4]
            y2 = coord[1][4]

            inter2 = arcIntersection(x1, y1, x2, y2, rc)

            # The phase wire is completely exposed
            if inter1 is None and inter2 is None:
                expo.append(2*rc)

            # The phase wire intersects with 1 of the shielding wires
            elif inter1 is None and inter2 is not None:
                if obj[1][0] > 0:
                    expo.append(1)

    # Shield wire exposure width: if all phase wires are contained then it's the
    # horizontal distance between arc intersections and intersection with ground strike line
    if all(v == 0 for v in expo) == True:
        if intersecGround[3][0] <= intersecGround[4][0]:
            expo.append( math.fabs(shield_intCoord - intersecGround[3][0]) )
            expo.append( math.fabs(shield_intCoord - intersecGround[4][1]) )

        else:
            expo.append( math.fabs(shield_intCoord - intersecGround[3][1]) )
            expo.append( math.fabs(shield_intCoord - intersecGround[4][0]) )


    # Probability that the 1st stroke current is higher than the critical current
    pFlash = 1/(1 + math.pow(icrit/31, 2.6))

    # Phase wire, we don't use the probability because it's not a backflashover
    for k in range(len(expo) - 2):
        expo[k] = expo[k]/1000*length*flashDens

    # Shielding wire, we use the probability
    for k in range(len(expo) - 3, len(expo)):
        expo[k] = expo[k]/1000*length*flashDens*pFlash

    flashRate = math.fsum(expo)

    label.setText(str(flashRate))

    return

class SysView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Phase view')
        self.setGeometry(100, 100, 1200, 500)

        # Phase view
        mainLayout = QGridLayout()
        paramLayout = QGridLayout()

        self.paramBox = QWidget()

        paramLayout.addWidget(QPushButton('Update view'), 0, 0)
        paramLayout.addWidget(QPushButton('Flashover Rate'), 0, 1)

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

        @pyqtSlot()
        def calcFlashRate():
            flashRate(self)

        rate = paramLayout.itemAtPosition(0,1).widget()
        rate.pressed.connect(calcFlashRate)

    def paintEvent(self, e):
        qp = QPainter()

        # Calculates all coordinates and changes the scales accordingly
        coord = self.calcCoordinates()

        qp.begin(self)

        self.drawGround(qp, coord)
        self.drawPhases(qp, coord)
        self.drawArcs(qp, coord)
        self.drawObject(qp, coord)

        qp.end()

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

        # Checks if everything is in bounds, if not we change the scales
        outBounds = True

        while outBounds == True:
            # Check if a conductor is out of bounds
            for k in range(len(coord[0])):
                condX = self.width() - self.drawView.width()/2 + coord[0][k]*hScale
                condY = self.drawView.height() - coord[1][k]*vScale

                condOut = condX < self.width() - self.drawView.width() or condX > self.width() \
                            or condY < 0 or condY > self.height()

                if condOut == True:
                    break

            # Check if an arc is out of bounds
            for k in range(len(coord[0])):
                if condOut == True:
                    arcOut = True
                    break

                arcWidth = 2*strikeDist[1]*hScale
                arcHeight = 2*strikeDist[1]*vScale

                condX = self.width() - self.drawView.width()/2 + coord[0][k]*hScale
                condY = self.drawView.height() - coord[1][k]*vScale

                arcOriginX = condX - arcWidth/2
                arcOriginY = condY - arcHeight/2

                arcOut = arcOriginX < self.width() - self.drawView.width() \
                        or arcOriginX > self.width() or arcOriginX + arcWidth > self.width() \
                        or arcOriginY > self.height() or arcOriginY < 0 \
                        or arcOriginY < 0

                if arcOut == True:
                    break

            # Check if an object is out of bounds
            for k in range(len(obj[0])):
                if condOut == True or arcOut == True:
                    objOut = True
                    break

                objX = self.width() - self.drawView.width()/2 + obj[0][k]*hScale
                objY = self.drawView.height() - obj[1][k]*vScale

                objOut = objX > self.width() or objX < self.width() - self.drawView.width() \
                        or objY > self.height() or objY < 0

                if objOut == True:
                    break

            # If any element is out of bounds, we change the scales
            if condOut == True or arcOut == True or objOut == True:
                hScale = 9 * hScale / 10
                vScale = 9 * vScale / 10
            else:
                outBounds = False


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
        arcWidth = 2*strikeDist[1]*hScale
        arcHeight = 2*strikeDist[1]*vScale
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

        # Add arc width and height for the "drawArc" function
        coord.append(arcWidth)
        coord.append(arcHeight)

        # Strike distance to ground
        coord.append(strikeDist[0]*vScale)

        # Objects
        coord.append(obj[0])
        coord.append(obj[1])

        return coord

    def drawGround(self, qp, coord):
        grid = self.paramBox.layout()
        pen = QPen(Qt.darkGreen, 20, Qt.SolidLine)

        qp.setPen(pen)

        angle = grid.itemAtPosition(2,1).widget().text()

        try:
            slope = float(angle)

            if slope > 45:
                slope = 45.0
            elif slope < -45:
                slope = -45.0

        except ValueError:
            slope = 0.0

        width = self.drawView.width()
        height = self.drawView.height()
        tan = math.tan(math.radians(slope))

        qp.drawLine(QLineF(self.width() - width, height + width*tan/2,
                           self.width(), height - width*tan/2))

        # Striking distance to ground
        rg = coord[6]

        qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))

        height = self.drawView.height() - rg
        qp.drawLine(QLineF(self.width() - width, height + width*tan/2,
                           self.width(), height - width*tan/2))

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
        for k in range(len(coord[0])):
            if k < len(coord[0])-2:
                # Phase wires in red
                qp.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            else:
                # Shielding wires in green
                qp.setPen(QPen(Qt.darkGreen, 2, Qt.SolidLine))

            qp.drawArc(coord[2][k], coord[3][k], coord[4], coord[5], 0, 180*16)

    def drawObject(self, qp, coord):
        grid = self.paramBox.layout()
        angle = grid.itemAtPosition(2,1).widget().text()

        realCoord = readObj(self)

        try:
            slope = float(angle)

            if slope > 45:
                slope = 45.0
            elif slope < -45:
                slope = -45.0

        except ValueError:
            slope = 0.0

        tan = math.tan(math.radians(slope))

        # If the object has a height of 0 we don't need to draw it
        if realCoord[1][0] > 0:
            qp.setPen(QPen(Qt.darkGreen, 5, Qt.SolidLine))

            # Left object (starts from left side until the xCoordinate)
            poly = QPolygonF()

            # Bottom left
            point1 = QPointF(self.width() - self.drawView.width(),
                             self.drawView.height() + self.drawView.width()*tan/2)
            poly.append(point1)

            # Top left
            point2 = QPointF(self.width() - self.drawView.width(),
                             coord[8][0] + self.drawView.width()*tan/2)
            poly.append(point2)

            # Top right
            point3 = QPointF(coord[7][0], coord[8][0] + tan*(self.width() -
                             self.drawView.width()/2 - coord[7][0]))
            poly.append(point3)

            # Bottom right
            point4 = QPointF(coord[7][0],
                             self.drawView.height() + tan*(self.width() -
                             self.drawView.width()/2 - coord[7][0]))
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

           # Bottom left
            point1 = QPointF(coord[7][1], self.drawView.height() + tan*(self.width() -
                             self.drawView.width()/2 - coord[7][1]))
            poly.append(point1)

            # Top left
            point2 = QPointF(coord[7][1], coord[8][1] + tan*(self.width() -
                            self.drawView.width()/2 - coord[7][1]))
            poly.append(point2)

            # Top right
            point3 = QPointF(self.width(),
                             coord[8][1] - self.drawView.width()*tan/2)
            poly.append(point3)

            # Bottom right
            point4 = QPointF(self.width(),
                             self.drawView.height() - self.drawView.width()*tan/2)
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