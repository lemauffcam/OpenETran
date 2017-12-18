# -*- coding: utf-8 -*-
"""
Created on Wed Jan 4 2017
OpenEtran GUI main Python file
@author: Matthieu Bertin - University of Pittsburgh
"""

import sys
from PyQt5.QtWidgets import (QApplication, QTabWidget, QWidget, QGridLayout,
                             QPushButton, QLineEdit, QLabel, QComboBox, QRadioButton)
from PyQt5.QtCore import pyqtSlot
from openetran_py3 import Project, ReadStruct, Add_Delete_Widgets, R60, Draw

# Function to add widgets on the tabs for the 1st time
def addWidgets(grid, names, rowEnd, ColEnd):
    LPM_KI = '7.785e-07'
    LPM_E0 = '535e+03'
    Ground_E0 = '400e+03'
    Arrbez_ref = '0.051'

    positions = [(i,j) for i in range(rowEnd) for j in range(ColEnd)]
    for position, name in zip(positions, names):
        if name == '' or name == LPM_KI or name == LPM_E0 or name == Ground_E0 or name == Arrbez_ref:
            widget = QLineEdit(name)

        elif name == 'New' or name == 'Delete' or name == 'Get Counterpoise R60':
            widget = QPushButton(name)

        elif name == '/':
            widget = QLabel()

        else:
            widget = QLabel(name)

        grid.addWidget(widget, *position)

# Function to connect the Add/Delete buttons on each tabs, which are always located at positions
# (0,0) and (0,1) respectively in the tab's layout.
def connectButtons(layout, newFunction, deleteFunction):
    new = layout.itemAtPosition(0,0).widget()
    new.pressed.connect(newFunction)

    delete = layout.itemAtPosition(0,1).widget()
    delete.pressed.connect(deleteFunction)

