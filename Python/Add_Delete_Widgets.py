# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 10:11:59 2017

Function used to dynamically add and remove widgets on each tabs

@author: Matthieu Bertin
"""

from PyQt5.QtWidgets import (QLineEdit, QLabel, QComboBox)

# General function to add widgets
def addWidgets(grid, names, rowOffset, numCol):
    LPM_KI = '7.785e-07'
    LPM_E0 = '535e+03'
    Ground_E0 = '400e+03'
    Arrbez_ref = '0.051'

    count = grid.count()
    rowStart = int(count / numCol)  # Number of colums and number of elements are
                                    # always even, so the result will always be an int.
                                    # Still needs to be converted because the result is
                                    # typed as a float by default
    rowEnd = rowStart + rowOffset
    positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(numCol)]

    for position, name in zip(positions, names):
        if name == '' or name == LPM_KI or name == LPM_E0 or name == Ground_E0 or name == Arrbez_ref:
            widget = QLineEdit(name)

        elif name == '/':
            widget = QLabel()

        else:
            widget = QLabel(name)

        grid.addWidget(widget, *position)

# General function to remove widgets
def removeWidgets(grid, initCount, rowOffset, numCol):
    count = grid.count()

    # No widgets left to delete
    if count == initCount:
        return 1

    rowEnd = int(count / numCol)
    rowStart = rowEnd - rowOffset
    positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(numCol)]

    # Removing a widget's parents removes the widget in PyQt
    for position in positions:
        widget = grid.itemAtPosition(position[0], position[1]).widget()
        widget.setParent(None)

    return 0

def addConductor(self, grid):
    names = ['Conductor', '/', '/', '/',
             'Number', '', 'Height (m)', '',
             'Horizontal Position (m)', '','Radius (m)', '',
             'Voltage Bias (V)', '', 'Sag (m)', '',
             'Nb', '', 'Sb (m)', '']

    addWidgets(grid, names, 5, 4)

def deleteConductor(self, grid):
    # 28 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 24, 5, 4)

def addGround(self, grid):
    names = ['Ground', '/', '/', '/', '/', '/',
             'R60 (Ohm)', '', 'Resistivity (Ohm.m)', '',
             'Soil Breakdown Gradient (V.m)', '400e+03',
             'Downlead Inductance (H/m)', '', 'Length of downlead (m)', '',
             'Counterpoise radius (m)', '', 'Counterpoise depth (m)', '',
             'Counterpoise length (m)', '', 'Number of segments', '',
             'Soil relative permittivity', '',
             'Pairs', '', 'Poles', '']

    addWidgets(grid, names, 5, 6)

# Function strictly identical to the one deleting conductors. No need to rewrite it.
def deleteGround(self, grid):
    # 36 is the number of elements when the tab was first created (including buttons)
    return removeWidgets(grid, 36, 5, 6)

def addArrester(self, grid):
    names = ['Arrester', '/', '/', '/',
             'Sparkover voltage (V)', '', 'Turn-on voltage (V)', '',
             'Characteristic"s slope (Ohm)', '', 'Inductance of lead (H/m)', '',
             'Lead length (m)', '', 'Pairs', '',
             'Poles', '', '/', '/']

    addWidgets(grid, names, 5, 4)

def deleteArrester(self, grid):
    # 24 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 24, 5, 4)

def addArrbez(self, grid):
    names = ['Arrbez', '/', '/', '/',
             'Sparkover voltage (V)', '', '10kA 8x20 discharge voltage (V)', '',
             'Reference voltage (p.u.)', '0.051', 'Inductance of lead (H/m)', '',
             'Lead length (m)', '', 'Plot arrester current ? (1/0)', '',
             'Pairs', '', 'Poles', '']

    addWidgets(grid, names, 5, 4)

# That function is the same as the one used to delete conductor widgets
def deleteArrbez(self, grid):
    # 24 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 24, 5, 4)

def addInsulator(self, grid):
    names = ['Insulator', '/', '/', '/',
             'CFO (V)', '', 'Minimum volt. for destructive effects (V)', '',
             'beta (no unit)', '', 'DE', '',
             'Pairs', '', 'Poles', '']

    addWidgets(grid, names, 4, 4)

def deleteInsulator(self, grid):
    # 20 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 20, 4, 4)

def addLPM(self, grid):
    names = ['LPM', '/', '/', '/',
             'CFO (V)', '', 'E0 (V/m)', '535e+03',
             'Kl (no unit)', '7.785e-07', 'Pairs', '',
             'Poles', '', '/', '/']

    addWidgets(grid, names, 4, 4)

def deleteLPM(self, grid):
    # 20 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 20, 4, 4)

def addMeter(self, grid):
    names = ['Meter', '/', '/', '/',
             'Type', '//', 'Pairs', '',
             'Poles', '', '/', '/']

    count = grid.count()
    rowStart = int(count / 4)
    rowEnd = rowStart + 3
    positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(4)]

    for position, name in zip(positions, names):
        if name == '':
            widget = QLineEdit()

        elif name == '/':
            widget = QLabel()

        elif name == '//':
            widget = QComboBox()
            widget.addItem('Voltage')
            widget.addItem('Arrester/Arrbez current')
            widget.addItem('Ground current')
            widget.addItem('Customer house current')
            widget.addItem('Transformer X2 term. current')
            widget.addItem('Pipegap current')

        else:
            widget = QLabel(name)

        grid.addWidget(widget, *position)

def deleteMeter(self, grid):
    # 16 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 16, 3, 4)

def addLabel(self, grid):
    count = grid.count()
    rowStart = int(count / 4)
    rowEnd = rowStart + 3
    positions = [(i,j) for i in range(rowStart, rowEnd) for j in range(4)]

    names = ['Label', '/', '/', '/',
             'Type', '//', 'Element number', '',
             'Name', '', '/', '/']

    for position, name in zip(positions, names):
        if name == '':
            widget = QLineEdit()

        elif name == '/':
            widget = QLabel()

        elif name == '//':
            widget = QComboBox()
            widget.addItem('Phase')
            widget.addItem('Pole')

        else:
            widget = QLabel(name)

        grid.addWidget(widget, *position)

def deleteLabel(self, grid):
    # 16 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 16, 3, 4)

def addResistor(self, grid):
    names = ['Resistor', '/', '/', '/',
             'Value (Ohm)', '', 'Pairs', '',
             'Poles', '', '/', '/']

    addWidgets(grid, names, 3, 4)

def deleteResistor(self, grid):
    # 12 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 16, 3, 4)

def addCapacitor(self, grid):
    names = ['Capacitor', '/', '/', '/',
             'Value (F)', '', 'Pairs', '',
             'Poles', '', '/', '/']

    addWidgets(grid, names, 3, 4)

def deleteCapacitor(self, grid):
    # 12 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 16, 3, 4)

def addInductor(self, grid):
    names = ['Inductor', '/', '/', '/',
             'Series resistance (Ohm)', '', 'Value (H)', '',
             'Pairs', '', 'Poles', '']

    addWidgets(grid, names, 3, 4)

def deleteInductor(self, grid):
    # 12 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 16, 3, 4)

def addCustomer(self, grid):
    names = ['Customer', '/', '/', '/', '/', '/',
             'Rhg (Ohm)', '', 'Soil resistivity (Ohm.m)', '', 'E0 (V/m)', '',
             'Lhg (H/m)', '', 'Ground lead length (m)', '', 'Transf. turns ratio', '',
             'Lp (H)', '', 'Ls1 (H)', '', 'Ls2 (H)', '',
             'Lcm (H/m)', '', 'rA (m)', '', 'rN (m)', '',
             'Dan (m)', '', 'Daa (m)', '', 'Service drop length (m)', '',
             'Pairs', '', 'Poles', '', '/', '/']

    addWidgets(grid, names, 7, 6)

def deleteCustomer(self, grid):
    # 42 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 48, 7, 6)

def addPipegap(self, grid):
    names = ['Pipegap', '/', '/', '/',
             'CFO between conductors (V)', '', 'Series resistance (Ohm)', '',
             'Pairs', '', 'Poles', '']

    addWidgets(grid, names, 3, 4)

def deletePipegap(self, grid):
    # 12 is the number of elements when the tab was first created (including buttons)
    # We delete all the conductor widgets, except for the 'New' and 'Delete' buttons
    return removeWidgets(grid, 16, 3, 4)