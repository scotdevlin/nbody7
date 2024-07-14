# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 11:31:15 2024

@author: ScotDevlin

"""

import struct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
pd.set_option('display.max_columns', None)

file_path = rf'C:\Users\ScotDevlin\Documents\anaconda_nbody7\Unions1_nbody7\{input_df.loc[input_df["run"] == file, "filename"].values[0]}'
time_steps = int(input_df.loc[input_df["run"] == file, "steps"].values[0])            # (time / time step length) + 1  (check as 0.1 have 200 time step until 10200Myr)
zmbar =      float(input_df.loc[input_df["run"] == file, "z_mbar"].values[0])      # last number 3rd line of .PAR file
ns =         int(input_df.loc[input_df["run"] == file, "n_s"].values[0])            #  No. of stars

# start_index = time_steps-2  #  Choose how many 2D cluster plots (plots of star positions) you want to see

up_mass = 0.792102                  # from abs mag in i band of 8.5 (23.5 in app mag)
lo_mass = 0.305027                 # from abs mag in i band of 2.5 (17.5 in app mag)

G = 0.00430091727
V0 = 200

nout=0
#data_list is a list of data frames 
data_list = []
header_data_list = []

#rb stands for read binary    reccomended to use with -  with open(file_path, 'rb') as dat:
dat = open(file_path, 'rb')

#SET this number to the Number of iterations (time steps)
while nout < time_steps:
    
    #prints nout which is the TIME STEP
    print (nout)
    
    dat.read(4)
    buf = struct.unpack('III', dat.read(4 * 3))
    dat.read(4)
    dat.read(4)
    print(f"ntot: {buf[0]}, 30: {buf[1]}, n: {buf[2]}")
    ntot = buf[0]
    
    header_data = np.fromfile(dat, dtype=np.float64, count=30)
    mass = np.fromfile(dat, dtype=np.float64, count=ntot)
    pos = np.fromfile(dat, dtype=np.float64, count=3 * ntot).reshape((ntot, 3))
    vel = np.fromfile(dat, dtype=np.float64, count=3 * ntot).reshape((ntot, 3))
    pot = np.fromfile(dat, dtype=np.float64, count=ntot)
    nam = np.fromfile(dat, dtype=np.uint32, count=ntot)
    # prints the first 4 names of stars, the first print out should be 1,2,3,4 and then subsequent time steps may have different stars there - they get put at the start if they have gone into KS regularisation 
    print(nam[0], nam[1], nam[2], nam[3], nam[4], nam[5], nam[6], nam[7])
    typ = np.fromfile(dat, dtype=np.uint32, count=ntot)
    lum = np.fromfile(dat, dtype=np.float32, count=ntot)
    rad = np.fromfile(dat, dtype=np.float32, count=ntot)
    
    dat.read(4)
    
    print('read pos', dat.tell())

    nout=nout+1
    
    rbar = -3.671642

    data = {
        'Mass': mass,
        'Position_X': pos[:, 0] * rbar,
        'Position_Y': pos[:, 1] * rbar,
        'Position_Z': pos[:, 2] * rbar,
        # X, Y and Z_GC is the position of the stars when the galaxy is centred at 0,0 (does this by tkaing away the galaxy position, storred x,y,z in header_data[20], 21, 22)
        'Position_X_GC': (pos[:, 0] - header_data[20]) *rbar, 
        'Position_Y_GC': (pos[:, 1] - header_data[21]) * rbar,
        'Position_Z_GC': (pos[:, 2] - header_data[22]) * rbar,
        'Velocity_X': vel[:, 0],
        'Velocity_Y': vel[:, 1],
        'Velocity_Z': vel[:, 2],
        'Potential_Energy': pot,
        'Name': nam,
        'Stellar_Type': typ,
        'Luminosity': lum,
        'Radius': rad
    }

    # Calculate log Luminosity and add it to the DataFrame
    data['Log_Luminosity'] = np.log10(data['Luminosity'])

    # Calculate log temperature and add it to the DataFrame
    data['Log_Temperature'] = 3.762 + 0.25 * data['Log_Luminosity'] - 0.5 * np.log10(data['Radius'])

    df = pd.DataFrame(data)

    # Filter out rows where Stellar_Type is 13 or 14  (Neutron stars and Black holes) - therefore you dont see lots of ejecta
    #df = df[(df['Stellar_Type'] != 13) & (df['Stellar_Type'] != 14)]

     # Ensure df contains only the first xxxx rows (read in from buf2 = the number of stars), if there are more rows because of the centre of mass particles cut them OFF!   (buf[0] is the number of stars+number of center of mass particles.))
     # Check if this step has worked by runni the chekc for duplicate star names cell below
    if len(df) > buf[2]:
        df = df.iloc[:buf[2]]

    data_list.append(df)
    
    # Store header_data separately for each iteration
    header_data_list.append(pd.DataFrame(header_data.reshape(1, -1), columns=[f'Header_{i + 1}' for i in range(30)]))

#     # EXCEL BELOW  -  Access each DataFrame in data_list for further analysis if needed
# excel_file_path = 'output_data.xlsx'
# with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
#     for i, df in enumerate(data_list):
#         df.to_excel(writer, sheet_name=f'iteration_{i + 1}', index=False)
# #  Add a new sheet with concatenated header data
#     pd.concat(header_data_list).to_excel(writer, sheet_name='header_data', index=False)
