# TODO determine if this file is useful for anything at all.
# Not imported by any other files in this project as of 3/17/17
import copy
import itertools
import random
from collections import defaultdict as ddict
from scipy.cluster.vq import vq, kmeans, whiten
from scipy.spatial.distance import cdist
from numpy import array

def kmeans(numStates, observations):
	print 'Starting k means'
	# distMatrix = []
	# for ob1 in observations:
	# 	distMatrix.append([])
	# 	for ob2 in observations:
	# 		diffs = 0
	# 		for i in range(len(ob1)):
	# 			if ob1[i] != ob2[i]:
	# 				diffs += 1
	# 		distMatrix[-1].append(diffs**2)
	#print distMatrix
	obArray = array(observations)
	distMatrix=cdist(obArray, obArray, 'matching')

	### K MEANS CLUSTER ANALYSIS
	print 'whitening'
	whitened = whiten(distMatrix)
	#print whitened
	print 'kmeans'
	centroids, dist = kmeans(whitened, numStates)
	# print whitened
	# print dir(centroids)

	print 'vq'
	code, distance = vq(whitened, centroids)

	return code, decodeSequences

def main():
	obsFile = open('observations.txt', 'r')
	obsFileList = pickle.load(obsFile)
	obsFile.close()
	codeFileList = []
	for entry in obsFileList:
		numStates = entry[0]
		obs = entry[1]
		code, decodeSequences = kmeans(numStates, obs)
		codeFileList.append((numStates, code, decodeSequences))

	codeFile = open('code.txt', 'w')
	pickle.dump(codeFileList, codeFile)
	codeFile.close()
	
