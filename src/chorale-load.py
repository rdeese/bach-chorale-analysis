from music21 import *
import copy
from collections import defaultdict as ddict
import cPickle

def parseCorpus():
	# Get the bach chorales
	bCorpus = corpus.chorales.Iterator()
	sequences = []
	seenChords = ddict(int)

	numParsed = 0

	# Get sequences from each chorale
	for chorale in bCorpus:
		numParsed += 1
		print 'Loading', chorale.corpusFilepath
		print 'Getting slices...'
		# Convert the chorale into a series of quarter-note chords.
		slices = alpha.theoryAnalysis.theoryAnalyzer.getVerticalities(chorale, classFilterList=['Note'])
		sliceStream = stream.Stream()
		for s in slices:
			sliceStream.append(chord.Chord(map(lambda X: X[0], s.contentDict.values())))

		print 'Windowed key analysis...'
		# Do windowed key analysis using Bellman-Budge algorithm.
		bB = analysis.discrete.BellmanBudge()
		wA = analysis.windowed.WindowedAnalysis(sliceStream, bB)
		aR = wA.process(8,8,1,includeTotalWindow=False)
		guessedKeys = aR[0][0]

		print 'Collecting sequences...'
		# Collect sequences from the chorale
		# The current sequence starts empty, with the key first guessed by the alg.
		curSeq = []
		curKey = None

		# For each chord
		for i in range(len(sliceStream)):
			# Determine the key guesses that it was windowed in:
			wFirst = max(i-7,0)
			wLast = i+1
			keyGueses = map(lambda X: (X[0].pitchClass, X[1]), guessedKeys[wFirst:wLast])

			# If the guesses all agree...
			if len(set(keyGueses)) == 1 and keyGueses[0][1] == 'major':
				nextChord = tuple(sliceStream[i].transpose(-keyGueses[0][0]).orderedPitchClasses)
				# If it's a new key, end the current sequence and start a new one with
				# this chord first.
				if keyGueses[0] != curKey:
					curKey = keyGueses[0]
					if len(curSeq) != 0:
						sequences.append(copy.deepcopy(curSeq))
					seenChords[nextChord] += 1
					curSeq = [nextChord]

				# If its the current key, only add the chord if it's different from the
				# previous chord and not a small cardinality subset.
				# ALSO, if the previous chord was of small cardinality, and this chord
				# is a superset of it, delete the previous chord and append this one.
				else:
					lChord = set(curSeq[-1])
					nChord = set(nextChord)
					if nextChord != curSeq[-1]:
						if len(nextChord) > 3 or not nChord.issubset(lChord):
							seenChords[nextChord] += 1
							curSeq.append(nextChord)
						elif len(curSeq[-1]) < 3 and nChord.issuperset(lChord):
							del curSeq[-1]
							seenChords[curSeq[-1]] -= 1
							seenChords[nextChord] += 1
							curSeq.append(nextChord)

			# Otherwise, end the current sequence.
			else:
				curKey = None
				if len(curSeq) != 0:
					sequences.append(copy.deepcopy(curSeq))
				curSeq = []

		if len(curSeq) != 0:
			sequences.append(copy.deepcopy(curSeq))
		curSeq = []
		curKey = None

	temp = open('chords_before_remove.txt', 'w')
	cPickle.dump(sequences, temp)
	temp.close

	### Remove the 40% least-probable chord types
	l = len(seenChords)
	sortedSeenChords = sorted(seenChords, reverse=True, key=seenChords.get)
	seenChordsList = sortedSeenChords[:6*l/10]
	notProbChords = sortedSeenChords[6*l/10:]

	allSequences = []
	for s in sequences:
		i = 0
		for k in range(len(s)):
			if s[k] in notProbChords:
				newSeq = s[i:k]
				if len(newSeq) > 1:
					allSequences.append(newSeq)
				i = k+1
		if i < len(s)-1:
			allSequences.append(s[i:])

	print "Parsed", numParsed, "works, got", len(sequences), "sequences. The sequences", \
		"have an average length of", sum(map(len, sequences))/len(sequences), \
		". The 40 percent least common chords were removed," \
		"resulting in an average sequence length of", sum(map(len, allSequences))/len(allSequences), \
		", and", len(allSequences), "total sequences."
	print "The", len(seenChordsList), "chords seen are:\n", \
		"\n".join([chord.Chord(X).pitchedCommonName for X in seenChordsList])
	print "with the following", len(notProbChords), "least common chords removed:\n", \
		"\n".join([chord.Chord(X).pitchedCommonName for X in notProbChords])

	seqs = open('seqs_and_chords.txt', 'w')
	cPickle.dump((allSequences, seenChordsList), seqs)
	seqs.close()

if __name__ == "__main__":
	parseCorpus()
