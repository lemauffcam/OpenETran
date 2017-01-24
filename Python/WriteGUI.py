# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 17:07:23 2017

Script to write in every GUI text fields when loading a project
Very similar to the ReadStruct.py script, with a few added functionnalities, such
as adding widgets dynamically if there are more than 1 element per tab.

@author: Matthieu
"""

import Add_Delete_Widgets

# General function to write values in the text fields on the grid layout
# Particular case if the number of text fields to read is not even
def writeWidgets(openetran, grid, name, rowOffset, numCol, notEven):
    countTotal = grid.count()
    count = 0 # current count of the elements in the layout
    i = 0 # index of the current list (each key containing a list of lists)

    rowStart = 2
    rowEnd = rowStart + rowOffset

    while count < countTotal:
        # List of positions of each text fields in the layout
        positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(1, numCol, 2)]
        k = 0

        if notEven == 1:
            for position in positions:
                count = (position[0] + 1) * (position[1] + 1)

                if position[0] == (rowEnd - 1) and position[1] == (numCol-1):
                    continue

                else:
                    v = openetran[name][i][k]
                    widget = grid.itemAtPosition(position[0], position[1]).widget()
                    widget.setText(v)

                    k += 1
        else:
            for position in positions:
                v = openetran[name][i][k]

                count = (position[0] + 1) * (position[1] + 1)

                widget = grid.itemAtPosition(position[0], position[1]).widget()
                widget.setText(v)

                k += 1

        rowStart = rowEnd + 1
        rowEnd = rowStart + rowOffset
        i += 1
        k = 0

def write(self, openetran, dispNormal):
    # Simulation parameters
    writeSimulation(self, openetran)

    # Conductor parameters
    writeConductor(self, openetran)

    # Ground parameters
    writeGround(self, openetran)

    # Surge and Steepfront
    writeSurge(self,openetran)

    # Arrbez
    writeArrbez(self, openetran)

    # LPM
    writeLPM(self, openetran)

    # Meter
    writeMeter(self, openetran)

    # Labels
    writeLabel(self, openetran)

    if dispNormal == True:
        # Steepfront
        writeSteepfront(self, openetran)

        # Insulator
        writeInsulator(self, openetran)

        # Arrester
        writeArrester(self, openetran)

        # Resistor
        writeResistor(self, openetran)

        # Capacitor
        writeCapacitor(self, openetran)

        # Inductor
        writeInductor(self, openetran)

        # Customer
        writeCustomer(self, openetran)

        # Pipegap
        writePipegap(self, openetran)

def writeSimulation(self, openetran):
    layout = self.Simulation.layout()

    for k in range(7):
        widget = layout.itemAtPosition(k, 1).widget()
        widget.setText(openetran['simulation'][k])

def writeConductor(self, openetran):
    grid = self.Conductor.layout()

    # Number of conductors in the system
    num = len(openetran['conductor'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addConductor(self, grid)

    writeWidgets(openetran, grid, 'conductor', 3, 4, 1)

def writeGround(self, openetran):
    grid = self.Ground.layout()

    # Number of grounds in the system
    num = len(openetran['ground'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addGround(self, grid)

    writeWidgets(openetran, grid, 'ground', 4, 6, 0)

def writeSurge(self, openetran):
    grid = self.Surge.layout()

    for k in range(6):
        widget = grid.itemAtPosition(k, 1).widget()
        widget.setText(openetran['surge'][k])

def writeSteepfront(self, openetran):
    grid = self.Steepfront.layout()

    for k in range(7):
        widget = grid.itemAtPosition(k, 1).widget()
        widget.setText(openetran['steepfront'][k])

# Particular case in Arrester (see while loop)
def writeArrester(self, openetran):
    grid = self.Arrester.layout()

    # Number of arresters in the system
    num = len(openetran['arrester'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addArrester(self, grid)

    writeWidgets(openetran, grid, 'arrester', 4, 4, 1)

def writeArrbez(self, openetran):
    grid = self.Arrbez.layout()

    # Number of arrbez in the system
    num = len(openetran['arrbez'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addArrbez(self, grid)

    writeWidgets(openetran, grid, 'arrbez', 4, 4, 0)

def writeInsulator(self, openetran):
    grid = self.Insulator.layout()

    # Number of insulators in the system
    num = len(openetran['insulator'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addInsulator(self, grid)

    writeWidgets(openetran, grid, 'insulator', 3, 4, 0)

# Particular case in LPM
def writeLPM(self, openetran):
    grid = self.LPM.layout()

    # Number of LPMs in the system
    num = len(openetran['lpm'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addLPM(self, grid)

    writeWidgets(openetran, grid, 'lpm', 3, 4, 1)

def writeMeter(self, openetran):
    grid = self.Meter.layout()

    # Number of Meters in the system
    num = len(openetran['meter'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addMeter(self, grid)

    countTotal = grid.count()
    count = 0 # current count of the elements in the layout
    i = 0 # index of the current list (each key containing a list of lists)

    rowStart = 2
    rowEnd = rowStart + 2

    while count < countTotal:
        # List of positions of each text fields in the layout
        positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(1, 4, 2)]
        k = 0

        for position in positions:
            count = (position[0] + 1) * (position[1] + 1)

            if position[0] == (rowEnd - 1) and position[1] == 3:
                continue

            # Slightly different function if it's a combo box to set the text
            elif position[0] == rowStart and position[1] == 1:
                v = openetran['meter'][i][k]
                widget = grid.itemAtPosition(position[0], position[1]).widget()

                if v == '':
                    widget.setCurrentIndex(0)
                else:
                    widget.setCurrentIndex(int(v))

                k += 1

            else:
                v = openetran['meter'][i][k]
                widget = grid.itemAtPosition(position[0], position[1]).widget()
                widget.setText(v)

                k += 1

        rowStart = rowEnd + 1
        rowEnd = rowStart + 2
        i += 1
        k = 0

def writeLabel(self, openetran):
    grid = self.Label.layout()

    # Number of Meters in the system
    num = len(openetran['label'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addLabel(self, grid)

    countTotal = grid.count()
    count = 0 # current count of the elements in the layout
    i = 0 # index of the current list (each key containing a list of lists)

    rowStart = 2
    rowEnd = rowStart + 2

    while count < countTotal:
        # List of positions of each text fields in the layout
        positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(1, 4, 2)]
        k = 0

        for position in positions:
            count = (position[0] + 1) * (position[1] + 1)

            if position[0] == (rowEnd - 1) and position[1] == 3:
                continue

            # Slightly different function if it's a combo box to set the text
            elif position[0] == rowStart and position[1] == 1:
                v = openetran['label'][i][k]
                widget = grid.itemAtPosition(position[0], position[1]).widget()

                if v == 'Phase':
                    widget.setCurrentIndex(0)
                else:
                    widget.setCurrentIndex(1)

                k += 1

            else:
                v = openetran['label'][i][k]
                widget = grid.itemAtPosition(position[0], position[1]).widget()
                widget.setText(v)

                k += 1

        rowStart = rowEnd + 1
        rowEnd = rowStart + 2
        i += 1
        k = 0

def writeResistor(self, openetran):
    grid = self.Resistor.layout()

    # Number of Meters in the system
    num = len(openetran['resistor'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addResistor(self, grid)

    writeWidgets(openetran, grid, 'resistor', 2, 4, 1)

def writeCapacitor(self, openetran):
    grid = self.Capacitor.layout()

    # Number of Meters in the system
    num = len(openetran['capacitor'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addCapacitor(self, grid)

    writeWidgets(openetran, grid, 'capacitor', 2, 4, 1)

def writeInductor(self, openetran):
    grid = self.Inductor.layout()

    # Number of Meters in the system
    num = len(openetran['inductor'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addInductor(self, grid)

    writeWidgets(openetran, grid, 'inductor', 2, 4, 0)

def writeCustomer(self, openetran):
    grid = self.Customer.layout()

    # Number of Meters in the system
    num = len(openetran['customer'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addCustomer(self, grid)

    writeWidgets(openetran, grid, 'customer', 6, 6, 1)

def writePipegap(self, openetran):
    grid = self.Pipegap.layout()

    # Number of Meters in the system
    num = len(openetran['pipegap'])

    if num > 1:
        for k in range(num - 1):
            Add_Delete_Widgets.addPipegap(self, grid)

    writeWidgets(openetran, grid, 'pipegap', 2, 4, 0)