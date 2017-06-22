# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 2016

Script with functions to save, load and simulate the project

@author: Matthieu Bertin
"""

import json, subprocess
import os.path as osp
from PyQt5.QtWidgets import QFileDialog
import WriteGUI, ParseInput, CSVRead, Plot2D
#from pkg_resources import resource_filename

# Writes main structure into .JSON file
def saveProject(self, openetran):
    fileDialog = QFileDialog()

    name = fileDialog.getSaveFileName(None, 'Save File', '/home', 'JSON Files (*.json)')

    if name == ('',''):
        return
    else:
       openetran['name'] = name[0]

    with open(name[0], 'w') as f:
        json.dump(openetran, f, indent=2)

# Reads main structure from .JSON file
def loadProject(self, guiNormal):
    openetran = dict()
    fileDialog = QFileDialog()
    dispNormal = False

    # Get project name
    name = fileDialog.getOpenFileName(None, 'Save File', '/home', 'JSON Files (*.json)')

    if name == ('',''):
        return

    with open(name[0], 'r') as f:
        openetran = json.load(f)
        openetran['name'] = name[0]

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

    # If there's an error during saving and no project name, then abort simulation
    try:
        test = openetran['name']
    except KeyError:
        return

    del[test]

    # Writes main structure in openetran .dat input file
    ParseInput.write(openetran)

    # OpenEtran input .dat file name
    k = len(openetran['name'])
    inputFileName = openetran['name'][0:k-5] + '.dat'

    # Executable file name prefix
    prefix = WriteGUI.__file__

    k = len(prefix) - 4
    j = prefix[k] # j starts as the last letter of the filename, before the extension

    while (j != '/' and j != "\\"):
        k -= 1
        j = prefix[k]

    prefix = prefix[0:k]

    # OpenEtran executable file path
    execName = osp.join(prefix, 'openetran.exe')

    # One shot simulation mode with .csv plot files
    if plotMode.isChecked() == True:
        args = [execName, '-plot', 'csv', inputFileName]
        completedProcess = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                          universal_newlines=True)

        print(completedProcess.stdout)
        print('Simulation done\n')

        if 'OpenEtran Error' in completedProcess.stderr:
            print(completedProcess.stderr)

        elif completedProcess.returncode != 0:
            print('OpenEtran crashed\n')
            print(completedProcess.stderr)
            return

        else:
            # Interpreting the output .csv file
            k = len(openetran['name'])
            outputFileName = openetran['name'][0:k-5] + '.csv'
            CSVRead.read(outputFileName, outputDict)

            # Plot the data using matplotlib
            Plot2D.draw(outputDict)

    # Critical current iteration mode, no plot files
    else:
        grid = self.Simulation.layout()

        # Text file with the results for the critical currents
        k = len(openetran['name'])
        outputFileName = openetran['name'][0:k-5] + '.txt'

        # Strings from the text fields
        pole1 = grid.itemAtPosition(3, 3).widget().text()
        pole2 = grid.itemAtPosition(4, 3).widget().text()
        wire = grid.itemAtPosition(5, 3).widget().text()

        # Str lists for the pole sequence for when OpenEtran is called
        poleSeq = list()
        wireSeq = list()

        try:
            firstPole = int(pole1)
        except ValueError:
            print('Err! "First pole to hit" field must be an int')
            return

        try:
            lastPole = int(pole2)
        except ValueError:
            print('Err! "First pole to hit" field must be an int')
            return

        if firstPole <= 0 or lastPole <= 0:
            print('Pole1 and Pole2 must be positive numbers')
            return

        if firstPole > lastPole:
            print('First pole must be < than last pole')
            return

        # Writes the pole sequence for OpenEtran
        k = 0
        for k in range(firstPole, lastPole+1):
            poleSeq.append(str(k))

        for i in range(0, len(wire), 2):
            if wire[i] == '' or (wire[i] != '1' and wire[i] != '0'):
                print('Invalid wire sequence')
                return

            else:
                wireSeq.append(wire[i])

        f = open(outputFileName, 'w')

        # We call OpenEtran with wire1 = wire2 (see OpenEtran doc) in a loop
        # for each selected pole
        for i in poleSeq:
            if len(wireSeq) == 1:
                args = [execName, '-icrit', i, i, wireSeq[0], inputFileName]

            elif len(wireSeq) == 2:
                args = [execName, '-icrit', i, i, wireSeq[0], wireSeq[1], inputFileName]

            elif len(wireSeq) == 3:
                args = [execName, '-icrit', i, i, wireSeq[0], wireSeq[1], wireSeq[2], inputFileName]

            elif len(wireSeq) == 4:
                args = [execName, '-icrit', i, i, wireSeq[0], wireSeq[1], wireSeq[2], \
                        wireSeq[3], inputFileName]

            elif len(wireSeq) == 5:
                args = [execName, '-icrit', i, i, wireSeq[0], wireSeq[1], wireSeq[2], \
                        wireSeq[3], wireSeq[4], inputFileName]

            else:
                print('Invalid wire sequence')
                f.close()
                return

            completedProcess = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              universal_newlines=True)

            print(completedProcess.stdout)
            f.write(completedProcess.stdout)

            if completedProcess.returncode != 0:
                print('OpenEtran crashed\n')
                print(completedProcess.stderr)
                f.close()
                return

            elif 'Error' in completedProcess.stderr:
                print(completedProcess.stderr)
                f.close()
                return

        print('Simulation done')
        f.close()