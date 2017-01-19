# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:04:54 2016

Interprets the .csv output file from OpenETran. Each plot data is written
into a dictionnary.

@author: Matthieu Bertin
"""

import csv

def read(openETran, fileName, plotDict):
    with open(fileName, 'r', newline = '') as csvFile:
        plots = csv.reader(csvFile, dialect = 'excel', delimiter = ',', quotechar = '|')
        keys = list()

        for row in plots:

            # First step is to create the keys from the 1st line of the .csv file
            if 'Time' == row[0]:
                for key in row:
                    plotDict[key] = list()
                    keys.append(key)

            # We can then fill each list in the dict.
            else:
                for j in range(len(keys)):
                    (plotDict[keys[j]]).append(row[j])