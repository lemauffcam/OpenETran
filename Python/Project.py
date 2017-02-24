# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 2016

Saves main structure into a JSON file

@author: Matthieu
"""

import json
import subprocess

import WriteGUI
import ParseInput
import CSVRead
import Plot2D

# Writes main structure into .JSON file
def saveProject(openetran, name):
    with open(name + '.json', 'w') as f:
        json.dump(openetran, f, indent=2)

# Reads main structure from .JSON file
def loadProject(self, guiNormal):
    openetran = dict()
    dispNormal = False

    # Get project name
    layout = self.Project.layout()
    widget = layout.itemAtPosition(0, 2).widget()
    name = widget.text()

    if name == '':
        print('Error, no project name')
        return

    else:
        with open(name + '.json', 'r') as f:
            openetran = json.load(f)

        for k in openetran.keys():
            # If we find the arrester key, then we need to display the extended interface
            if k == 'arrester' and guiNormal.isChecked() == False:
                guiNormal.toggle()
                dispNormal = True

        # Write all values in the GUI text fields
        WriteGUI.write(self, openetran, dispNormal)

# Parses input file from main structure and calls openetran
def simulateProject(plotMode, self, openetran):
    outputDict = dict()

    # Writes main structure in openetran .dat input file
    ParseInput.write(openetran)

    # OpenEtran input .dat file name
    inputFileName = openetran['name'] + '.dat'

    # One shot simulation mode with .csv plot files
    if plotMode.isChecked() == True:
        completedProcess = subprocess.run(["openetran.exe", "-plot", "csv", inputFileName],
                          stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

        print(completedProcess.stdout)

        if 'OpenEtran Error' in completedProcess.stderr:
            print(completedProcess.stderr)
            return

        elif completedProcess.returncode != 0:
            print('OpenEtran crashed')
            return

        else:
            # Interpreting the output .csv file
            outputFileName = openetran['name'] + '.csv'
            CSVRead.read(openetran, outputFileName, outputDict)

            # Plot the data using matplotlib
            Plot2D.draw(outputDict)

    # Critical current iteration mode, no plot files
    else:
        grid = self.Simulation.layout()

        # Strings from the text fields
        pole1 = grid.itemAtPosition(3, 3).widget().text()
        pole2 = grid.itemAtPosition(4, 3).widget().text()
        wire = grid.itemAtPosition(5, 3).widget().text()

        # Str lists for the pole sequence for when OpenEtran is called
        poleSeq = list()

        if pole1.isdigit() == True and pole2.isdigit() == True:
            if int(pole1) <= 0 or int(pole2) <= 0:
                print('Pole1 and Pole2 must be positive numbers')
                return

            firstPole = int(pole1)
            lastPole = int(pole2)

            if lastPole > firstPole:
                k = 0
                for k in range(firstPole, lastPole+1):
                    poleSeq.append(str(k))

            elif lastPole < firstPole:
                k = 0
                for k in range(lastPole, firstPole+1):
                    poleSeq.append(str(k))

            else:
                poleSeq.append(pole1)

        else:
            print('Pole1 and Pole2 must be single numbers')
            return

        for i in poleSeq:
            # Recommanded to run the critical current mode with wire1 = wire2 (see OpenEtran) doc
            completedProcess = subprocess.run(["openetran.exe", "-icrit", i, i, wire, inputFileName],
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

            if 'OpenEtran Error' in completedProcess.stderr:
                print(completedProcess.stderr)
                return

            elif completedProcess.returncode != 0:
                print('OpenEtran crashed')
                return

            else:
                print(completedProcess.stdout)