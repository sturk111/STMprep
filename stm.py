import socket
import struct
from time import sleep
import pandas as pd
import numpy as np

def connect(timeout=10):
    port = 6501
    ip = '192.168.236.1'

    stmx = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    stmx.connect((ip,port))
    stmx.settimeout(timeout)
    return stmx

#Scan.FrameGet returns the scan frame parameters
def scanFrameGet():
    stmx = connect()
    msg = bytes.fromhex('5363 616e 2e46 7261 6d65 4765 7400 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0000\
        0001 0000')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    xc = struct.unpack('!f',reply[40:44])[0]
    yc = struct.unpack('!f',reply[44:48])[0]
    width = struct.unpack('!f',reply[48:52])[0]
    height = struct.unpack('!f',reply[52:56])[0]
    angle = struct.unpack('!f',reply[56:60])[0]
    return [xc, yc, width, height, angle]



#Run this function to start taking the grid spectroscopy map that is set up in the software 
#Note that the base name may need to be changed
def map():
    stmx = connect()
    exptName = '4269 6173 2053 7065 6374 726f 7363 6f70 7920 4249 4e41 5259'
    baseName = '5454 4730 3031 5f6d 6170'
    #Pattern.PropsSet
    msg = bytes.fromhex('5061 7474 6572 6e2e 5072 6f70 7353 6574 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0036 \
        0000 0000 \
        0000 0018' + \
        exptName + \
        '0000 000A' + \
        baseName + \
        '0000 0000 \
        0000 0000 \
        0000 0001')
    stmx.sendall(msg)
    sleep(1)

    #Pattern.ExpOpen
    msg1 = bytes.fromhex('5061 7474 6572 6e2e 4578 704f 7065 6e00 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0000 0000')
    #Pattern.ExpStart
    msg2 = bytes.fromhex('5061 7474 6572 6e2e 4578 7053 7461 7274 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0002 \
        0000 0000 \
        0001')

    stmx.sendall(msg1)
    sleep(1)
    stmx.sendall(msg2)
    stmx.close()

def line():
    stmx = connect()
    exptName = '4269 6173 2053 7065 6374 726f 7363 6f70 7920 4249 4e41 5259'
    baseName = '5454 4730 3031 5f6c 696e'
    #Pattern.PropsSet
    msg = bytes.fromhex('5061 7474 6572 6e2e 5072 6f70 7353 6574 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0036 \
        0000 0000 \
        0000 0018' + \
        exptName + \
        '0000 000A' + \
        baseName + \
        '0000 0000 \
        0000 0000 \
        0000 0001')
    stmx.sendall(msg)
    sleep(1)

    #Pattern.ExpOpen
    msg1 = bytes.fromhex('5061 7474 6572 6e2e 4578 704f 7065 6e00 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0000 0000')
    #Pattern.ExpStart
    msg2 = bytes.fromhex('5061 7474 6572 6e2e 4578 7053 7461 7274 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0002 \
        0000 0000 \
        0002')

    stmx.sendall(msg1)
    sleep(1)
    stmx.sendall(msg2)
    stmx.close()

#Pattern.ExpStatusGet
#returns 1 if exp is running, 0 if not
def mapStat():
    stmx = connect()
    msg = bytes.fromhex('5061 7474 6572 6e2e 4578 7053 7461 7475 7347 6574 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0001 0000')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    return struct.unpack('!I',reply[40:44])[0]

#Scan.StatusGet
#returns 1 if exp is running, 0 if not
def scanStat():
    stmx = connect()
    msg = bytes.fromhex('5363 616e 2e53 7461 7475 7347 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0001 0000')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    return struct.unpack('!I',reply[40:44])[0]


#sets user output number index to value (V, phys. units)
def userOut(index, value):
    stmx = connect()
    valueHex = hex(struct.unpack('!I', struct.pack('!f', value))[0])[2:]
    valueHex = (8-len(valueHex))*'0' + valueHex
    msg = bytes.fromhex('5573 6572 4f75 742e 5661 6c53 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0000 0000 \
        0000 000' + str(index) \
        + valueHex)
    stmx.sendall(msg)
    stmx.close()

