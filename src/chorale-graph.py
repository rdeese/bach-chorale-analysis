from music21 import *
import igraph
from collections import defaultdict as ddict
from numpy import array
#import matplotlib.pyplot as plt
import cPickle
import time
import os

import pylab
from pylab import arange,pi,sin,cos,sqrt

def drawGraph(numStates, rawCode, decodeSequences, out, label):
	## Get transition probabilities for each transition and
	## go through the kmeans code to construct chord function dicts.
	transProb = ddict(int)
	flatDecSeqs = sum(decodeSequences, [])
	chordFunctions = []

	codeTransDict = {}
	statesToTrans = set(rawCode)
	i = 0
	for state in statesToTrans:
		codeTransDict[state] = i
		i += 1

	code = array(map(lambda X: codeTransDict[X], rawCode))

	for i in range(numStates):
		chordFunctions.append(ddict(int))
	for i in range(len(code)-1):
		transProb[(code[i],code[i+1])] += 1
		chordFunctions[code[i]][flatDecSeqs[i]] += 1
	chordFunctions[code[-1]][flatDecSeqs[-1]] += 1
	numTrans = len(code)-1

	# for s in chordFunctions:
	# 	print sorted(s)

	# Make directed graph using igraph
	edges = []
	edge_attrs = {}
	edge_attrs["weight"] = []
	edge_attrs["width"] = []
	edge_attrs["arrow_size"] = []
	vertex_attrs = {}
	vertex_attrs["label"] = []
	vertex_attrs["size"] = []
	weights = []
	
	out.write('Model for '+str(numStates)+' states:\n')

	for i in range(numStates):
		probChords = map(lambda X: str(round(float(chordFunctions[i][X])/sum(chordFunctions[i].values()),2))
			+', '+chord.Chord(X).pitchedCommonName, 
			sorted(chordFunctions[i], key=chordFunctions[i].get, reverse=True)) [:4]

		vertex_attrs["label"].append(i)
		vertex_attrs["size"].append(10+30*(numStates**.5)*(float((code==i).sum())/len(code)))
		for j in range(numStates):
			edges.append((i,j))
			weight = float(transProb[(i,j)])/numTrans
			if weight < 0.01:
				weight = 0
			edge_attrs["weight"].append(weight)
			edge_attrs["width"].append(weight*15*(numStates**.5))
			edge_attrs["arrow_size"].append(weight*5*numStates**.5)

		out.write('State '+str(i)+': '+ '; '.join(probChords)+'\n')
	out.write('\n\n')


	g = igraph.Graph(edges, directed=True, edge_attrs=edge_attrs, vertex_attrs=vertex_attrs);
	l = g.layout('kamada_kawai')
	print 'hi3'
	gPlot = igraph.plot(g,label+'-model-'+str(numStates)+'.pdf', labellayout=l, margin=(40), bbox=(300,300),
		vertex_color='white')
	print 'hi4'

def main():
	label = time.strftime("%m%d%H%M%S")
	codeFile = open('code.txt', 'r')
	print 'hi'
	codeFileList = cPickle.load(codeFile)
	print 'hi2'
	codeFile.close()
	os.mkdir(label)
	os.chdir(label)
	out = open(label+'-modelEmissions.txt', 'w')
	silPlotX = []
	for entry in codeFileList:
		if entry[0] == 'dists':
			dists = entry[1]
		else:
			numStates, code, decodeSequences = entry
			silPlotX.append(numStates)
			drawGraph(numStates, code, decodeSequences, out, label)
	out.close()

	fig_width_pt = 239.3943  # Get this from LaTeX using \showthe\columnwidth
	inches_per_pt = 1.0/72.27               # Convert pt to inch
	golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
	fig_width = fig_width_pt*inches_per_pt  # width in inches
	fig_height = fig_width*golden_mean      # height in inches
	fig_size =  [fig_width,fig_height]
	params = {'backend': 'ps',
	          'axes.labelsize': 10,
	          'text.fontsize': 10,
	          'legend.fontsize': 10,
	          'xtick.labelsize': 8,
	          'ytick.labelsize': 8,
	          'text.usetex': True,
	          'figure.figsize': fig_size}
	pylab.rcParams.update(params)

	# Plot data
	pylab.figure(1)
	pylab.clf()
	pylab.axes([0.16,0.2,0.95-0.16,0.95-0.2])
	pylab.plot(silPlotX, dists)
	pylab.xlabel('$k$ (number of states)')
	pylab.ylabel('Silhouette Score')
	pylab.legend()
	pylab.savefig('fig1.eps')


if __name__ == "__main__":
	main()