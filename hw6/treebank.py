# Author: Anas Salamah
# Date: Oct 21, 2014

import nltk
from collections import defaultdict
from nltk import grammar
from nltk.grammar import Nonterminal, Production, is_nonterminal
from sets import Set
from copy import deepcopy
from nltk.tree import Tree

class PcfgEstimator:
    """
    Estimates the production probabilities of a PCFG
    """
    def __init__(self):
        self._counts = defaultdict(nltk.FreqDist)
	self._flag = False
    def add_sentence(self, sentence):
        """
        Add the sentence to the dataset
        """
        if not isinstance(sentence, Tree):
            return sentence
	elif self._flag:
            self._flag = False
            self._counts[str(sentence.node)].inc(" ".join([t.node if isinstance(t, Tree) else t for t in sentence]))
            for t in sentence:
                if isinstance(t, Tree):
                    self._flag = True
                    self.add_sentence(t)
        else:
            for t in sentence:
                self._flag = True
                self.add_sentence(t)


    def query(self, lhs, rhs):
        """
        Returns the MLE probability of this production
        """

        return self._counts[lhs].freq(rhs)
