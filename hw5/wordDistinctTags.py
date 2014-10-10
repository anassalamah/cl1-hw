from nltk.corpus import brown
from collections import defaultdict


def main():
    '''
    this will create a dictionary like d[word] = [tag1,tag2,tag3,...]
    '''
    d = defaultdict(list)
    for word,tag in brown.tagged_words():
        if not word in d:
            d[word].append(tag)
        else:
            if not tag in d[word]:
                d[word].append(tag)
    '''
    this will set the number
    '''
    oneTag = defaultdict(int)
    twoTag = defaultdict(int)
    threeTag = defaultdict(int)
    fourTag = defaultdict(int)
    fiveTag = defaultdict(int)
    sixTag = defaultdict(int)
    sevenTag = defaultdict(int)
    eightTag = defaultdict(int)
    nineTag = defaultdict(int)
    tenTag = defaultdict(int)
    for word in d:
        oneTag[word] += 1
        '''if len(d[word]) == 1:
            oneTag[word] += 1
        elif len(d[word]) == 2:
            twoTag[word] += 1
        elif len(d[word]) == 3:
            threeTag[word] += 1
        elif len(d[word]) == 4:
            fourTag[word] += 1
        elif len(d[word]) == 5:
            fiveTag[word] += 1
        elif len(d[word]) == 6:
            sixTag[word] += 1
        elif len(d[word]) == 7:
            sevenTag[word] += 1
        elif len(d[word]) == 8:
            eightTag[word] += 1
        elif len(d[word]) == 9:
            nineTag[word] += 1
        elif len(d[word]) == 10:
            tenTag[word] += 1'''
    print len(oneTag)
    '''
    find word with maximum number of tags
    '''
    maxLength = 0
    maxWord = ''
    for word in d:
        if len(d[word]) > maxLength:
            maxLength = len(d[word])
            maxWord = word
    '''
    find sentences for each tag of word with maximum number of tags
    '''
    sentences = defaultdict(int)
    for sent in brown.tagged_sents():
        for word,tag in sent:
            for dictTag in d[word]:
                if word == 'that' and tag == dictTag:
                        sentences[word+' as a '+tag] = sent
    

if __name__ == "__main__": main()
