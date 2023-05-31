"""                                                                                                           
Python frontend for controlling UVic light pulser card
                                                                                                              
"""

import midas
import midas.frontend
import midas.event
import collections
import ctypes
import os
import subprocess
from time import time
import shlex

import serial
import time

ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)  # open serial port
print(ser.name)         # check which port was really used



cmd="Q\n"
ser.write(cmd.encode())
#ser.write(b'Q\n')     # write a string

line = ser.readline() 
if line != b'\n' and line != b'\r\n' : 
    print(line)
line = ser.readline() 
if line != b'\n' and line != b'\r\n' : 
    print(line)

print("Finished read")



cmd="Q\n"
ser.write(cmd.encode())
#ser.write(b'Q\n')     # write a string

line = ser.readline() 
if line != b'\n' and line != b'\r\n' : 
    print(line)
line = ser.readline() 
if line != b'\n' and line != b'\r\n' : 
    print(line)

print("Finished second read")

# Turn board on

cmd="E\n"
ser.write(cmd.encode())


line = ser.readline()
if line != b'\n' and line != b'\r\n' : 
    print(line)
line = ser.readline()
if line != b'\n' and line != b'\r\n' : 
    print(line)
line = ser.readline()

# Set to external trigger

cmd="TE\n"
ser.write(cmd.encode())
#ser.write(b'Q\n')     # write a string                                                                       

line = ser.readline()
if line != b'\n' and line != b'\r\n' : 
    print(line)
line = ser.readline()
if line != b'\n' and line != b'\r\n' : 
    print(line)


print("External trigger")


# Set DAC to 650

print("Set command; wait 5 seconds");
cmd="S0650"
ser.write(cmd.encode())
#ser.write(b'Q\n')     # write a string                                                             
time.sleep(5)

line = ser.readline()
if line != b'\n' and line != b'\r\n' : 
    print(line)
line = ser.readline()
if line != b'\n' and line != b'\r\n' : 
    print(line)


time.sleep(1)

print("Set bias")

for i in range(5):
    cmd="Q"
    ser.write(cmd.encode())

    line = ser.readline()
    if line != b'\n' and line != b'\r\n' : 
        print(line)
    line = ser.readline()
    if line != b'\n' and line != b'\r\n' : 
        print(line)

    print("Finished read")


ser.close()             # close port