#units are V, sec
def ramp(userIndex,RTIndex,end,rate,step):
    start = readSignal(RTIndex)
    sleep(step/rate+1)
    numSteps = int(abs(end-start)/step)
    V = np.linspace(start,end,numSteps)
    for v in V:
        userOut(userIndex,v)
        sleep(step/rate)

def rampBias(start,end,rate,step):
    #start = readSignal(24)
    #sleep(step/rate+1)
    numSteps = int(abs(end-start)/step)
    V = np.linspace(start,end,numSteps)
    for v in V:
        biasSet(v)
        sleep(step/rate)


def sputter(time_on_in_minutes):
    t = 60*time_on_in_minutes
    print('Sputter Routine')
    c=1
    while True:
        print(c)
        userOut(2,10)
        print('Sputter On')
        sleep(t)
        userOut(2,0)
        print('Sputter Off')
        sleep(t)
        c+=1

#turns feedback on
def feedbackOn():
    stmx = connect()
    msg = bytes.fromhex('5a43 7472 6c2e 4f6e 4f66 6653 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0004 0000 0000 0000 0001')
    stmx.sendall(msg)
    stmx.close()

def feedbackOff():
    stmx = connect()
    msg = bytes.fromhex('5a43 7472 6c2e 4f6e 4f66 6653 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0004 \
        0000 0000 \
        0000 0000')
    stmx.sendall(msg)
    stmx.close()

#withdras the tip
def withdraw():
    stmx = connect()
    msg = bytes.fromhex('5a43 7472 6c2e 5769 7468 6472 6177 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0008 0000 0000 0000 0001 ffff ffff')
    stmx.sendall(msg)
    stmx.close()

#turns lockin oscillation on
def oscOn():
    stmx = connect()
    msg = bytes.fromhex('4c6f 636b 496e 2e4d 6f64 4f6e 4f66 6653 6574 0000 0000 0000 0000 0000 0000 0000 0000 0008 0000 0000 0000 0001 0000 0001')
    stmx.sendall(msg)
    stmx.close()

#turns lockin oscillation off
def oscOff():
    stmx = connect()
    msg = bytes.fromhex('4c6f 636b 496e 2e4d 6f64 4f6e 4f66 6653 6574 0000 0000 0000 0000 0000 0000 0000 0000 0008 0000 0000 0000 0001 0000 0000')
    stmx.sendall(msg)
    stmx.close()

#returns lockin X value using Signals.ValGet
def LIX():
    stmx = connect()
    msg = bytes.fromhex('5369 676e 616c 732e 5661 6c47 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0008 0001 0000 0000 0056 0000 0001')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    return struct.unpack('!f',reply[40:44])[0]

#returns lockin Y value
def LIY():
    stmx = connect()
    msg = bytes.fromhex('5369 676e 616c 732e 5661 6c47 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0001 0000 \
        0000 0057 0000 0001')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    return struct.unpack('!f',reply[40:44])[0]

#returns the current (nanonis analog input 1)
def current():
    stmx=connect()
    msg = bytes.fromhex('5369 676e 616c 732e 5661 6c47 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0001 0000 \
        0000 0000 0000 0001')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    return struct.unpack('!f',reply[40:44])[0]

#Return value of signal (output 8 is index 31)
def readSignal(index):
    indexHex = hex(struct.unpack('!I', struct.pack('!I', index))[0])[2:]
    indexHex = (8-len(indexHex))*'0' + indexHex
    stmx=connect()
    msg = bytes.fromhex('5369 676e 616c 732e 5661 6c47 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0001 0000' \
        + indexHex + '0000 0001')
    stmx.sendall(msg)
    sleep(1)
    reply = stmx.recv(256)
    stmx.close()
    return struct.unpack('!f',reply[40:44])[0]

#ZCtrl.ZPosGet returns the z position of the tip
def zPos():
    stmx = connect()
    msg = bytes.fromhex('5a43 7472 6c2e 5a50 6f73 4765 7400 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0001 0000')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    zPos = struct.unpack('!f',reply[40:44])[0]
    stmx.close()
    return zPos

