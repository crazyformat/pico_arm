#
# USB serial communication for the Raspberry Pi Pico (RD2040) using the second RD2040
# thread/processor (written by Dorian Wiskow - Janaury 2021)
#
from sys import stdin, exit
from utime import sleep
#
# global variables to share between both threads/processors
#
bufferSize = 1024                 # size of circular buffer to allocate
# circuolar incomming USB serial data buffer (pre fill)
buffer = [' '] * bufferSize
# USB serial port echo incooming characters (True/False)
bufferEcho = False
# pointers to next in/out character in circualr buffer
bufferNextIn, bufferNextOut = 0, 0
# tell 'bufferSTDIN' function to terminate (True/False)
terminateThread = False
#
# bufferSTDIN() function to execute in parallel on second Pico RD2040 thread/processor
#


def bufferSTDIN():
    global buffer, bufferSize, bufferEcho, bufferNextIn, terminateThread

    while True:                                 # endless loop
        if terminateThread:                     # if requested by main thread ...
            break  # ... exit loop
        # wait for/store next byte from USB serial
        buffer[bufferNextIn] = stdin.read(1)
        if bufferEcho:                          # if echo is True ...
            # ... output byte to USB serial
            print(buffer[bufferNextIn], end='')
        bufferNextIn += 1                       # bump pointer
        if bufferNextIn == bufferSize:          # ... and wrap, if necessary
            bufferNextIn = 0
#
# instantiate second 'background' thread on RD2040 dual processor to monitor and buffer
# incomming data from 'stdin' over USB serial port using ‘bufferSTDIN‘ function (above)
#

#
# function to check if a byte is available in the buffer and if so, return it
#


def getByteBuffer():
    global buffer, bufferSize, bufferNextOut, bufferNextIn

    # if no unclaimed byte in buffer ...
    if bufferNextOut == bufferNextIn:
        return ''  # ... return a null string
    n = bufferNextOut                           # save current pointer
    bufferNextOut += 1                          # bump pointer
    if bufferNextOut == bufferSize:  # ... wrap, if necessary
        bufferNextOut = 0
    return (buffer[n])                          # return byte from buffer

#
# function to check if a line is available in the buffer and if so return it
# otherwise return a null string
#
# NOTE 1: a line is one or more bytes with the last byte being LF (\x0a)
#      2: a line containing only a single LF byte will also return a null string
#


def getLineBuffer():
    global buffer, bufferSize, bufferNextOut, bufferNextIn

    # if no unclaimed byte in buffer ...
    if bufferNextOut == bufferNextIn:
        return ''  # ... RETURN a null string

    n = bufferNextOut                           # search for a LF in unclaimed bytes
    while n != bufferNextIn:
        if buffer[n] == '\x0a':                 # if a LF found ...
            break  # ... exit loop ('n' pointing to LF)
        n += 1                                  # bump pointer
        if n == bufferSize:  # ... wrap, if necessary
            n = 0
    if (n == bufferNextIn):                     # if no LF found ...
        return ''  # ... RETURN a null string

    # LF found in unclaimed bytes at pointer 'n'
    line = ''
    n += 1                                      # bump pointer past LF
    if n == bufferSize:  # ... wrap, if necessary
        n = 0

    while bufferNextOut != n:                   # BUILD line to RETURN until LF pointer 'n' hit

        if buffer[bufferNextOut] == '\x0d':     # if byte is CR
            bufferNextOut += 1  # bump pointer
            if bufferNextOut == bufferSize:  # ... wrap, if necessary
                bufferNextOut = 0
            continue  # ignore (strip) any CR (\x0d) bytes

        if buffer[bufferNextOut] == '\x0a':     # if current byte is LF ...
            bufferNextOut += 1  # bump pointer
            if bufferNextOut == bufferSize:  # ... wrap, if necessary
                bufferNextOut = 0
            break  # and exit loop, ignoring (i.e. strip) LF byte
        line = line + buffer[bufferNextOut]     # add byte to line
        bufferNextOut += 1                      # bump pointer
        if bufferNextOut == bufferSize:  # wrap, if necessary
            bufferNextOut = 0
    return line                                 # RETURN unclaimed line of input
