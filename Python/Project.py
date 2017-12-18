# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 2016

Script with functions to save, load and simulate the project

@author: Matthieu Bertin
"""

import json, subprocess
import os.path as osp
import platform
from PyQt5.QtWidgets import QFileDialog
from openetran_py3 import WriteGUI, ParseInput, CSVRead, Plot2D

# Writes main structure into .JSON file
def saveProject(self, openetran, lastDirectory):
    fileDialog = QFileDialog()

    if lastDirectory == '':
        name = fileDialog.getSaveFileName(None, 'Save File', '/home', 'JSON Files (*.json)')
    else:
        name = fileDialog.getSaveFileName(None, 'Save File', lastDirectory, 'JSON Files (*.json)')

    if name == ('',''):
        print('Save cancelled')
        return lastDirectory
    else:
       openetran['name'] = name[0]
       lastDirectory = osp.dirname(name[0])

    with open(name[0], 'w') as f:
        json.dump(openetran, f, indent=2)

    print('Project saved')
    return lastDirectory

# Reads main structure from .JSON file
def loadProject(self, guiNormal, lastDirectory):
    openetran = dict()
    fileDialog = QFileDialog()
    dispNormal = False

    # Get project name
    if lastDirectory == '':
        name = fileDialog.getOpenFileName(None, 'Save File', '/home', 'JSON Files (*.json)')
    else:
        name = fileDialog.getOpenFileName(None, 'Save File', lastDirectory, 'JSON Files (*.json)')

    if name == ('',''):
        print('Load cancelled')
        return lastDirectory
    else:
        lastDirectory = osp.dirname(name[0])

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
    print('Project loaded')
    return lastDirectory

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
    prefix = osp.dirname(prefix)

    # OpenEtran executable file path depending on the machine's operating system
    opSys = platform.platform()

    if 'Windows' in opSys:
        prefix = osp.join(prefix, 'win')
        execName = osp.join(prefix, 'openetran.exe')

    elif 'Linux' in opSys:
        prefix = osp.join(prefix, 'linux')
        execName = osp.join(prefix, 'openetran')

    elif 'Mac' in opSys:
        prefix = osp.join(prefix, 'macosx')
        execName = osp.join(prefix, 'openetran')

    else:
        print('Architecture not recognized or not compatible')
        return

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
        pole1 = grid.itemAtPosition(7, 1).widget().text()
        pole2 = grid.itemAtPosition(8, 1).widget().text()
        wire = grid.itemAtPosition(9, 1).widget().text()

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