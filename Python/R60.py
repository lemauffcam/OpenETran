# -*- coding: utf-8 -*-
"""
Created on Thu Feb 2 2017
Calculates the 60Hz resistance of the counterpoise
@author: Matthieu
"""

import math

def calcR60(openetran, grid):
    rowCount = grid.rowCount() - 1
    k = len(openetran['ground']) - 1

    while rowCount > 2:
        label = grid.itemAtPosition(rowCount, 1).widget()

        # Read counterpoise parameters (first as strings)
        rho_str = openetran['ground'][k][1]
        a_str = openetran['ground'][k][5]
        h_str = openetran['ground'][k][6]
        ltot_str = openetran['ground'][k][7]
        nSeg_str = openetran['ground'][k][8]
        eps_str = openetran['ground'][k][9]

        rho = float(rho_str)
        a = float(a_str)
        h = float(h_str)
        ltot = float(ltot_str)
        nSeg = int(nSeg_str)
        eps = float(eps_str)

        # Length of 1 segment
        if nSeg > 0 and a > 0 and h > 0 and ltot > 0:
            li = ltot / nSeg
        else:
            print('Parameter error. All fields of the counterpoise must be positive floats')
            return

        # Resistance as used in the counterpoise model (see documentation)
        ri = rho/(2*math.pi*li) * ( (2*h+a)/li + math.log((li + math.sqrt(li*li + a*a))/a) -
          math.sqrt(1 + math.pow(a/li, 2)) + math.log((li + math.sqrt(li*li + 4*h*h)) / (2*h)) -
          math.sqrt(1 + math.pow(2 * h / li, 2)) );

        # Capacitance and conductance (only conductance is used, but Ci is needed to calculate it)
        if 2*h-a > a:
            Ci = shuntCapa(li, eps, a) + shuntCapa(li, eps, 2*h - a)
        else:
            Ci = 2*shuntCapa(li, eps, a)

        Gi = Ci / (eps * 8.8419412828E-12 * rho)

        # K coefficient (see documentation)
        K = ri/Gi

        # DFFz and DFF triangles coefficients (see documentation)
        b = bCoeff(nSeg)
        c = cCoeff(nSeg)

        # Input impedance
        sumB = 0
        sumC = 0

        for j in range(nSeg+1):
            sumB += b[nSeg][j]*math.pow(K, j)
            sumC += c[nSeg][j]*math.pow(K, j)

        Z = Gi*sumB/sumC
        label.setText(str(Z))


        rowCount = rowCount-6
        k -= 1

    return

# Shunt capacitance of the counterpoise in an infinite medium
def shuntCapa(li, eps, a):
	perm = eps * 8.8419412828E-12 # Soil permittivity

	C = 2 * math.pi * perm * li / ( a/li + math.log( (li + math.sqrt(li*li + a*a)) / a )
		- math.sqrt(1 + math.pow(a / li, 2)) )

	return C

# Returns the array of DFF triangle coefficients (see documentation)
def bCoeff(nSeg):
    b = [[0 for x in range(nSeg+1)] for y in range(nSeg+1)]

    for i in range(nSeg+1):
        for j in range(nSeg+1):
            if j > i:
                b[i][j] = 0

            elif j == 0 or (j == i and i == 1):
                b[i][j] = 1

            else:
                b[i][j] = 2*b[i-1][j] + b[i-1][j-1] - b[i-2][j]


    return b

# Returns the array of DFFz triangle coefficients (see documentation)
def cCoeff(nSeg):
    c = [[0 for x in range(nSeg+1)] for y in range(nSeg+1)]

    for i in range(nSeg+1):
        for j in range(nSeg+1):
            if j >= i:
                c[i][j] = 0

            elif j == 0:
                c[i][j] = i

            else:
                c[i][j] = 2*c[i-1][j] + c[i-1][j-1] - c[i-2][j]

    return c