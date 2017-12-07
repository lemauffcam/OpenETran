# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 14:50:36 2016

Writes the openetran input file from the main structure

@author: Matthieu Bertin
"""
# General function to write the lists for each key in the input file
# The field at each key is expected to be a list of lists
def writeKey(f, openetran, key):
    err = 0

    for v in openetran[key]:
        # We first check if evey field has been written in (counterpoise fields
        # in "ground" are optionnal so it's a special case for that key)
        if key == 'ground':
            for i in range(5):
                if v[i] == '':
                    err = 1
                    break

            # Last 2 fields are Pairs and Poles, which are mandatory
            i = len(v)
            if v[i-1] == '' or v[i-2] == '':
                err = 1
                break

        # In 'conductor', the last 3 fields are also optional
        elif key == 'conductor':
            for i in range(5):
                if v[i] == '':
                    err = 1
                    break

        else:
            for i in range(len(v)):
                if v[i] == '':
                    err = 1
                    break

        # If there's an error (missing text field), we go to the next list
        if err == 1:
            # print('Error, missing field in ' + k)
            continue

        # We start by writing which field it is (same name as the key in the dict)
        f.write(key + ' ')

        # Write separate values, except for the last two.
        for i in range(len(v) - 2):
            f.write(v[i] + ' ')

        f.write('\n')

        # The last 2 strings are for pairs and poles
        i = len(v) - 2
        f.write('pairs ' + v[i] + '\n')
        f.write('poles ' + v[i+1] + '\n')

        f.write('\n')

def write(openetran):
    k = len(openetran['name'])
    inputFileName = openetran['name'][0:k-5] + '.dat'

    with open(inputFileName, 'w') as f:

        # We write the mandatory simulation parameters and conductor data first
        k = 0
        for v in openetran['simulation']:
            if k == 7: # If we're still in the loop at that value, then it's a critical current
                       # simulation. The last 3 parameters aren't in the .dat file.
                break
            else:
                f.write(v + ' ')
                k += 1

        f.write('\n')

        for cond in openetran['conductor']:
            f.write('conductor ')
            for v in cond:
                f.write(v + ' ')

            f.write('\n')

        f.write('\n')

        for k, v in openetran.items():
            if k == 'simulation' or k == 'conductor' or k == 'name':
                continue

            # Simplified version of the writeKey() fonction
            elif k == 'surge' or k == 'steepfront':
                v = openetran[k]
                err = 0

                for i in range(len(v)):
                    if v[i] == '':
                        err = 1
                        break

                if err == 1:
                    # print('Error, missing field in ' + k)
                    continue

                # We start by writing which field it is (same name as the key in the dict)
                f.write(k + ' ')

                for i in range(len(v) - 2):
                    f.write(v[i] + ' ')

                f.write('\n')

                # The last 2 strings are for pairs and poles
                i = len(v) - 2
                f.write('pairs ' + v[i] + '\n')
                f.write('poles ' + v[i+1] + '\n')

                f.write('\n')

            elif k == 'label':
                err = 0

                for v in openetran['label']:
                    # We first check if evey field has been written in.
                    for i in range(len(v)):
                        if v[i] == '':
                            err = 1
                            break

                    # If there's an error (missing text field), we go to the next list
                    if err == 1:
                        # print('Error, missing field in ' + k)
                        continue

                    if v[0] == 'Phase':
                        f.write('labelphase ')
                    else:
                        f.write('labelpole ')

                    f.write(v[1] + ' ' + v[2] + '\n')

                f.write('\n')

            else:
                writeKey(f, openetran, k)