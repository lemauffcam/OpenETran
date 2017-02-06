# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 13:57:16 2016

Plots the OpenETran curves

@author: Matthieu Bertin
"""

import matplotlib.pyplot as plt

def draw(outputDict):

    # Close all figures that could have been opened by another simulation instance
    plt.close('all')

    # Time scale used as x-axis in the figures
    time = outputDict['Time']

    arr = list()
    gd = list()
    volt = list()
    pipe = list()
    tX2 = list()
    house = list()

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

        # Pipegap current
        elif 'IPIPE' in k:
            plt.figure(3)
            plt.xlabel('Time (s)')
            plt.ylabel('Current (A)')
            plt.title('Pipegap Current')

            plt.plot(time, outputDict[k])
            pipe.append(k)

        # Transformer X2 terminal current
        elif 'IX2' in k:
            plt.figure(4)
            plt.xlabel('Time (s)')
            plt.ylabel('Current (A)')
            plt.title('Transformer X2 terminal current')

            plt.plot(time, outputDict[k])
            tX2.append(k)

        # House ground current
        elif 'IHG' in k:
            plt.figure(5)
            plt.xlabel('Time (s)')
            plt.ylabel('Current (A)')
            plt.title('House ground current')

            plt.plot(time, outputDict[k])
            house.append(k)

        elif 'Time' in k:
            continue

        # Pole voltages
        else:
            plt.figure(6)
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.title('Pole voltages')

            plt.plot(time, outputDict[k])
            volt.append(k)


    # Graphs legends
    if len(arr) > 0:
        plt.figure(1)
        plt.legend(arr)

    if len(gd) > 0:
        plt.figure(2)
        plt.legend(gd)

    if len(pipe) > 0:
        plt.figure(3)
        plt.legend(pipe)

    if len(tX2) > 0:
        plt.figure(4)
        plt.legend(tX2)

    if len(house) > 0:
        plt.figure(5)
        plt.legend(house)

    if len(volt) > 0:
        plt.figure(6)
        plt.legend(volt)

    plt.show()