class GUi_Tab(object):
    def setupUi(self, Tab):
        Tab.setWindowTitle('OpenETran')

        # Project Tab
        self.Project = QWidget()
        grid = QGridLayout()

        save = QPushButton('Save')
        load = QPushButton('Load')

        # RadioButtons to select the simplified or full interface. Simplified selected by default
        guiSimple = QRadioButton('Simplified interface')
        guiNormal = QRadioButton('Full interface')

        guiSimple.setChecked(True)

        grid.addWidget(save, 0, 0)
        grid.addWidget(load, 0, 1)
        grid.addWidget(guiSimple, 0, 3)
        grid.addWidget(guiNormal, 0, 4)

        self.Project.setLayout(grid)
        Tab.addTab(self.Project, 'Project')

        # Simulation Tab
        self.Simulation = QWidget()
        grid = QGridLayout()
        self.Simulation.setLayout(grid)

        names = ['Number of conductors', '', 'Number of poles', '', 'Line Span (m)', '',
                 'Left Termination (1/0)', '', 'Right Termination (1/0)', '',
                 'Time Step (s)', '', 'Simulation Max Time (s)', '']

        addWidgets(grid, names, 7, 2)

        simulate = QPushButton('Simulate !')
        grid.addWidget(simulate, 0,  3)

        # RadioButtons for the simulation mode - One shot mode is selected by default
        plotMode = QRadioButton('One shot mode simulation')
        plotMode.setChecked(True)
        grid.addWidget(plotMode, 1, 3)

        critMode = QRadioButton('Critical current iteration simulation')
        grid.addWidget(critMode, 2, 3)

        # LineEdit fields for Critical current iteration mode
        pole1 = QLineEdit()
        pole2 = QLineEdit()
        wire = QLineEdit()

        pole1_text = QLabel('First pole to hit')
        pole2_text = QLabel('Last pole to hit')
        wire_text = QLabel('Wire sequence')

        Tab.addTab(self.Simulation, 'Simulation')

        # Conductor Tab
        self.Conductor = QWidget()
        grid = QGridLayout()
        self.Conductor.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Conductor', '/', '/', '/',
                 'Number', '', 'Height (m)', '',
                 'Horizontal Position (m)', '','Radius (m)', '',
                 'Voltage Bias (V)', '', 'Sag (m)', '',
                 'Nb', '', 'Sb (m)', '']

        addWidgets(grid, names, 6, 4)

        Tab.addTab(self.Conductor, 'Conductors')

        # Label Tab
        self.Label = QWidget()
        grid = QGridLayout()
        self.Label.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Label', '/', '/', '/',
                 'Type', '//', 'Element number', '',
                 'Name', '', '/', '/']

        positions = [(i,j) for i in range(4) for j in range(4)]
        for position, name in zip(positions, names):
            if name == '':
                widget = QLineEdit()

            elif name == 'New' or name == 'Delete':
                widget = QPushButton(name)

            elif name == '/':
                widget = QLabel()

            elif name == '//':
                widget = QComboBox()
                widget.addItem('Phase')
                widget.addItem('Pole')

            else:
                widget = QLabel(name)

            grid.addWidget(widget, *position)

        Tab.addTab(self.Label, 'Labels')

        # Ground Tab
        self.Ground = QWidget()
        grid = QGridLayout()
        self.Ground.setLayout(grid)

        names = ['New', 'Delete', 'Get Counterpoise R60', '/', '/', '/',
                 'Ground', '/', '/', '/', '/', '/',
                 'R60 (Ohm)', '', 'Resistivity (Ohm.m)', '', 'Soil Breakdown Gradient (V.m)', '400e+03',
                 'Downlead Inductance (H/m)', '', 'Length of downlead (m)', '', 'Counterpoise radius (m)', '',
                 'Counterpoise depth (m)', '', 'Counterpoise length (m)', '', 'Number of segments', '',
                 'Soil relative permittivity', '', 'Pairs', '', 'Poles', '']

        addWidgets(grid, names, 6, 6)

        Tab.addTab(self.Ground, 'Ground')

        # Surge Tab with surge parameters
        self.Surge = QWidget()
        grid = QGridLayout()
        self.Surge.setLayout(grid)

        names = ['Crest Current (A)', '', '30-90 Front Time (s)', '',
                 '50% Fail Time (s)', '', 'Surge Starting Time (s)', '',
                 'Pairs', '', 'Poles', '']

        addWidgets(grid, names, 6, 2)

        Tab.addTab(self.Surge, 'Surge')

        # Steepfront Tab - not added by default (not part of simplified interface)
        self.Steepfront = QWidget()
        grid = QGridLayout()
        self.Steepfront.setLayout(grid)

        names = ['Crest Current (A)', '', '30-90 Front Time (s)', '',
                 '50% Fail Time (s)', '', 'Surge Starting Time (s)', '',
                 'Max Current Steepness (per unit)', '', 'Pairs', '',
                 'Poles', '']

        addWidgets(grid, names, 7, 2)

        # Arrester Tab - not added by default (not part of simplified interface)
        self.Arrester = QWidget()
        grid = QGridLayout()
        self.Arrester.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Arrester', '/', '/', '/',
                 'Sparkover voltage (V)', '', 'Turn-on voltage (V)', '',
                 'Characteristic"s slope (Ohm)', '', 'Inductance of lead (H/m)', '',
                 'Lead length (m)', '', 'Pairs', '',
                 'Poles', '', '/', '/']

        addWidgets(grid, names, 6, 4)

        # Arrbez Tab
        self.Arrbez = QWidget()
        grid = QGridLayout()
        self.Arrbez.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Arrbez', '/', '/', '/',
                 'Sparkover voltage (V)', '', '10kA 8x20 discharge voltage (V)', '',
                 'Reference voltage (p.u)', '0.051', 'Inductance of lead (H/m)', '',
                 'Lead length (m)', '', 'Plot arrester current ? (1/0)', '',
                 'Pairs', '', 'Poles', '']

        addWidgets(grid, names, 6, 4)

        Tab.addTab(self.Arrbez, 'Arrbez')

        # Insulator Tab - not added by default (not part of simplified interface)
        self.Insulator = QWidget()
        grid = QGridLayout()
        self.Insulator.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Insulator', '/', '/', '/',
                 'CFO (V)', '', 'Minimum volt. for destructive effects (V)', '',
                 'beta (no unit)', '', 'DE', '',
                 'Pairs', '', 'Poles', '']

        addWidgets(grid, names, 5, 4)

        # LPM Tab
        self.LPM = QWidget()

        grid = QGridLayout()
        self.LPM.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'LPM', '/', '/', '/',
                 'CFO (V)', '', 'E0 (V/m)', '535e+03',
                 'Kl (no unit)', '7.785e-07', 'Pairs', '',
                 'Poles', '', '/', '/']

        addWidgets(grid, names, 5, 4)

        Tab.addTab(self.LPM, 'LPM')

        # Meter Tab
        self.Meter = QWidget()
        grid = QGridLayout()
        self.Meter.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Meter', '/', '/', '/',
                 'Type', '//', 'Pairs', '',
                 'Poles', '', '/', '/']

        positions = [(i,j) for i in range(4) for j in range(4)]
        for position, name in zip(positions, names):
            if name == '':
                widget = QLineEdit()

            elif name == 'New' or name == 'Delete':
                widget = QPushButton(name)

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

        Tab.addTab(self.Meter, 'Meter')

        # Resistor Tab - not added by default (not part of simplified interface)
        self.Resistor = QWidget()
        grid = QGridLayout()
        self.Resistor.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Resistor', '/', '/', '/',
                 'Value (Ohm)', '', 'Pairs', '',
                 'Poles', '', '/', '/']

        addWidgets(grid, names, 4, 4)
        Tab.addTab(self.Resistor, 'Resistor')

        # Capacitor Tab - not added by default (not part of simplified interface)
        self.Capacitor = QWidget()
        grid = QGridLayout()
        self.Capacitor.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Capacitor', '/', '/', '/',
                 'Value (F)', '', 'Pairs', '',
                 'Poles', '', '/', '/']

        addWidgets(grid, names, 4, 4)

        # Inductor Tab
        self.Inductor = QWidget()
        grid = QGridLayout()
        self.Inductor.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Inductor', '/', '/', '/',
                 'Series resistance (Ohm)', '', 'Value (H)', '',
                 'Pairs', '', 'Poles', '']

        addWidgets(grid, names, 4, 4)

        # Customer Tab - not added by default (not part of simplified interface)
        self.Customer = QWidget()
        grid = QGridLayout()
        self.Customer.setLayout(grid)

        names = ['New', 'Delete', '/', '/', '/', '/',
                 'Customer', '/', '/', '/', '/', '/',
                 'Rhg (Ohm)', '', 'Soil resistivity (Ohm.m)', '', 'E0 (V/m)', '',
                 'Lhg (H/m)', '', 'Ground lead length (m)', '', 'Transf. turns ratio', '',
                 'Lp (H)', '', 'Ls1 (H)', '', 'Ls2 (H)', '',
                 'Lcm (H/m)', '', 'rA (m)', '', 'rN (m)', '',
                 'Dan (m)', '', 'Daa (m)', '', 'Service drop length (m)', '',
                 'Pairs', '', 'Poles', '', '/', '/']

        addWidgets(grid, names, 8, 6)

        # Pipegap Tab - not added by default (not part of simplified interface)
        self.Pipegap = QWidget()
        grid = QGridLayout()
        self.Pipegap.setLayout(grid)

        names = ['New', 'Delete', '/', '/',
                 'Pipegap', '/', '/', '/',
                 'CFO between conductors (V)', '', 'Series resistance (Ohm)', '',
                 'Pairs', '', 'Poles', '']

        addWidgets(grid, names, 4, 4)

        @pyqtSlot()
        def dispNormal():
            if guiNormal.isChecked() == True:
                Tab.addTab(self.Steepfront, 'Steepfront')
                Tab.addTab(self.Arrester, 'Arrester')
                Tab.addTab(self.Insulator, 'Insulator')
                # Tab.addTab(self.Resistor, 'Resistor')
                Tab.addTab(self.Capacitor, 'Capacitor')
                Tab.addTab(self.Inductor, 'Inductor')
                Tab.addTab(self.Customer, 'Customer')
                Tab.addTab(self.Pipegap, 'Pipegap')

        @pyqtSlot()
        def dispSimple():
            if guiSimple.isChecked() == True:
                Tab.removeTab( Tab.indexOf(self.Steepfront) )
                Tab.removeTab( Tab.indexOf(self.Arrester) )
                Tab.removeTab( Tab.indexOf(self.Insulator) )
                # Tab.removeTab( Tab.indexOf(self.Resistor) )
                Tab.removeTab( Tab.indexOf(self.Capacitor) )
                Tab.removeTab( Tab.indexOf(self.Inductor) )
                Tab.removeTab( Tab.indexOf(self.Customer) )
                Tab.removeTab( Tab.indexOf(self.Pipegap) )

        @pyqtSlot()
        def simOneShot():
            if plotMode.isChecked() == True:
                pole1.setParent(None)
                pole2.setParent(None)
                wire.setParent(None)

                pole1_text.setParent(None)
                pole2_text.setParent(None)
                wire_text.setParent(None)

        @pyqtSlot()
        def simCrit():
            if critMode.isChecked() == True:
                grid = self.Simulation.layout()
                grid.addWidget(pole1_text, 7, 0)
                grid.addWidget(pole2_text, 8, 0)
                grid.addWidget(wire_text, 9, 0)

                grid.addWidget(pole1, 7, 1)
                grid.addWidget(pole2, 8, 1)
                grid.addWidget(wire, 9, 1)

        @pyqtSlot()
        def simulateProject():
            openetran = saveProject()
            Project.simulateProject(plotMode, self, openetran)

        @pyqtSlot()
        def saveProject():
            # Read the structure in the GUI in case it changed
            openetran = ReadStruct.read(self, guiNormal)
            self.lastDirectory = Project.saveProject(self, openetran, self.lastDirectory)

            return openetran

        @pyqtSlot()
        def loadProject():
            self.lastDirectory = Project.loadProject(self, guiNormal, self.lastDirectory)

        @pyqtSlot()
        def newConductor():
            Add_Delete_Widgets.addConductor(self, self.Conductor.layout())

        @pyqtSlot()
        def deleteConductor():
            Add_Delete_Widgets.deleteConductor(self, self.Conductor.layout())

        @pyqtSlot()
        def newGround():
            Add_Delete_Widgets.addGround(self, self.Ground.layout())

        @pyqtSlot()
        def deleteGround():
            Add_Delete_Widgets.deleteGround(self, self.Ground.layout())

        @pyqtSlot()
        def calculateR60():
            openetran = ReadStruct.read(self, guiNormal)
            R60.calcR60(openetran, self.Ground.layout())

        @pyqtSlot()
        def newArrester():
            Add_Delete_Widgets.addArrester(self, self.Arrester.layout())

        @pyqtSlot()
        def deleteArrester():
            Add_Delete_Widgets.deleteArrester(self, self.Arrester.layout())

        @pyqtSlot()
        def newArrbez():
            Add_Delete_Widgets.addArrbez(self, self.Arrbez.layout())

        @pyqtSlot()
        def deleteArrbez():
            Add_Delete_Widgets.deleteArrbez(self, self.Arrbez.layout())

        @pyqtSlot()
        def newInsulator():
            Add_Delete_Widgets.addInsulator(self, self.Insulator.layout())

        @pyqtSlot()
        def deleteInsulator():
            Add_Delete_Widgets.deleteInsulator(self, self.Insulator.layout())

        @pyqtSlot()
        def newLPM():
            Add_Delete_Widgets.addLPM(self, self.LPM.layout())

        @pyqtSlot()
        def deleteLPM():
            Add_Delete_Widgets.deleteLPM(self, self.LPM.layout())

        @pyqtSlot()
        def newMeter():
            Add_Delete_Widgets.addMeter(self, self.Meter.layout())

        @pyqtSlot()
        def deleteMeter():
            Add_Delete_Widgets.deleteMeter(self, self.Meter.layout())

        @pyqtSlot()
        def newLabel():
            Add_Delete_Widgets.addLabel(self, self.Label.layout())

        @pyqtSlot()
        def deleteLabel():
            Add_Delete_Widgets.deleteLabel(self, self.Label.layout())

        @pyqtSlot()
        def newResistor():
            Add_Delete_Widgets.addResistor(self, self.Resistor.layout())

        @pyqtSlot()
        def deleteResistor():
            Add_Delete_Widgets.deleteResistor(self, self.Resistor.layout())

        @pyqtSlot()
        def newCapacitor():
            Add_Delete_Widgets.addCapacitor(self, self.Capacitor.layout())

        @pyqtSlot()
        def deleteCapacitor():
            Add_Delete_Widgets.deleteCapacitor(self, self.Capacitor.layout())

        @pyqtSlot()
        def newInductor():
            Add_Delete_Widgets.addInductor(self, self.Inductor.layout())

        @pyqtSlot()
        def deleteInductor():
            Add_Delete_Widgets.deleteInductor(self, self.Inductor.layout())

        @pyqtSlot()
        def newCustomer():
            Add_Delete_Widgets.addCustomer(self, self.Customer.layout())

        @pyqtSlot()
        def deleteCustomer():
            Add_Delete_Widgets.deleteCustomer(self, self.Customer.layout())

        @pyqtSlot()
        def newPipegap():
            Add_Delete_Widgets.addPipegap(self, self.Pipegap.layout())

        @pyqtSlot()
        def deletePipegap():
            Add_Delete_Widgets.deletePipegap(self, self.Pipegap.layout())

        # Connect buttons to each actions
        save.pressed.connect(saveProject)
        load.pressed.connect(loadProject)
        simulate.pressed.connect(simulateProject)

        # Conductor
        layout = self.Conductor.layout()
        connectButtons(layout, newConductor, deleteConductor)

        # Ground
        layout = self.Ground.layout()
        connectButtons(layout, newGround, deleteGround)

        calcR60 = layout.itemAtPosition(0,2).widget()
        calcR60.pressed.connect(calculateR60)

        # Arrester
        layout = self.Arrester.layout()
        connectButtons(layout, newArrester, deleteArrester)

        # Arrbez
        layout = self.Arrbez.layout()
        connectButtons(layout, newArrbez, deleteArrbez)

        # Insulator
        layout = self.Insulator.layout()
        connectButtons(layout, newInsulator, deleteInsulator)

        # LPM
        layout = self.LPM.layout()
        connectButtons(layout, newLPM, deleteLPM)

        # Meter
        layout = self.Meter.layout()
        connectButtons(layout, newMeter, deleteMeter)

        # Labels
        layout = self.Label.layout()
        connectButtons(layout, newLabel, deleteLabel)

        # Resistor
        layout = self.Resistor.layout()
        connectButtons(layout, newResistor, deleteResistor)

        # Capacitor
        layout = self.Capacitor.layout()
        connectButtons(layout, newCapacitor, deleteCapacitor)

        # Inductor
        layout = self.Inductor.layout()
        connectButtons(layout, newInductor, deleteInductor)

        # Customer
        layout = self.Customer.layout()
        connectButtons(layout, newCustomer, deleteCustomer)

        # Pipegap
        layout = self.Pipegap.layout()
        connectButtons(layout, newPipegap, deletePipegap)

        # RadioButtons
        guiSimple.toggled.connect(dispSimple)
        guiNormal.toggled.connect(dispNormal)

        plotMode.toggled.connect(simOneShot)
        critMode.toggled.connect(simCrit)

    # Used in the Visualization class to update the wires' coordinates
    # Returns a dictionnary with all wires' coordinates
    def readWireCoordinates(self):
        struct= dict()
        struct['conductor'] = list()

        ReadStruct.readConductor(self, struct)

        # If 4 wires, we change the 5th wire coordinates to be equal to the 4th wire
        if len(struct['conductor']) == 4:
            struct['conductor'].append(list(struct['conductor'][3]))
            struct['conductor'][4][0] = 5

        return struct

def main():
    app = QApplication(sys.argv)

    # Main tab window
    Tab = QTabWidget()

    ui = GUi_Tab()
    ui.lastDirectory = ''
    ui.setupUi(Tab)
    Draw.SysView(ui)

    Tab.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()