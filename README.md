# Markov-Model Analysis of Chord Functions in the Bach Chorales

A project re-creating Chapter 4 of Christopher White's dissertation, [Some Statistical Properties of Tonality, 1650-1900](https://eric.ed.gov/?id=ED556598).

## Running the code

### Setup (for OSX)

1. Meet core requirements.

  * Python 2.7.9 (probably anything 2.7, but 2.7.9 is what I've tested.)
  * Build requirements for GHMM
    * SWIG (`brew install swig`)
    * Up to date libtool (`brew install libtool`)
  * igraph C core (`brew install igraph`, more reliable than letting pip handle it)

2. Install [GHMM](http://ghmm.org/).

  Instructions may have changed, but last I checked the process was:

  ```bash
  svn checkout svn://svn.code.sf.net/p/ghmm/code/trunk/ghmm ghmm
  cd ghmm
  ./autogen.sh
  ./configure
  make CFLAGS='-g -Wall -Wno-return-type' CXXFLAGS='-g -Wall -Wno-return-type' 
  make install
  cd ghmmwrapper
  python setup.py build
  python setup.py install
  ```

3. Install other required packages.

  ```bash
  pip install -r requirements.txt
  ```

### Run

1. Preprocess the bach chorales into chord sequences, and pickle the result.
  ```bash
  python chorale-load.py
  ```

2. Load the chord sequences, and train a bunch of markov models using bigrams from them. Run the Viterbi algorithm on a subset of the sequences, to assign a state of each markov model to every chord (in every sequence) of that subset. Pickle the list of state assignments for each of these chords.

  ```bash
  python chorale-markov.py
  ```

3. Load the state assignments for each chord, and construct a distance matrix where the distance between each pair of chords is the squared sum of the differences between their state assignments. Run a k-means clustering algorithm to find the "average" hidden states, and the chords that "belong" to each. Pickle these average states.
  ```bash
  python chorale-kmeans.py
  ```

4. Using the average states and the chord sequences that we Viterbi'd earlier, calculate state transition probabilities, emission probabilities for each chord for each state, and probability of being in each state. Output that information in a state-machine style graph.

  ```bash
  python chorale-graph.py
  ```

## Compiling the report

```bash
cd tex
pdflatex ai_final_report.tex
bibtex ai_final_report
pdflatex ai_final_report.tex
pdflatex ai_final_report.tex
```
