# -*- coding: utf-8 -*-
"""
Created on Thu Dec 1 2016

Reads openetran structure from the GUI

@author: Matthieu Bertin
"""

# General function to read widget on the grid layout
# Particular case if the number of text fields to read is not even
def readWidgets(openetran, grid, name, rowOffset, numCol, notEven):
    countTotal = grid.count()
    count = 0 # current count of the elements

    rowStart = 2
    rowEnd = rowStart + rowOffset

    while count < countTotal:
        # Positions of all text fields in each element of the tab
        positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(1, numCol, 2)]
        listParam = list()

        # If the number of text fields is not even, the widget at the bottom right of the read
        # element will be a label, so it's ignored.
        if notEven == 1:
            for position in positions:
                count = (position[0] + 1) * (position[1] + 1)

                # Bottom right widget is a label, so we ignore it
                if position[0] == (rowEnd - 1) and position[1] == (numCol-1):
                    continue

                else:
                    # Get the text and append it in the list
                    widget = grid.itemAtPosition(position[0], position[1]).widget()
                    listParam.append(widget.text())
        else:
            for position in positions:
                count = (position[0] + 1) * (position[1] + 1)

                widget = grid.itemAtPosition(position[0], position[1]).widget()
                listParam.append(widget.text())

        # Append the list of values (which makes for one whole component) in the key list
        openetran[name].append(listParam)
        rowStart = rowEnd + 1
        rowEnd = rowStart + rowOffset

def read(self, guiNormal):
    openetran = dict()

    openetran['simulation'] = list()
    openetran['conductor'] = list()
    openetran['ground'] = list()
    openetran['surge'] = list()
    openetran['arrbez'] = list()
    openetran['lpm'] = list()
    openetran['meter'] = list()
    openetran['label'] = list()
    openetran['resistor'] = list()

    # Only read steepfront, arrester etc. when we're in extended view
    if guiNormal.isChecked() == True:
        openetran['steepfront'] = list()
        openetran['arrester'] = list()
        openetran['insulator'] = list()
        openetran['inductor'] = list()
        openetran['capacitor'] = list()
        openetran['customer'] = list()
        openetran['pipegap'] = list()

    # Simulation parameters
    readSimulation(self, openetran)

    # Conductor parameters
    readConductor(self, openetran)

    # Ground parameters
    readGround(self, openetran)

    # Surge and Steepfront
    readSurge(self,openetran)

    # Arrbez
    readArrbez(self, openetran)

    # LPM
    readLPM(self, openetran)

    # Meter
    readMeter(self, openetran)

    # Labels
    readLabel(self, openetran)

    # Resistor
    readResistor(self, openetran)

    if guiNormal.isChecked() == True:
        # Steepfront
        readSteepfront(self, openetran)

        # Insulator
        readInsulator(self, openetran)

        # Arrester
        readArrester(self, openetran)

        # Capacitor
        readCapacitor(self, openetran)

        # Inductor
        readInductor(self, openetran)

        # Customer
        readCustomer(self, openetran)

        # Pipegap
        readPipegap(self, openetran)

    return openetran

def readSimulation(self, openetran):
    layout = self.Simulation.layout()
    critMode = layout.itemAtPosition(2,3).widget()

    if critMode.isChecked() == True:
        max = 10
    else:
        max = 7

    for k in range(max):
        widget = layout.itemAtPosition(k, 1).widget()
        openetran['simulation'].append(widget.text())

def readConductor(self, openetran):
    grid = self.Conductor.layout()
    readWidgets(openetran, grid, 'conductor', 4, 4, 0)

def readGround(self, openetran):
    grid = self.Ground.layout()
    readWidgets(openetran, grid, 'ground', 4, 6, 0)

def readSurge(self, openetran):
    grid = self.Surge.layout()

    for k in range(6):
        widget = grid.itemAtPosition(k, 1).widget()
        openetran['surge'].append(widget.text())

def readSteepfront(self, openetran):
    grid = self.Steepfront.layout()

    for k in range(7):
        widget = grid.itemAtPosition(k, 1).widget()
        openetran['steepfront'].append(widget.text())

# Particular case in Arrester (see while loop)
def readArrester(self, openetran):
    grid = self.Arrester.layout()
    readWidgets(openetran, grid, 'arrester', 4, 4, 1)

def readArrbez(self, openetran):
    grid = self.Arrbez.layout()
    readWidgets(openetran, grid, 'arrbez', 4, 4, 0)

def readInsulator(self, openetran):
    grid = self.Insulator.layout()
    readWidgets(openetran, grid, 'insulator', 3, 4, 0)

# Particular case in LPM
def readLPM(self, openetran):
    grid = self.LPM.layout()
    readWidgets(openetran, grid, 'lpm', 3, 4, 1)

def readMeter(self, openetran):
    grid = self.Meter.layout()

    countTotal = grid.count()
    count = 0 # current count of the elements

    rowStart = 2
    rowEnd = rowStart + 2

    while count < countTotal:
        positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(1, 4, 2)]
        listParam = list()

        for position in positions:
            count = (position[0] + 1) * (position[1] + 1)

            if position[0] == (rowEnd - 1) and position[1] == 3:
                continue

            # Slightly different function if it's a combo box to read the text
            elif position[0] == rowStart and position[1] == 1:
                widget = grid.itemAtPosition(position[0], position[1]).widget()
                text = widget.currentText()

                if 'Voltage' in text:
                    listParam.append('0')

                elif 'Arrester' in text:
                    listParam.append('1')

                elif 'Ground' in text:
                    listParam.append('2')

                elif 'Customer' in text:
                    listParam.append('3')

                elif 'Transformer' in text:
                    listParam.append('4')

                else:
                    listParam.append('5')

            else:
                widget = grid.itemAtPosition(position[0], position[1]).widget()
                listParam.append(widget.text())

        openetran['meter'].append(listParam)
        rowStart = rowEnd + 1
        rowEnd = rowStart + 2

def readLabel(self, openetran):
    grid = self.Label.layout()

    countTotal = grid.count()
    count = 0 # current count of the elements

    rowStart = 2
    rowEnd = rowStart + 2

    while count < countTotal:
        positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(1, 4, 2)]
        listParam = list()

        for position in positions:
            count = (position[0] + 1) * (position[1] + 1)

            if position[0] == (rowEnd - 1) and position[1] == 3:
                continue

            # Slightly different function if it's a combo box to read the text
            elif position[0] == rowStart and position[1] == 1:
                widget = grid.itemAtPosition(position[0], position[1]).widget()
                listParam.append(widget.currentText())

            else:
                widget = grid.itemAtPosition(position[0], position[1]).widget()
                listParam.append(widget.text())

        openetran['label'].append(listParam)
        rowStart = rowEnd + 1
        rowEnd = rowStart + 2

def readResistor(self, openetran):
    grid = self.Resistor.layout()
    readWidgets(openetran, grid, 'resistor', 2, 4, 1)

def readCapacitor(self, openetran):
    grid = self.Capacitor.layout()
    readWidgets(openetran, grid, 'capacitor', 2, 4, 1)

def readInductor(self, openetran):
    grid = self.Inductor.layout()
    readWidgets(openetran, grid, 'inductor', 2, 4, 0)

def readCustomer(self, openetran):
    grid = self.Customer.layout()
    readWidgets(openetran, grid, 'customer', 6, 6, 1)

def readPipegap(self, openetran):
    grid = self.Pipegap.layout()
    readWidgets(openetran, grid, 'pipegap', 2, 4, 0)