#ZCtrl.ZPosSet sets z position to z (in meters) 
#feedback must be turned off before running this command
def zPosSet(z):
    stmx = connect()
    zHex = hex(struct.unpack('!I', struct.pack('!f', z))[0])[2:]
    zHex = (8-len(zHex))*'0' + zHex
    msg = bytes.fromhex('5a43 7472 6c2e 5a50 6f73 5365 7400 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0004\
        0000 0000'
        + zHex)
    stmx.sendall(msg)
    stmx.close()

def zLimits():
    stmx = connect()
    msg = bytes.fromhex('5a43 7472 6c2e 4c69 6d69 7473 4765 7400 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0001 0000')
    stmx.sendall(msg)
    reply = stmx.recv(256)
    stmx.close()
    return [struct.unpack('!f',reply[40:44])[0],struct.unpack('!f',reply[44:48])[0]]

#this function checks to see if feedback is on
#if yes, retract; if no, engage
def engage_retract():
    stmx = connect()
    query = bytes.fromhex('5a43 7472 6c2e 4f6e 4f66 6647 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0001 0000')
    stmx.sendall(query)
    reply = stmx.recv(256)
    status = struct.unpack('!I',reply[40:44])[0] #controller status; 1=on, 0=off
    if status:
        withdraw()
    else:
        feedback_on()
    stmx.close()

#moves steps steps in direction dir
#dir: Valid values are 0=X+, 1=X-, 2=Y+, 3=Y-, 4=Z+, 5=Z-
def move(dir,steps):
    stmx = connect()
    stepsHex = hex(steps)[2:]
    N = (4-len(stepsHex))*'0' + stepsHex
    msg = bytes.fromhex('4d6f 746f 722e 5374 6172 744d 6f76 6500 0000 0000 0000 0000 0000 0000 0000 0000 0000 000e 0000 0000 0000 000' + str(dir) + '' + N + ' 0000 0000 0000 0000')
    stmx.sendall(msg)
    stmx.close()
    print('direction: {}, steps: {}'.format(dir,steps))

#toggles auto approach on(x=1)/off(x=0)
#choice of fast or safe approach must be set manually in nanonis
def autoApproach(x):
    stmx = connect()
    msg = bytes.fromhex('4175 746f 4170 7072 6f61 6368 2e4f 6e4f 6666 5365 7400 0000 0000 0000 0000 0000 \
     0000 0002 \
     0000 0000 \
     000' + str(x))
    stmx.sendall(msg)
    stmx.close()

#checks to see if autoapproach is on (returns 1) or off (returns 0)
def autoApproachStatus():
    stmx = connect()
    query = bytes.fromhex('4175 746f 4170 7072 6f61 6368 2e4f 6e4f 6666 4765 7400 0000 0000 0000 0000 0000 \
        0000 0000\
        0001 0000')
    stmx.sendall(query)
    reply = stmx.recv(256)
    stmx.close()
    return int(str(reply)[104])

#set the z controller gain
#units are Proportional (m/A), Time Const. (s)
def gainSet(P,T):
    I = P/T
    stmx=connect()
    pHex = hex(struct.unpack('!I', struct.pack('!f', P))[0])[2:]
    tHex = hex(struct.unpack('!I', struct.pack('!f', T))[0])[2:]
    iHex = hex(struct.unpack('!I', struct.pack('!f', I))[0])[2:]
    msg = bytes.fromhex('5a43 7472 6c2e 4761 696e 5365 7400 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 000c \
        0000 0000' \
        + pHex + tHex + iHex)
    stmx.sendall(msg)
    stmx.close()

#set the tunneling set point current I (Amps)
def setSet(I):
    stmx = connect()
    iHex = hex(struct.unpack('!I', struct.pack('!f', I))[0])[2:]
    msg = bytes.fromhex('5a43 7472 6c2e 5365 7470 6e74 5365 7400 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0004 \
        0000 0000' \
        + iHex)
    stmx.sendall(msg)
    stmx.close()

