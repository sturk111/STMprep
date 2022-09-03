import numpy as np
import pandas as pd 
import os
import re
import matplotlib.pyplot as plt
from sklearn.svm import OneClassSVM
from sklearn.mixture import GaussianMixture
import pickle

plt.ion()

#Helper functions for data import
#----------------------------------
def str2num(txt):
    '''
    Convert a string to a floating point number.
    '''
    try:
        s = float(txt)
        return s
    except ValueError:
        return False
    
def importSpec(fn):
    '''
    Import a dI/dV spectrum as a numpy array.
    This reads .dat files that are saved by Nanonis.
    '''
    f = open(fn)
    raw = f.read()
    f.close()
    rawSplit = re.split('\t|\n',raw)
    rawSplit = [i for i in rawSplit if i]
    startInd = rawSplit.index('[DATA]')
    chInd = rawSplit.index('LI Demod 1 X (A)')
    ch = chInd-startInd
    check = False
    c=0
    while check == False:
        check = str2num(rawSplit[chInd+c])
        c+=1
    numCh = ch+c-2
    data = rawSplit[chInd+c-1:-1]
    data = np.array([float(x) for x  in data])
    v = data[0::numCh]
    didv = data[ch-1::numCh]
    return v,didv


#Import data
#---------------------------------
directory = '.../Spectra/Surface state (good tip)' #define file path of positive training data
Xpos=[];
for entry in os.scandir(directory):
    if entry.path.endswith('.dat'):
        fn = entry.path
        v,didv = importSpec(fn)
        Xpos.append(didv/np.mean(didv))

Xpos = np.array(Xpos)
np.random.shuffle(Xpos)
m = np.shape(Xpos)[0]

directory = '.../Spectra/bad tip' #define file path of neg training data
Xneg=[];
for entry in os.scandir(directory):
    if entry.path.endswith('.dat'):
        fn = entry.path
        v,didv = importSpec(fn)
        Xneg.append(didv/np.mean(didv))

Xneg = np.array(Xneg)
np.random.shuffle(Xneg)

#split into train and test sets
Xtrain = Xpos[1:round(0.8*m),:]
Xtest = np.concatenate((Xpos[round(0.8*m):,:],Xneg))
ytest = np.concatenate((np.ones((m-round(0.8*m))),-1*np.ones(len(Xneg))))


#use a gaussian mixture model (GMM) to augment the data set
#---------------------------------
gm = GaussianMixture()
gm.fit(Xpos)

#generate 1000 samples from the GMM
Xgen = []
while len(Xgen)<1e3:
    tmp = gm.sample()[0]
    if np.sum(tmp <=0) == 0:
        Xgen.append(tmp)
Xgen = np.squeeze(np.array(Xgen))

#hyperparameter search for one class support vector machine
#----------------------------------
thresholds = np.linspace(0.01,0.99,20)
specificity = np.zeros(len(thresholds))
recall = np.zeros(len(thresholds))
tp = np.zeros(len(thresholds))
fp = np.zeros(len(thresholds))
fn = np.zeros(len(thresholds))
tn = np.zeros(len(thresholds))
fscore_gen = np.zeros(len(thresholds))

for i,thresh in enumerate(thresholds):
    clf = OneClassSVM(gamma=0.05,nu=thresh).fit(Xgen)
    predictions = clf.predict(Xtest)
    tp[i] = np.sum((predictions==1)*(ytest==1))
    fp[i] = np.sum((predictions==1)*(ytest==-1))
    fn[i] = np.sum((predictions==-1)*(ytest==1))
    tn[i] = np.sum((predictions==-1)*(ytest==-1))
    specificity[i] = tn[i]/(tn[i]+fp[i])
    recall[i] = tp[i]/(tp[i]+fn[i])
    fscore_gen[i] = tp[i]/(tp[i] + 0.5*(fp[i]+fn[i]))

#plot results

font = {'family' : 'Helvetica',
        'weight' : 'normal',
        'size'   : 16}

plt.rc('font', **font)

fig,ax = plt.subplots()

ax.plot(thresholds,tp,color='k')
ax.plot(thresholds,fp,linestyle='-.',color='g')
ax.plot(thresholds,fn,linestyle='--',color='b')

plt.xlim(0,1)
plt.ylim(-0.5,22)
ax.set_aspect(1/22.5)
plt.setp(ax.spines.values(), linewidth=2)
plt.xlabel(r'$\nu$')
plt.ylabel('Counts')
plt.legend(['tp','fp','fn'])
plt.title(r'$N_{train} = 1000$')

plt.tight_layout()
#plt.savefig('...')

#Save the optimal classifier
clf = OneClassSVM(gamma=0.05,nu=0.4).fit(Xgen)

filename = '.../SVM_model.pkl'
pickle.dump(clf, open(filename, 'wb'))
        
