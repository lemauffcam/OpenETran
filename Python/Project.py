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
    i = layout.count() - 3
    widget = layout.itemAt(i).widget()
    name = widget.text()

    if name == '':
        print('Error, no project name')
        return

    else:
        with open(name + '.json', 'r') as f:
            openetran = json.load(f)

        # By default we start with the simplified GUI
        if guiNormal.isChecked() == True:
            guiNormal.toggle()

        for k in openetran.keys():
            # If we find the arrester key, then we need to display the extended interface
            if k == 'arrester' and guiNormal.isChecked() == False:
                guiNormal.toggle()
                dispNormal = True

        # Write all values in the GUI text fields
        WriteGUI.write(self, openetran, dispNormal)

# Parses input file from main structure and calls openetran
def simulateProject(openetran):
    outputDict = dict()

    # Writes main structure in openetran .dat input file
    ParseInput.write(openetran)

    # Calls openetran with the input file, output as a .csv file
    inputFileName = openetran['name'] + '.dat'
    completedProcess = subprocess.run(["openetran.exe", "-plot", "csv", inputFileName],
                                      stderr=subprocess.PIPE, universal_newlines=True)

    if 'OpenEtran Error' in completedProcess.stderr:
        print(completedProcess.stderr)
        return

    else:
        # Interpreting the output .csv file
        outputFileName = openetran['name'] + '.csv'
        CSVRead.read(openetran, outputFileName, outputDict)

        # Plot the data using Mathplotlib
        Plot2D.draw(outputDict)