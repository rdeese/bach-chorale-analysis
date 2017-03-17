from scipy.spatial.distance import cdist
from numpy import array, zeros
from sklearn.cluster import KMeans as skMeans
from sklearn.metrics import silhouette_score as silScore
from Pycluster import kmedoids
import cPickle
import time

def getKMeans(numStates, observations):
	print 'K-means for', numStates, 'states'
	print 'Getting distance matrix:'
	start_time = time.time()
	obsLen = len(observations)
	distMatrix = [[0 for _ in range(obsLen)] for _ in range(obsLen)]
	for i in range(obsLen):
		for j in range(i, obsLen):
			diffs = 0
			for k in range(len(observations[i])):
				if observations[i][k] != observations[j][k]:
					diffs += 1
			distMatrix[i][j] = distMatrix[j][i] = diffs**2
	print 'Got in', time.time() - start_time, "seconds."

	obArray = array(observations)
	distMatrix = array(distMatrix)
	#print obArray

	print "Clustering:"
	start_time = time.time()
	kmeansModel = skMeans(n_clusters=numStates, n_init=10).fit(distMatrix)
	code = kmeansModel.labels_
	nfound = 1
#	code, silhouetteScore, nfound = kmedoids(distMatrix, nclusters=numStates, npass=300)
	silhouetteScore = silScore(distMatrix, code, metric='euclidean')
	print "Clustered in", time.time() - start_time, "seconds, found best solution", \
	nfound, "times, with score of", silhouetteScore


	return code, silhouetteScore

def main():
	obsFile = open('observations.txt', 'r')
	print 'Loading data:'
	start_time = time.time()
	obsFileList = cPickle.load(obsFile)
	print 'Pickled in', time.time() - start_time, "seconds."

	obsFile.close()
	codeFileList = []
	silScores = []
	for i in range(len(obsFileList)):
		numStates, obs, decodeSequences = obsFileList[i]
		code, silhouetteScore = getKMeans(numStates, obs)
		codeFileList.append((numStates, code, decodeSequences))
		silScores.append(silhouetteScore)

	codeFileList.append(('dists', silScores))
	codeFile = open('code.txt', 'w')
	cPickle.dump(codeFileList, codeFile)
	codeFile.close()

if __name__ == "__main__":
	main()
