# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 13:57:16 2016

Plots the OpenETran curves

@author: Matthieu Bertin
"""

import matplotlib.pyplot as plt

def draw(outputDict):
    # Time scale used as x-axis in the following figures
    time = outputDict['Time']
    arr = list()
    gd = list()

    for k in outputDict.keys():
        # Arrester current in figure 1
        if 'IARR' in k:
            plt.figure(1)
            plt.xlabel('Time (s)')
            plt.ylabel('Current (A)')
            plt.title('Arrester Currents')

            plt.plot(time, outputDict[k])
            arr.append(k)

        # Ground current in figure 2
        elif 'IPG' in k:
            plt.figure(2)
            plt.xlabel('Time (s)')
            plt.ylabel('Current (A)')
            plt.title('Ground Currents')

            plt.plot(time, outputDict[k])
            gd.append(k)

    plt.figure(1)
    plt.legend(arr)

    plt.figure(2)
    plt.legend(gd)

    plt.show()