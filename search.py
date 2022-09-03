import stm
from time import sleep
import numpy as np

approachBias = 1 #(V)
approachCurrent = 50e-12 #(A)
stepsOut = 5 #number of steps out to take in z before moving in x/y
stepSize = 2 #number of x/y steps to take at a time (i.e. without checking capacitance or crash in between)
capThresh = 0.10 #percent rise of capacitance allowed while moving in x or y before taking more steps out
#note that steps taken will be rounded up to the nearest integer divisible by stepSize
rThresh = 0.5#if the roughness exceeds this threshold (in nm), the script will move on to the next spot
path = 0#list of x,y values to visit in the search procedure
testVoltage = 50#strainDirection function will sweep to this voltage (V)

#decides whether or not to stay in this area (True = stay, False = go)
#scan parameters (size, speed, tilt, etc.) must be set manually in nanonis
def flatEnough():
	r = stm.roughness(3)
	if r > rThresh:
		return False
	else:
		return True


#move x steps and y steps from present position, taking care not to crash by monitoring scope and capacitance
#starts from tunneling position and tries to end in tunneling position at new location
#returns 1 if final position is tunneling, 0 if failed
#tunneling is defined as the current being within 10% of the set point after feedback has been on for 10 seconds
#Note: uses LIY for capacitance measurements (make sure the phase is set for this!)
def move(x,y):
	stm.withdraw()
	sleep(0.1)

	dir1 = (x>0)*0 + (x<0)*1
	dir2 = (y>0)*2 + (y<0)*3
	signx = np.sign(x)
	signy = np.sign(y)

	x = abs(x)
	y = abs(y)

	stm.coarseSet(700,300)
	sleep(0.1)

	stm.osciRun()
	sleep(0.1)

	stm.clearScope()
	sleep(0.1)

	stm.oscAmp(0.5)
	sleep(0.1)

	stm.oscOn()
	sleep(0.1)

	Cs = stm.LIY()
	sleep(0.1)

	stm.move(5,stepsOut)
	sleep(0.1)

	C0 = stm.LIY()
	sleep(0.1)

	xtaken = 0
	ytaken = 0

	crashLog = []
	while xtaken < x:
		C = stm.LIY()
		sleep(0.1)
		crashed = stm.crash()
		sleep(0.1)

		while C < (C0 + capThresh*(Cs-C0)) and not crashed and xtaken < x:
			diff = x-xtaken
			step = (diff<stepSize)*diff + (diff>=stepSize)*stepSize
			stm.move(dir1,step)
			sleep(0.1)
			
			xtaken += step

			C = stm.LIY()
			sleep(0.1)
			
			crashed = stm.crash()
			sleep(0.1)

			if crashed:
				crashLog.append([signx*xtaken,signy*ytaken])

		if xtaken < x:
			stm.move(5,stepsOut)
			sleep(0.1)

	while ytaken < y:
		C = stm.LIY()
		sleep(0.1)
		crashed = stm.crash()
		sleep(0.1)

		while C < (C0 + capThresh*(Cs-C0)) and not crashed and ytaken < y:
			diff = y-ytaken
			step = (diff<stepSize)*diff + (diff>=stepSize)*stepSize
			stm.move(dir2,step)
			sleep(0.1)
			
			ytaken += step

			C = stm.LIY()
			sleep(0.1)
			
			crashed = stm.crash()
			sleep(0.1)

			if crashed:
				crashLog.append([signx*xtaken,signy*ytaken])

		if ytaken < y:
			stm.move(5,stepsOut)
			sleep(0.1)

	stm.oscOff()
	sleep(0.1)

	stm.coarseSet(700,150)
	sleep(1)

	stm.followMe(0,0)
	sleep(0.1)

	stm.gainSet(1,180e-6)
	sleep(0.1)

	stm.setSet(approachCurrent)
	sleep(0.1)

	stm.biasSet(approachBias)
	sleep(0.1)

	stm.clearScope()
	sleep(0.1)

	print('Safe Approach Active!')

	stm.autoApproach(1)
	sleep(0.1)

	approaching = stm.autoApproachStatus()
	sleep(0.1)

	crashed = stm.crash()
	sleep(0.1)

	while approaching and not crashed:
		approaching = stm.autoApproachStatus()
		sleep(3)

		crashed = stm.crash()
		sleep(0.1)

	stm.withdraw()
	sleep(0.1)

	stm.gainSet(0.3,180e-6)
	sleep(0.1)

	stm.feedbackOn()
	sleep(15)

	tunneling = stm.tunneling(approachCurrent)
	sleep(0.1)

	if not tunneling:
		stm.withdraw()
		sleep(0.1)

	return tunneling, crashed, crashLog #if crashed returns true, then it crashed on approach




