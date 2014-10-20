import sys

import nltk
from nltk.corpus import dependency_treebank
from nltk.classify.maxent import MaxentClassifier
from nltk.classify.util import accuracy

VALID_TYPES = set(['s', 'l', 'r'])

class Transition:
    def __init__(self, type, edge=None):
        self._type = type
        self._edge = edge
        assert self._type in VALID_TYPES

    def pretty_print(self, sentence):
        if self._edge:
            a, b = self._edge
            return "%s\t(%s, %s)" % (self._type,
                                     sentence.get_by_address(a)['word'],
                                     sentence.get_by_address(b)['word'])
        else:
            return self._type

def transition_sequence(sentence):
    """
    Return the sequence of shift-reduce actions that reconstructs the input sentence.
    """
	
    sentence_length = len(sentence.nodelist)
    for ii in xrange(sentence_length - 1):
    	if sentence.nodelist[ii]['address'] != 0:
    	    if not sentence.nodelist[ii]['deps'] or all(i > sentence.nodelist[ii]['address'] for i in sentence.nodelist[ii]['deps']):
    		yield Transition('s')
            else:
                for kk in sentence.nodelist[ii]['deps']:
                    """ finding left Transitions by saying if ii[deps] == ii-1[address] """
                    if kk == sentence.nodelist[ii-1]['address']:
        		sentence.nodelist[ii]['deps'].remove(kk)
        		yield Transition('l', (ii, ii-1))
        		""" shift after left transition if ii[deps] has value less than it's """
        		#if all(i > sentence.nodelist[ii]['address'] for i in sentence.nodelist[ii]['deps']):
        		if sentence.nodelist[ii]['address'] == sentence.nodelist[0]['deps'][0] or sentence.nodelist[ii]['head'] > sentence.nodelist[ii]['address'] or  sentence.nodelist[ii]['head'] == sentence.nodelist[sentence.nodelist[0]['deps'][0]]['address']:
                            yield Transition('s')
        	
    for ii in xrange(sentence_length - 1, 1, -1):
    	if sentence.nodelist[ii-1]['deps']:
    		for kk in sentence.nodelist[ii-1]['deps']:
    			if kk == sentence.nodelist[ii]['address']:
    				sentence.nodelist[ii-1]['deps'].remove(kk)
        			yield Transition('r', (sentence.nodelist[ii-1]['address'], sentence.nodelist[ii]['address']))
        		elif kk == sentence.nodelist[ii]['head']:
    				sentence.nodelist[ii-1]['deps'].remove(kk)
        			yield Transition('r', (sentence.nodelist[ii-1]['address'], sentence.nodelist[ii]['head']))
        			if sentence.nodelist[ii-1]['deps']:
        				yield Transition('s')
        				if sentence.nodelist[ii-1]['deps'][0] == sentence.nodelist[sentence_length - 1]['address']:
        					yield Transition('r', (sentence.nodelist[ii-1]['address'], sentence.nodelist[sentence_length - 1]['address']))
    for ii in xrange(sentence_length - 1):
    	if sentence.nodelist[ii]['address'] == sentence.nodelist[0]['deps'][0]:
    		yield Transition('r', (0, sentence.nodelist[ii]['address']))
    yield Transition('s')



#transitions = list(transition_sequence(dep))
