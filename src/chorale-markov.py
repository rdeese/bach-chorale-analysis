from ghmm import *
import random
import cPickle

def seqsToBigram(seqs):
	flatSeq = sum(seqs, [])
	allSeqsBigram = []
	for i in range(len(flatSeq)-1):
		allSeqsBigram.append([flatSeq[i], flatSeq[i+1]])
	return allSeqsBigram

def runMarkov(numStates, numTrials, allSequences, seenChordsList):
	bigramSeqs = seqsToBigram(allSequences)
	#random.shuffle(bigramSeqs)
	trainingSequences = bigramSeqs
	decodeSequences = allSequences[:200]
	observations = []
	for i in range(len(sum(decodeSequences, []))):
		observations.append([])

	print "Running", numTrials, "randomly initialized HMMs with", \
		numStates, "states each. Training on", len(trainingSequences), \
		"bigrams, and subsequently decoding", len(decodeSequences), \
		"sequences with an average length of", sum(map(len, decodeSequences))/len(decodeSequences)

	### Begin state machine
	sigma = Alphabet(seenChordsList)
	train_seqs = SequenceSet(sigma, trainingSequences)
	decode_seqs = SequenceSet(sigma, decodeSequences)

	for trial in range(numTrials):
		tProbs = []
		eProbs = []
		initProbs = []
		for i in range(numStates):
			initProbs.append(random.random())
			#initProbs.append(1.0/numStates)
			tProbs.append([])
			eProbs.append([])
			for j in range(numStates):
				tProbs[-1].append(random.random())
				#tProbs[-1].append(1.0/numStates)
			for k in range(len(sigma)):
				eProbs[-1].append(random.random())
				#eProbs[-1].append(1.0/len(sigma))
			s = sum(tProbs[-1])
			tProbs[-1] = map(lambda X: X/s, tProbs[-1])
			s = sum(eProbs[-1])
			eProbs[-1] = map(lambda X: X/s, eProbs[-1])

		s = sum(initProbs)
		initProbs = map(lambda X: X/s, initProbs)

		hmm = HMMFromMatrices(sigma, DiscreteDistribution(sigma), tProbs, eProbs, initProbs)
		hmm.baumWelch(train_seqs)
		obs = hmm.viterbi(decode_seqs)[0]

		i = 0
		for s in obs:
			for ob in s:
				observations[i].append(ob)
				i += 1
	return observations, decodeSequences

def main():
	seqs = open('seqs_and_chords.txt', 'r')
	allSequences, seenChordsList = cPickle.load(seqs)
	seqs.close()

	obsFileList = []

	for numStates in range(2,16):
		observations, decodeSequences = runMarkov(numStates, 50, allSequences, seenChordsList)
		obsFileList.append((numStates, observations, allSequences))

	obsFile = open('observations.txt', 'w')
	cPickle.dump(obsFileList, obsFile)
	obsFile.close()

if __name__ == "__main__":
	main()