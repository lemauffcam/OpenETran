# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:31:30 2017

Draws the system

@author: Matthieu
"""
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QFileDialog
from PyQt5.QtGui import QPen, QPainter, QPolygonF, QPainterPath, QColor
from PyQt5.QtCore import pyqtSlot, Qt, QLineF, QPointF
import math, json, os.path as osp

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
def strikeDistance(self, current):
    grid = self.paramBox.layout()
    slope = grid.itemAtPosition(2,1).widget().text()

    # Read coorductors coordinates (set to 0m if empy field)
    coord = readCoordinates(self)

    # Maximum height of coorductor
    yc = max(coord[1])

    # Slope is the sine of the ground angle
    try:
        groundAngle = float(slope)
    except ValueError:
        groundAngle = 0.0

    # Rc is the strike distance to coorductor
    rc = 10.0*math.pow(current, 0.65)

    if yc < 43:
        beta = 0.37 + 0.17 * math.log(43 - yc)
    else:
        beta = 0.55

    try:
        rg = beta*rc / math.cos( math.radians(groundAngle) )
    except ZeroDivisionError:
        rg = beta*rc

    return rc, rg

# Returns the objects position and height
def readObj(self):
    grid = self.paramBox.layout()
    obj = list()
    x = list()
    y = list()

    # coord[0] will be the x coordinate, coord[1] the y coordinate
    obj.append(x)
    obj.append(y)

    for i in range(10,12):
        for j in range(1,3):
            text = grid.itemAtPosition(i,j).widget().text()

            try:
                obj[j-1].append(float(text))

            except ValueError:
                obj[j-1].append(0.0)

    return obj

# Returns the coordinates of the intersections between the 2 arcs, None if no intersection
def arcIntersection(x1, y1, x2, y2, rc):
    if y1 != y2 and x1 != x2:
        a = -(y2 - y1) / (x2 - x1)
        b = (-x1*x1 - y1*y1 + x2*x2 + y2*y2) / (2*x2 - 2*x1)

        A = a*a + 1
        B = 2*a*b - 2*a*x1 - 2*y1
        C = b*b - 2*b*x1 + x1*x1 + y1*y1 - rc*rc

        det = B*B - 4*A*C

        if det >= 0:
            # Only 1 intersection is relevant, the highest one
            # Also, it needs to be the upper half of the arc
            y_inter = (-B + math.sqrt(det))/(2*A)
            x_inter = a*y_inter + b

            if y_inter >= y1 or y_inter >= y2:
                return (x_inter, y_inter)

    elif y1 == y2 and x1 != x2:
        x_inter = (x2*x2 - x1*x1) / (2*x2 - 2*x1)

        A = 1
        B = -2*y1
        C = x_inter*x_inter - 2*x_inter*x1 + x1*x1 + y1*y1 - rc*rc

        det = B*B - 4*A*C

        if det >= 0:
            # Only 1 intersection is relevant, the highest one
            # Also, it needs to be the upper half of the arc
            y_inter = (-B + math.sqrt(det))/(2*A)

            if y_inter >= y1 or y_inter >= y2:
                return (x_inter, y_inter)

    elif y1 != y2 and x1 == x2:
        y_inter = (y2*y2 - y1*y1) / (2*y2 - 2*y1)

        if y_inter < y1 and y_inter < y2:
            return

        A = 1
        B = -2*x1
        C = y_inter*y_inter - 2*y_inter*y1 + y1*y1 + x1*x1 - rc*rc

        det = B*B - 4*A*C

        if det >= 0:
            x_inter = (-B + math.sqrt(det))/(2*A)
            return (x_inter, y_inter)

    else:
        return

def groundIntersections(x, y, rc, rg, slope, obj):
    intList = list()
    tan = math.tan(math.radians(slope))

    # Ground case
    A = 1
    B = -2*x
    C = x*x + math.pow(rg + tan*x - y, 2) - rc*rc
    det = B*B - 4*A*C

    if det >= 0 and y < rg:
        x_intG1 = (-B - math.sqrt(det)) / (2*A)
        x_intG2 = (-B + math.sqrt(det)) / (2*A)

        intList.append(x_intG1)
        intList.append(rg + tan*x_intG1)

        intList.append(x_intG2)
        intList.append(rg + tan*x_intG2)

    # 1st object
    if obj[1][0] > 0 and y < rg + obj[1][0] + tan*x:
        A = 1
        B = -2*x
        C = C = x*x + math.pow(rg + obj[1][0] + tan*x - y, 2) - rc*rc
        det = B*B - 4*A*C

        if det >= 0:
            x_intO11 = (-B - math.sqrt(det)) / (2*A)
            x_intO12 = (-B + math.sqrt(det)) / (2*A)

            # We only care about the intersection on the actual object line
            if x_intO11 <= obj[0][0] and x_intO12 <= obj[0][0]:
                intList.append(x_intO11)
                intList.append(rg + obj[1][0] + tan*x)

                intList.append(x_intO12)
                intList.append(rg + obj[1][0] + tan*x)

            elif x_intO11 > obj[0][0] and x_intO12 <= obj[0][0]:
                intList.append(x_intO12)
                intList.append(rg + obj[1][0] + tan*x)

            elif x_intO11 <= obj[0][0] and x_intO12 > obj[0][0]:
                intList.append(x_intO11)
                intList.append(rg + obj[1][0] + tan*x)

        # If an object line is above the arc it'll protect it, so we'll treat the point where
        # the arc goes under the hovering object line as an intersection like the others
        A = 1
        B = -2*y
        C = y*y + math.pow(obj[0][0] - x, 2) - rc*rc
        det = B*B - 4*A*C

        if det >= 0:
            y_int = (-B + math.sqrt(det)) / (2*A)

            if rg + obj[1][0] + tan*obj[0][0] >= y_int:
                intList.append(obj[0][0])
                intList.append(y_int)

    # 2nd object
    if obj[1][1] > 0 and y < rg + obj[1][1] + tan*x:
        A = 1
        B = -2*x
        C = C = x*x + math.pow(rg + obj[1][1] + tan*x - y, 2) - rc*rc
        det = B*B - 4*A*C

        if det >= 0:
            x_intO21 = (-B - math.sqrt(det)) / (2*A)
            x_intO22 = (-B + math.sqrt(det)) / (2*A)

            # We only care about the intersection on the actual object line
            if x_intO21 >= obj[0][1] and x_intO22 >= obj[0][1]:
                intList.append(x_intO21)
                intList.append(rg + obj[1][1] + tan*x_intO21)

                intList.append(x_intO22)
                intList.append(rg + obj[1][1] + tan*x_intO22)

            elif x_intO21 >= obj[0][1] and x_intO22 < obj[0][1]:
                intList.append(x_intO21)
                intList.append(rg + obj[1][1] + tan*x_intO21)

            elif x_intO21 < obj[0][1] and x_intO22 >= obj[0][1]:
                intList.append(x_intO22)
                intList.append(rg + obj[1][1] + tan*x_intO22)

        # If an object line is above the arc it'll protect it, so we'll treat the point where
        # the arc goes under the hovering object line as an intersection like the others
        A = 1
        B = -2*y
        C = y*y + math.pow(obj[0][1] - x, 2) - rc*rc
        det = B*B - 4*A*C

        if det >= 0:
            y_int = (-B + math.sqrt(det)) / (2*A)

            if rg + obj[1][1] + tan*obj[0][1] > y_int:
                intList.append(obj[0][1])
                intList.append(y_int)

    return intList

# Function returning a boolean saying whether the point at (x,y) is contained or not.
# x,y : current point coordinates
# coord: list of wires coordinates
# obj: list of objects coordinates
# rc,rg: striking distances
# k1,k2: indexes of the 2 arcs that intersect at the point (x,y)
def isContained(x, y, coord, obj, rc, rg, k1, k2):
    arcContained = False
    for i in range(len(coord[0])):
        if i != k1 and i != k2:
            arcContained = math.pow(x - coord[0][i], 2) + math.pow(y - coord[1][i], 2) \
                            < math.pow(rc, 2)

            if arcContained == True:
                break

    groundContained = y < rg or (obj[1][0] > 0 and y < rg + obj[1][0] and \
                      x < obj[0][0]) or \
                      (obj[1][1] > 0 and y < rg + obj[1][1] and \
                      x > obj[1][0])

    contained = arcContained or groundContained
    return contained

# Function to calculate the yearly flashover rate on the whole line
# Result is displayed in a label on the GUI
def flashRate(self):
    grid = self.paramBox.layout()
    coord = readCoordinates(self)
    obj = readObj(self)

    # Widget where the flashover rate is displayed
    label = grid.itemAtPosition(15,1).widget()
    length_str = grid.itemAtPosition(13,1).widget().text()
    flashDens_str = grid.itemAtPosition(14,1).widget().text()
    angle = grid.itemAtPosition(2,1).widget().text()
    icritList = list()

    # First we read all the critical currents
    # Get filename
    fileDialog = QFileDialog()
    name = fileDialog.getOpenFileName(None, 'Critical currents file', '/home', 'Text Files (*.txt)')

    if name == ('',''):
        return

    # 1 list for each wire currents
    for i in range(5):
        icritList.append(list())

    fileName = name[0]
    with open(fileName, 'r') as f:
        # Reads the whole critical currents file
        output = f.readlines()

        # If the word 'wire' is in a line, there's a critical current value to store
        for line in output:
            if 'wire' in line:
                end = len(line)
                pos = int(line[7]) - 1 # Wire number in the string, needed to know which
                                       # position it should take on the list.
                try:
                    current = float(line[end-14:end-1]) / 1000 # Actual critical current value [kA]
                except ValueError:
                    print('Critical current reading error')
                    continue

                icritList[pos].append(current)
            else:
                continue

    # Check length of list for considered phases (how many poles)
    length = 0
    for k in range(5):
        if len(icritList[k]) > length:
            length = len(icritList[k])
            break

    if length == 0:
        print('Err, critical currents file empty')
        return

    # If there's an empty line in the list, then the wire was not considered
    # We fill the line with -1 to indicate this phase isn't considered for the following analysis
    for k in range(5):
        if len(icritList[k]) == 0:
            for i in range(length):
                icritList[k].append(-1.0)

    try:
        slope = float(angle)

        if slope > 45:
            slope = 45.0
        elif slope < -45:
            slope = -45.0

    except ValueError:
        slope = 0.0

    try:
        length = float(length_str)
    except ValueError:
        label.setText('Err, invalid length')
        return

    try:
        flashDens = float(flashDens_str)
    except ValueError:
        label.setText('Err, invalid flash density')
        return

    flashRate_Total = list() # List of flashover rates at each pole
    numPoles = len(icritList[0]) # Number of poles in the analysis

    # Loop over all the poles for each phase
    for i in range(numPoles):
        icrit = list()
        for j in range(5):
            icrit.append(icritList[j][i])

        pLast = 1.0 # Probability that the current is higher than zero kA
        flashRate_Pole = 0.0 # Flashover rate at the current pole

        # Loop over several current values for each phases and add the contributions to the
        # local flashover rate
        for current in [x * 0.5 for x in range(5, 601)]:
            rc, rg = strikeDistance(self, current)
            expo = list() # list of exposure widths

            for k in range(len(coord[0])):
            	   # If the current is less than the wire's critical current, the stroke won't cause a flashover
                # If the current is -1, the wire is not considered for the analysis
                if current < icrit[k] or icrit[k] == -1:
                    expo.append(0)
                    continue

                intersec = list() # list of all intersections, with arcs and ground lines
                exposedInt = list()  # list of exposed intersections, by neither another arc
                                         # nor the ground
                x = coord[0][k] # Wire coordinates
                y = coord[1][k]

                # Intersections with each of the other wires in the system
                intersec.append(arcIntersection(x, y, coord[0][(k+1)%5], coord[1][(k+1)%5], rc))
                intersec.append(arcIntersection(x, y, coord[0][(k+2)%5], coord[1][(k+2)%5], rc))
                intersec.append(arcIntersection(x, y, coord[0][(k+3)%5], coord[1][(k+3)%5], rc))
                intersec.append(arcIntersection(x, y, coord[0][(k+4)%5], coord[1][(k+4)%5], rc))

                # Intersections with the ground and object lines
                intersec.append(groundIntersections(x, y, rc, rg, slope, obj))

                # Isolate the exposed arc intersections
                for i in range(0, 4):
                    if intersec[i] is not None:
                        x_i = intersec[i][0]
                        y_i = intersec[i][1]

                        if isContained(x_i, y_i, coord, obj, rc, rg, k, (k + i + 1)%5) == False:
                            exposedInt.append( (x_i, y_i) )

                # Same with ground intersections
                if len(intersec[4]) > 0:
                    for i in range(0, len(intersec[4]), 2):
                        x_i = intersec[4][i]
                        y_i = intersec[4][i+1] # Number of elements always even so no problem

                        if isContained(x_i, y_i, coord, obj, rc, rg, k, 5) == False:
                            exposedInt.append( (x_i, y_i) )

                if len(exposedInt) > 1:
                    width = 0
                    # If the arc portion between 2 intersections is exposed (i.e the point in the
                    # middle is exposed), we add the horizontal distance to the exposition width
                    for i in range(len(exposedInt)):
                        for j in range(len(exposedInt)):
                            if i == j:
                                continue

                            x0 = coord[0][k] # Phase coordinates
                            y0 = coord[1][k]
                            x1 = exposedInt[i][0] # 1st intersection coordinates
                            x2 = exposedInt[j][0] # 2nd intersection coordinates

                            x = (x1 + x2) / 2 # (x,y) the coordinates of the point "in the middle"

                            A = 1
                            B = -2*y0
                            C = y0*y0 + math.pow(x - x0, 2) - rc*rc
                            det = B*B - 4*A*C

                            y = (-B + math.sqrt(det)) / (2*A)

                            if isContained(x, y, coord, obj, rc, rg, k, 5) == False:
                                # With the current algorithm that distance is calculated twice. Hence the
                                # /2. Since there are usually no more than 2 or 3 exposed intersections
                                # there's no need for a faster method
                                width += math.fabs(x1 - x2) / 2

                    expo.append(width)

                # If there aren't any exposed intersections, either the arc is completely below
                # a ground/object line, in this case its exposure width is 0 since it's fully
                # protected, or it's above and clear of all other arcs. In this case the exposure
                # width is the arc's diameter
                else:
                   if coord[1][k] < rg + obj[1][0] or coord[1][k] < rg + obj[1][1]:
                       expo.append(0)
                   else:
                       expo.append(2*rc)

            pFlash = 1/(1 + math.pow(current/31, 2.6))  # Probability that the 1st stroke current is higher than this current
            pBin = pLast - pFlash # probability that the current is inside this histogram bin

            pLast = pFlash

            # Calculate the flashover rate using the exposure width
            for k in range(len(expo)):
                flashRate_Pole += expo[k]/1000*length/numPoles*flashDens*pBin

            del[expo]

        flashRate_Total.append(flashRate_Pole)

    # We display the average flashover rate for the whole line
    flashRate_Average = sum(flashRate_Total) / max(len(flashRate_Total), 1)
    label.setText(str(flashRate_Average))

    print('Flashover rate calculation complete')

    return

class SysView(QWidget):
    def __init__(self, openetran_window):
        super().__init__()

        self.openEtran = openetran_window

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
        paramLayout.addWidget(QPushButton('Update coordinates'), 0, 2)
        paramLayout.addWidget(QPushButton('Save'), 0, 3)
        paramLayout.addWidget(QPushButton('Load'), 0, 4)

        paramLayout.addWidget(QLabel('Current [kA]'), 1, 0)
        paramLayout.addWidget(QLineEdit('15'), 1, 1)

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
        paramLayout.addWidget(QLineEdit('20'), 13, 1)

        paramLayout.addWidget(QLabel('Flash density (strike/km2/y)'), 14, 0)
        paramLayout.addWidget(QLineEdit('5'), 14, 1)

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

        @pyqtSlot()
        def updateCoordinates():
            wireCoord = self.openEtran.readWireCoordinates()

            # Wire coordinates in text fields
            # Check conductor number, if 1 then it's A, 2 is B etc.
            for coord in wireCoord['conductor']:
                try:
                    num = int(coord[0])
                except ValueError:
                    print('Bad number on conductor')
                    continue

                y = coord[1]
                x = coord[2]

                if num < 1 or num > 5:
                    print('Bad number on conductor')
                    continue

                xField = paramLayout.itemAtPosition(num+3, 1).widget()
                xField.setText(x)

                yField = paramLayout.itemAtPosition(num+3, 2).widget()
                yField.setText(y)

        coordinates = paramLayout.itemAtPosition(0,2).widget()
        coordinates.pressed.connect(updateCoordinates)

        @pyqtSlot()
        def save():
            struct = dict() # main dictionnary
            struct['slope'] = paramLayout.itemAtPosition(2,1).widget().text()
            struct['length'] = paramLayout.itemAtPosition(13,1).widget().text()
            struct['density'] = paramLayout.itemAtPosition(14,1).widget().text()

            struct['obj_coordinates'] = list()
            struct['obj_coordinates'].append(list()) # Obj 1 coordinates
            struct['obj_coordinates'].append(list()) # Obj 2 coordinates

            obj1X = paramLayout.itemAtPosition(10,1).widget().text()
            obj1Y = paramLayout.itemAtPosition(10,2).widget().text()

            obj2X = paramLayout.itemAtPosition(11,1).widget().text()
            obj2Y = paramLayout.itemAtPosition(11,2).widget().text()

            struct['obj_coordinates'][0].append(obj1X)
            struct['obj_coordinates'][0].append(obj1Y)

            struct['obj_coordinates'][1].append(obj2X)
            struct['obj_coordinates'][1].append(obj2Y)

            fileDialog = QFileDialog()

            if self.openEtran.lastDirectory == '':
                filename = fileDialog.getSaveFileName(None, 'Save File', '/home', 'JSON Files (*.json)')
            else:
                filename = fileDialog.getSaveFileName(None, 'Save File', self.openEtran.lastDirectory, 'JSON Files (*.json)')

            if filename == ("",""):
                print('Save cancelled')
                return
            else:
                with open(filename[0], 'w') as f:
                    json.dump(struct, f, indent=2)

            self.openEtran.lastDirectory = osp.dirname(filename[0])
            print('Save done')

        saveButton = paramLayout.itemAtPosition(0,3).widget()
        saveButton.pressed.connect(save)

        @pyqtSlot()
        def load():
            fileDialog = QFileDialog()

            if self.openEtran.lastDirectory == '':
                filename = fileDialog.getOpenFileName(None, 'Save File', '/home', 'JSON Files (*.json)')
            else:
                filename = fileDialog.getOpenFileName(None, 'Save File', self.openEtran.lastDirectory, 'JSON Files (*.json)')

            if filename == ("",""):
                print('Load cancelled')
                return

            else:
                with open(filename[0], 'r') as f:
                    struct = json.load(f)

            paramLayout.itemAtPosition(2,1).widget().setText(struct['slope'])
            paramLayout.itemAtPosition(13,1).widget().setText(struct['length'])
            paramLayout.itemAtPosition(14,1).widget().setText(struct['density'])
            paramLayout.itemAtPosition(10,1).widget().setText(struct['obj_coordinates'][0][0])
            paramLayout.itemAtPosition(10,2).widget().setText(struct['obj_coordinates'][0][1])
            paramLayout.itemAtPosition(11,1).widget().setText(struct['obj_coordinates'][1][0])
            paramLayout.itemAtPosition(11,2).widget().setText(struct['obj_coordinates'][1][1])

            self.openEtran.lastDirectory = osp.dirname(filename[0])
            print('Load done')

        loadButton = paramLayout.itemAtPosition(0,4).widget()
        loadButton.pressed.connect(load)

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

        grid = self.paramBox.layout()
        current_str = grid.itemAtPosition(1,1).widget().text()

        try:
            current = math.fabs(float(current_str))
        except ValueError:
            current = 0.0

        # Calculates striking distances for the arcs
        rc, rg = strikeDistance(self, current)

        # Reads objects coordinates
        obj = readObj(self)

        # Checks if everything is in bounds, if not we change the scales
        outBounds = True

        while outBounds == True:
            # Check if a conductor is out of bounds
            for k in range(len(coord[0])):
                condX = self.width() - self.drawView.width()/2 + coord[0][k]*hScale
                condY = self.drawView.height() - coord[1][k]*vScale

                outBounds = condX < self.width() - self.drawView.width() or condX > self.width() \
                            or condY < 0 or condY > self.height()

                if outBounds == True:
                    break

            # Check if an arc is out of bounds
            for k in range(len(coord[0])):
                if outBounds == True:
                    break

                arcWidth = 2*rc*hScale
                arcHeight = 2*rc*vScale

                condX = self.width() - self.drawView.width()/2 + coord[0][k]*hScale
                condY = self.drawView.height() - coord[1][k]*vScale

                arcOriginX = condX - arcWidth/2
                arcOriginY = condY - arcHeight/2

                outBounds = arcOriginX < self.width() - self.drawView.width() \
                        or arcOriginX > self.width() or arcOriginX + arcWidth > self.width() \
                        or arcOriginY > self.height() or arcOriginY + arcHeight < 0 \
                        or arcOriginY < 0

            # Check if an object is out of bounds
            for k in range(len(obj[0])):
                if outBounds == True:
                    break

                objX = self.width() - self.drawView.width()/2 + obj[0][k]*hScale
                objY = self.drawView.height() - obj[1][k]*vScale

                outBounds = objX > self.width() or objX < self.width() - self.drawView.width() \
                        or objY > self.height() or objY < 0

            # If any element is out of bounds, we change the scales
            if outBounds == True:
                hScale = 9 * hScale / 10
                vScale = 9 * vScale / 10


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
        arcWidth = list()
        arcHeight = list()

        for k in range(len(coord[0])):
            width = 2*rc*hScale
            height = 2*rc*vScale

            arcOriginX.append(int(coord[0][k] - width/2))
            arcOriginY.append(int(coord[1][k] - height/2))
            arcWidth.append(width)
            arcHeight.append(height)

        coord.append(arcOriginX)
        coord.append(arcOriginY)

        # Add arc width and height for the "drawArc" function
        coord.append(arcWidth)
        coord.append(arcHeight)

        # New objects coordinates to screen scales
        for k in range(len(obj[0])):
            # object height must be positive
            if obj[1][k] < 0:
                obj[1][k] *= -1

            obj[0][k] = int(self.width() - self.drawView.width()/2 + obj[0][k]*hScale)
            obj[1][k] = int(self.drawView.height() - obj[1][k]*vScale)

        # Strike distance to ground
        coord.append(rg*vScale)

        # Objects
        coord.append(obj[0])
        coord.append(obj[1])

        return coord

    def drawGround(self, qp, coord):
        grid = self.paramBox.layout()
        pen = QPen(Qt.darkGreen, 10, Qt.SolidLine)

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

            qp.drawArc(coord[2][k], coord[3][k], coord[4][k], coord[5][k], 0, 180*16)

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