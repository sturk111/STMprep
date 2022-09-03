from random import random
import pickle
import stm
import search

#start from tunnelinng

filename = '.../SVM_model.pkl'
clf = pickle.load(open(filename,'rb'))

tunneling = stm.tunneling(search.approachCurrent)
stepsX = 10
stepsY = 0
maxPokes = 50

Npokes=0
while True:
	tunneling = stm.tunneling(search.approachCurrent)
	if tunneling and (Npokes <= maxPokes): 
		flat = search.flatEnough()
		if flat:
			_, spec, _ = stm.spec()[2,:] #get the channel correct!
			good = clf.predict(spec.reshape(1,-1))[0] == 1
			if good:
				return
			if not good:
				x,y = random()*80 - 40, random()*80 - 40
				stm.followMe(x,y)
				stm.poke()
				Npokes += 1
		if not flat:
			tunneling, _, _ = search.move(stepsX, stepsY) 
			Npokes = 0
	if not tunneling:
		tunneling, _, _ = search.move(stepsX, stepsY)
		Npokes = 0