#set the bias voltage V (Volts)
def biasSet(V):
    stmx = connect()
    vHex = hex(struct.unpack('!I', struct.pack('!f', V))[0])[2:]
    msg = bytes.fromhex('4269 6173 2e53 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0004 \
        0000 0000' \
        + vHex)
    stmx.sendall(msg)
    stmx.close()


#sets coarse motor frequency (Hz) and amplitude (V)
def coarseSet(freq, amp):
    stmx = connect()
    freqHex = hex(struct.unpack('<I', struct.pack('<f', freq))[0])[2:]
    ampHex = hex(struct.unpack('<I', struct.pack('<f', amp))[0])[2:]
    msg = bytes.fromhex('4d6f 746f 722e 4672 6571 416d 7053 6574 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 000a \
        0000 0000' \
        + freqHex + \
        ampHex + \
        '0000')
    stmx.sendall(msg)
    stmx.close()

#BiasSpectr.PropsGet
def specProps():
    stmx = connect()
    query = bytes.fromhex('4269 6173 5370 6563 7472 2e50 726f 7073 4765 7400 0000 0000 0000 0000 0000 0000\
        0000 0000 \
        0001 0000')
    stmx.sendall(query)
    header = stmx.recv(40)
    tmp = stmx.recv(2)
    numSweeps = struct.unpack('!i',stmx.recv(4))[0]
    tmp = stmx.recv(2)
    numPoints = struct.unpack('!i',stmx.recv(4))[0]

    return numSweeps,numPoints

#BiasSpectr.TimingGet
#returns list:
#[z avg time, z offset, init. settling time, max. slew rate, settling time, ...
#integration time, end settling time, z ctrl time]
def specTiming():
    stmx = connect()
    query = bytes.fromhex('4269 6173 5370 6563 7472 2e54 696d 696e 6747 6574 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0001 0000')
    stmx.sendall(query)
    header = stmx.recv(40)
    T = []
    for i in range(8):
        T.append(struct.unpack('!f',stmx.recv(4))[0])
    return T

#BiasSpectr.LimitsGet
def specLimits():
    stmx = connect()
    query = bytes.fromhex('4269 6173 5370 6563 7472 2e4c 696d 6974 7347 6574 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0001 0000')
    stmx.sendall(query)
    header = stmx.recv(40)
    start = struct.unpack('!f',stmx.recv(4))[0]
    end = struct.unpack('!f',stmx.recv(4))[0]

    return abs(end - start)

def sweeps():
    vRange = specLimits()
    sleep(0.1)
    T = specTiming()
    sleep(0.1)
    numSweeps,N = specProps()
    sweepT = T[0] + T[2] + T[6] + T[7] + N*(T[4] + T[5]) + 2*vRange/T[3]

    return numSweeps, sweepT

#BiasSpectr.Start takes a spectrum, using parameters set in nanonis, and returns data as numpy array
#be sure to set excitation amplitude first
def spec():
    stmx = connect()
    query = bytes.fromhex('4269 6173 5370 6563 7472 2e53 7461 7274 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0001 0000 \
        0000 0001 \
        0000 0000')
    stmx.sendall(query)
    
    header = stmx.recv(40)
    ChNamesSz = struct.unpack('!i',stmx.recv(4))[0]
    Nch = struct.unpack('!i',stmx.recv(4))[0]

    channels = []
    for i in range(Nch):
        l = struct.unpack('!i',stmx.recv(4))[0]
        channels.append(stmx.recv(l).decode('ascii'))

    Nrows = struct.unpack('!i',stmx.recv(4))[0] #channels
    Ncols = struct.unpack('!i',stmx.recv(4))[0] #biasV

    spectra = np.zeros((Nrows,Ncols))
    for i in range(Nrows):
        for j in range(Ncols):
            spectra[i,j] = struct.unpack('!f',stmx.recv(4))[0]

    Nparams = struct.unpack('!i',stmx.recv(4))[0]

    parameters=[]
    for i in range(Nparams):
        parameters.append(struct.unpack('!f',stmx.recv(4))[0])
    
    stmx.close()

    return channels, spectra, parameters

