# Author: Anas Salamah
# Date: Sept 26th, 2014
from math import log, exp
from collections import defaultdict
from string import lower
import argparse

from numpy import mean

import nltk
from nltk import FreqDist
from nltk.util import bigrams
from nltk.tokenize import TreebankWordTokenizer

kLM_ORDER = 2
kUNK_CUTOFF = 3
kNEG_INF = -1e6

kSTART = "<s>"
kEND = "</s>"
kUNK = "<UNK>"

def lg(x):
    return log(x) / log(2.0)

class BigramLanguageModel:

    def __init__(self, unk_cutoff, jm_lambda=0.6, dirichlet_alpha=0.1,
                 katz_cutoff=5, kn_discount=0.1, kn_concentration=1.0,
                 tokenize_function=TreebankWordTokenizer().tokenize,
                 normalize_function=lower):
        self._unk_cutoff = unk_cutoff
        self._jm_lambda = jm_lambda
        self._dirichlet_alpha = dirichlet_alpha
        self._katz_cutoff = katz_cutoff
        self._kn_concentration = kn_concentration
        self._kn_discount = kn_discount
        self._vocab_final = False

        self._tokenizer = tokenize_function
        self._normalizer = normalize_function
	
	self._dictionary = defaultdict(int)
	self._bigram = defaultdict(int)
	self._unigram = defaultdict(int)
	self._recursing = False
    def train_seen(self, word, count=1):
        """
        Tells the language model that a word has been seen @count times.  This
        will be used to build the final vocabulary.
        """
        assert not self._vocab_final, \
            "Trying to add new words to finalized vocab"

	self._dictionary[word] += count

    def tokenize(self, sent):
        """
        Returns a generator over tokens in the sentence.  

        You don't need to modify this code.
        """
        for ii in self._tokenizer(sent):
            yield ii
        
    def vocab_lookup(self, word):
        """
        Given a word, provides a vocabulary representation.  Words under the
        cutoff threshold shold have the same value.  All words with counts
        greater than or equal to the cutoff should be unique and consistent.
        """
        assert self._vocab_final, \
            "Vocab must be finalized before looking up words"

	if word == kSTART or word == kEND:
		return word
	else:
		if self._dictionary[word] < self._unk_cutoff:
			return kUNK
		else:
			return word

    def finalize(self):
        """
        Fixes the vocabulary as static, prevents keeping additional vocab from
        being added
        """
        self._vocab_final = True

    def tokenize_and_censor(self, sentence):
        """
        Given a sentence, yields a sentence suitable for training or
        testing.  Prefix the sentence with <s>, replace words not in
        the vocabulary with <UNK>, and end the sentence with </s>.
        """
        yield self.vocab_lookup(kSTART)
        for ii in self._tokenizer(sentence):
            yield self.vocab_lookup(self._normalizer(ii))
        yield self.vocab_lookup(kEND)


    def normalize(self, word):
        """
        Normalize a word
        """
        return self._normalizer(word)


    def mle(self, context, word):
        """
        Return the log MLE estimate of a word given a context.  If the
        MLE would be negative infinity, use kNEG_INF
        """
	if self._bigram.has_key(context+word):
		if self._unigram.has_key(context):
			mle = float(self._bigram[context+word]) / (self._unigram[context])
		else:
			mle = 1
		return lg(mle)

	else:
		mle = kNEG_INF
		return mle
        

    def laplace(self, context, word):
        """
        Return the log MLE estimate of a word given a context.
        """
        V = 0.0
	for i,n in self._unigram.items():
		V += n
	if self._bigram.has_key(context+word):
		if self._unigram.has_key(context):
			laplace = float(self._bigram[context+word] + 1) / (self._unigram[context] + V)
		else:
			laplace = float(self._bigram[context+word] + 1) / (1 + V)
	else:
		if self._unigram.has_key(context):
			laplace = float(1) / (self._unigram[context] + V)
		else:
			laplace = float(1) / (1 + V)
	return lg(laplace)
    def good_turing(self, context, word):
        """
        Return the Good Turing probability of a word given a context
        """
        return 0.0

    def jelinek_mercer(self, context, word):
        """
        Return the Jelinek-Mercer log probability estimate of a word
        given a context; interpolates context probability with the
        overall corpus probability.
        """
	V = 0.0
	for i,n in self._unigram.items():
		V += n
	if self._bigram.has_key(context+word):
		pwC = float(self._unigram[word] + 1) / len(self._unigram)
	else:
		pwC = 0
	if self._bigram.has_key(context+word):
		pw = float(self._bigram[context+word] + 1) / (V)
	else:
		pw = float(1) / (V)
	jm = self._jm_lambda * pwC + (1.0 - self._jm_lambda) * pw
	jm = lg(jm)
	return jm
    def kneser_ney(self, context, word):
        """
        Return the log probability of a word given a context given
        Kneser Ney backoff
        """
	""" V number of Values in context restaurant"""
	V = 0.0
	Cuni = 0.0
	for i,n in self._unigram.items():
		V += n
	for t,v in self._unigram.items():
		Cuni += v
	"""    kn = knL + knR( CknL + CknR*1/V) """
	""" or kn = knL + knR
	*** so kn = knL + knR(kn * 1/V)
	"""
	if not self._recursing:
		if self._bigram.has_key(context+word):
			if self._unigram.has_key(context):
				knL = float(self._bigram[context+word] - self._kn_discount) / (self._kn_concentration + self._unigram[context])
				"fix that one to count of something dynamic"
				knR = float(self._kn_concentration + (1 * self._kn_discount)) / (self._kn_concentration + self._unigram[context])
			else:
				knL = float(self._bigram[context+word] -  self._kn_discount) / (1 + self._kn_concentration)
				knR = float(self._kn_concentration + (1 * self._kn_discount)) / (1 + self._kn_concentration)
		else:
			knL = 0.0
			if self._unigram.has_key(context):
				 knR = float(self._kn_concentration + (1 * self._kn_discount)) / (self._kn_concentration + self._unigram[context])
			else:
				knR = float(self._kn_concentration + (1 * self._kn_discount)) / (1 + self._kn_concentration)
	else:
		if self._bigram.has_key(context+word):
			knL = float(self._bigram[context+word] + 1 - self._kn_discount) / (Cuni + self._kn_concentration)
			knR = float(self._kn_concentration + len(self._unigram) * self._kn_discount) / (Cuni + self._kn_concentration)
		else:
			knL = float(1 - self._kn_discount) / (Cuni + self._kn_concentration)
			knR = float(self._kn_concentration + len(self._unigram) * self._kn_discount) / (Cuni + self._kn_concentration)
	if self._recursing:
		interkn = knR * 1/V
		kn = knL + interkn
	else:
		self._recursing = True
		interkn = knR * self.kneser_ney(context,word)
		self._recursing = False
		kn = knL + interkn
		kn = lg(kn)
	return kn

    def dirichlet(self, context, word):
        """
        Additive smoothing, assuming independent Dirichlets with fixed
        hyperparameter.
        """
        V = 0.0
	for i,n in self._unigram.items():
		V += n
	if self._bigram.has_key(context+word):
		if self._unigram.has_key(context):
			dirichlet = float(self._bigram[context+word] + self._dirichlet_alpha) / (self._unigram[context] + (self._dirichlet_alpha * V))
		else:
			dirichlet = float(self._bigram[context+word] + self._dirichlet_alpha) / (1 + (self._dirichlet_alpha * V))
	else:
		if self._unigram.has_key(context):
			dirichlet = float(self._dirichlet_alpha) / (self._unigram[context] + (self._dirichlet_alpha * V))
		else:
			dirichlet = float(self._dirichlet_alpha) / (1 + (self._dirichlet_alpha * V))
	return lg(dirichlet)

    def add_train(self, sentence):
        """
        Add the counts associated with a sentence.
        """

        for context, word in bigrams(self.tokenize_and_censor(sentence)):
		if self._bigram.has_key(context+word):
			self._bigram[context+word] += 1
		else:
			self._unigram[word] += 1
			self._bigram[context+word] += 1

    def perplexity(self, sentence, method):
	"""
	Compute the perplexity of a sentence given a estimation method
        """
	return 2.0 ** (-1.0 * mean([method(context, word) for context, word in \
                                    bigrams(self.tokenize_and_censor(sentence))]))

    def sample(self, samples=25):
        """
        Sample words from the language model.
        
        @arg samples The number of samples to return.
        """
        yield ""
        return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--jm_lambda", help="Parameter that controls " + \
                           "interpolation between unigram and bigram",
                           type=float, default=0.6, required=False)
    argparser.add_argument("--dir_alpha", help="Dirichlet parameter " + \
                           "for pseudocounts",
                           type=float, default=0.1, required=False)
    argparser.add_argument("--unk_cutoff", help="How many times must a word " + \
                           "be seen before it enters the vocabulary",
                           type=int, default=2, required=False)    
    argparser.add_argument("--katz_cutoff", help="Cutoff when to use Katz " + \
                           "backoff",
                           type=float, default=0.0, required=False)
    argparser.add_argument("--lm_type", help="Which smoothing technique to use",
                           type=str, default='mle', required=False)
    argparser.add_argument("--brown_limit", help="How many sentences to add " + \
                           "from Brown",
                           type=int, default=-1, required=False)
    argparser.add_argument("--kn_discount", help="Kneser-Ney discount parameter",
                           type=float, default=0.1, required=False)
    argparser.add_argument("--kn_concentration", help="Kneser-Ney concentration parameter",
                           type=float, default=1.0, required=False)
    argparser.add_argument("--method", help="Which LM method we use",
                           type=str, default='laplace', required=False)
    
    args = argparser.parse_args()    
    lm = BigramLanguageModel(kUNK_CUTOFF, jm_lambda=args.jm_lambda,
                             dirichlet_alpha=args.dir_alpha,
                             katz_cutoff=args.katz_cutoff,
                             kn_concentration=args.kn_concentration,
                             kn_discount=args.kn_discount)

    for ii in nltk.corpus.brown.sents():
        for jj in lm.tokenize(" ".join(ii)):
            lm.train_seen(lm._normalizer(jj))

    print("Done looking at all the words, finalizing vocabulary")
    lm.finalize()

    sentence_count = 0
    for ii in nltk.corpus.brown.sents():
        sentence_count += 1
        lm.add_train(" ".join(ii))

        if args.brown_limit > 0 and sentence_count >= args.brown_limit:
            break

    print("Trained language model with %i sentences from Brown corpus." % sentence_count)
    assert args.method in ['kneser_ney', 'mle', 'dirichlet', \
                           'jelinek_mercer', 'good_turing', 'laplace'], \
      "Invalid estimation method"

    sent = raw_input()
    while sent:
        print("#".join(str(x) for x in lm.tokenize_and_censor(sent)))
        print(lm.perplexity(sent, getattr(lm, args.method)))
        sent = raw_input()
