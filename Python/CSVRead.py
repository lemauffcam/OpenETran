# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:04:54 2016

Interprets the .csv output file from OpenETran. Each plot data is written
into a dictionnary.

@author: Matthieu Bertin
"""

import csv

def read(fileName, plotDict):
    with open(fileName, 'r', newline = '') as csvFile:
        # Read the csv file
        plots = csv.reader(csvFile, dialect = 'excel', delimiter = ',', quotechar = '|')
        keys = list()

        for row in plots:

            # First step is to create the keys from the 1st line of the .csv file
            if 'Time' == row[0]:
                for k in row:
                    if k in keys:
                        k = k+'_doublon'

                    plotDict[k] = list()
                    keys.append(k)

            # We can then fill each list in the dict.
            else:
                for k in range(len(keys)):
                    (plotDict[keys[k]]).append(row[k])

    # Delete occasional doublons from the output dictionary
    doublons = list()
    for k in plotDict.keys():
        if '_doublon' in k:
            doublons.append(k)

    for k in doublons:
        del plotDict[k]