def poke():
    stmx = connect()
    msg = bytes.fromhex('5a53 7065 6374 722e 5374 6172 7400 0000 0000 0000 0000 0000 0000 0000 0000 0000\
        0000 0008 \
        0000 0000 \
        0000 0000 \
        0000 0000')
    stmx.sendall(msg)
    stmx.close()

#moves tip to x,y (position interact nm relative to 0,0)
def followMe(x,y):
    stmx = connect()
    X = hex(struct.unpack('>Q', struct.pack('>d', x*1e-9))[0])[2:]
    Y = hex(struct.unpack('>Q', struct.pack('>d', y*1e-9))[0])[2:]

    Xstr = (16-len(X))*'0' + X
    Ystr = (16-len(Y))*'0' + Y

    msg = bytes.fromhex('466f 6c4d 652e 5859 506f 7353 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
       0000 0014 \
       0001 0000' \
       + Xstr + \
       Ystr + \
       '0000 0001 ')
    stmx.sendall(msg)
    header = stmx.recv(40)
    stmx.close()
    #return header

#pulls up the oscilloscope 2T window (required in order to interact programatically with it)
def osciRun():
    stmx = connect()
    msg = bytes.fromhex('4f73 6369 3254 2e52 756e 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0000 \
        0000 0000')
    stmx.sendall(msg)
    stmx.close()

#returns present oscilloscope 2T window as array. data[0,:] is channel A
#must run clearScope before this else timeout error 
def scope():
    stmx = connect(timeout=0.5)
    #Osci2T.DataGet
    query = bytes.fromhex('4f73 6369 3254 2e44 6174 6147 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0002 \
        0001 0000 \
        0000')
    stmx.sendall(query)
    try:
        header = stmx.recv(40)
    except socket.timeout:
        stmx.close()
        return 0
    t0 = struct.unpack('!d',stmx.recv(8))[0]
    dt = struct.unpack('!d',stmx.recv(8))[0]
    ySz = struct.unpack('!i',stmx.recv(4))[0]

    data = np.zeros((2,ySz))
    for i in range(2):
        for j in range(ySz):
            data[i,j] = struct.unpack('!d',stmx.recv(8))[0]

    stmx.close()

    return data

#checks to see if tunneling at set current (A)
def tunneling(setCurrent):
    I = current()
    sleep(0.1)
    return abs(I - setCurrent)/setCurrent < 0.1

#checks for crash on current oscilloscope screen; returns true if crashed is detected, false if not
#crash is defined as current above 1.5 nA
def crash():
    data = scope()
    sleep(0.25)
    clearScope()
    crashed = max(data[0,:]) > 1.5e-9
    if crashed:
        print('Crash detected!')
    return crashed

#toggles the trigger on 2 channel oscilloscope
#x=0 is immediate, x=1 is level; trigger level is set to 500 pA
def trigSet(x):
    stmx = connect()
    msg = bytes.fromhex('4f73 6369 3254 2e54 7269 6753 6574 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 001e \
        0000 0000 \
        000' + str(x) + \
        '0000 \
        0001 \
        3e01 2e0b e826 d695 \
        0000 0000 0000 0000 \
        3fa999999999999a')
    stmx.sendall(msg)
    stmx.close()

#clears crash from current oscilloscope and turns triggering on at 500pA
#must use a time base of 128 ms 
#must run this before every attempt to read the scope or the connection will fail
def clearScope():
    trigSet(0)
    sleep(0.3)
    trigSet(1)

#performs a scan action
#action 0 start, 1 stop, 2 pause; direction 0 down, 1 up
def scan(action, direction):
    stmx = connect()
    msg = bytes.fromhex('5363 616e 2e41 6374 696f 6e00 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0006 \
        0000 0000 \
        000' + str(action) + \
        '0000 000' + str(direction))
    stmx.sendall(msg)
    stmx.close()

#returns z fwd values from current scan frame as numpy array (after truncating unfilled pixels and tilt correcting slow axis)
def grabScan():
    stmx = connect()
    query = bytes.fromhex('5363 616e 2e46 7261 6d65 4461 7461 4772 6162 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0001 0000 \
        0000 000e \
        0000 0001')
    stmx.sendall(query)

    header = stmx.recv(40)

    chNameSz = struct.unpack('!i',stmx.recv(4))[0]
    chName = stmx.recv(chNameSz).decode('ascii')
    Nrows = struct.unpack('!i',stmx.recv(4))[0]
    Ncols = struct.unpack('!i',stmx.recv(4))[0]

    scan = np.zeros((Nrows,Ncols))
    for i in range(Nrows):
        for j in range(Ncols):
            scan[i,j] = struct.unpack('!f',stmx.recv(4))[0]

    scanDir = struct.unpack('!I',stmx.recv(4))[0]

    stmx.close()
    scan = scan[~np.isnan(scan)]
    scan = scan[:int(np.floor(len(scan)/Nrows)*Nrows)].reshape(-1,Nrows)

    scanLineSub = np.zeros(np.shape(scan))
    x = np.arange(Nrows)
    for i in range(len(scan[:,0])):
        y = scan[i,:]
        m,b = np.polyfit(x,y,1)
        scanLineSub[i,:] = y - m*x - b

    return scanLineSub

#run this function while tunneling and it will return the surface roughness (in nm), extracted from the first t seconds of a scan
def roughness(t):
    scan(0,0)
    sleep(t)
    scan(1,0)
    sleep(0.25)
    data = grabScan()
    return 1e9*np.std(data.flatten())

#sets the excitation voltage to amp (V) on the internal lockin.
def oscAmp(amp):
    stmx = connect()
    ampHex = hex(struct.unpack('<I', struct.pack('<f', amp))[0])[2:]
    msg = bytes.fromhex('4c6f 636b 496e 2e4d 6f64 416d 7053 6574 0000 0000 0000 0000 0000 0000 0000 0000 \
        0000 0008 \
        0000 0000 \
        0000 0001' \
        + ampHex)
    stmx.sendall(msg)
    stmx.close()

#sets the oscillation frequency of the internal lockin
def oscFreq(freq):
    stmx = connect()
    freqHex = hex(struct.unpack('>Q', struct.pack('>d', freq))[0])[2:]
    msg = bytes.fromhex('4c6f 636b 496e 2e4d 6f64 5068 6173 4672 6571 5365 7400 0000 0000 0000 0000 0000 \
        0000 000c \
        0000 0000 \
        0000 0001' \
        + freqHex)
    stmx.sendall(msg)
    stmx.close()


#vigilant Approach will run a safe approach and check/print/store capacitance values every t seconds
#note that this will run indefinitely until terminated by user
def vigApproach(t):
    c = np.zeros(2)
    buff = np.zeros(10)
    print('Starting Vigilant Approach!')
    print('Press Ctrl-C to terminate!')
    oscOn()
    sleep(0.2)
    for i in range(10):
        buff[i] = LIY()
        sleep(0.2)
    c[0] = np.mean(buff)
    sleep(0.2)
    oscOff()
    sleep(0.2)
    print('Tip-sample capacitance = {}p'.format(np.round(c[0]*1e12,3)))
    print('----------------')
    try:
        while True:
            sleep(0.2)
            autoApproach(1)
            sleep(t)
            autoApproach(0)
            sleep(0.2)
            withdraw()
            sleep(0.2)
            oscOn()
            sleep(0.2)
            for i in range(10):
                buff[i] = LIY()
                sleep(0.2)
            c[1] = np.mean(buff)
            sleep(0.2)
            oscOff()
            print('Tip-sample capacitance = {}p'.format(np.round(c[1]*1e12,3)))
            print('Delta = {}p'.format(np.round(1e12*(c[1]-c[0]),3)))
            print('----------------')
            c[0]=c[1]

    except KeyboardInterrupt:
        sleep(0.2)
        autoApproach(0)
        sleep(0.2)
        withdraw()
        sleep(0.2)
        oscOff()
        sleep(0.2)
        print('Vigilant Approach terminated by user!')
        pass







