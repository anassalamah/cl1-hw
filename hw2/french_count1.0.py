import sys
from fst import FST
from fsmutils import composewords, trace

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    return list("%03i" % integer)

def french_count():
    f = FST('french')

    f.add_state('start')
    # one number and two trailing unknowns
    f.add_state('n**')
    # exception from state n**
    f.add_state('n**+')
    # two numbers and one trailing unknown
    f.add_state('nn*')
    # zero and two uknown digits trailing and so on
    f.add_state('0**')
    f.add_state('00*')
    f.add_state('00n')
    f.add_state('0n*')
    f.add_state('0n*+')
    f.add_state('0nn')
    f.add_state('n00')
    f.add_state('nnn')
    f.add_state('nnn*')
    f.add_state('*et*')
    # vegasimal counting for 7 in ((0/n)n*)
    f.add_state('0n*Vega7+')
    f.add_state('0n*Vega7')
    f.add_state('0nnVega7')
    # vegasimal counting for 8 in ((0/n)n*)
    f.add_state('0n*Vega8')
    f.add_state('0n*Vega8+')
    f.add_state('0nnVega8')
    # vegasimal counting for 9 in ((0/n)n*)
    f.add_state('0n*Vega9')
    f.add_state('0n*Vega9+')
    f.add_state('0n*Vega9++')
    f.add_state('0nnVega9')

    # set final states
    f.set_final('00n')
    f.set_final('0nn')
    f.set_final('nnn')
    f.set_final('n00')
    f.set_final('0nnVega7')
    f.set_final('0nnVega8')
    f.set_final('0nnVega9')

    # initial state
    f.initial_state = 'start'
    # remove initial zeroes
    f.add_arc('start', '0**', '0', ())
    f.add_arc('0**', '00*', '0', ())
    
    for ii in xrange(10):
        #from '0n*Vega8' to '0nnVega8
        if ii != 0:
            f.add_arc('0n*Vega8+', '0nnVega8', str(ii), [kFRENCH_TRANS[ii]])
        elif ii == 0:
            f.add_arc('0n*Vega8+', '0nnVega8', str(ii), ())
        #from '0n*Vega7' to '0nnVega7' 7-9
        if ii == 0 or ii == 7 or ii ==8 or ii == 9:
            f.add_arc('0n*Vega7', '0n*Vega7+', (), [kFRENCH_TRANS[10]])
            f.add_arc('0n*Vega7+', '0n*Vega7+', str(ii), [kFRENCH_TRANS[ii]])
            #
            f.add_arc('0n*Vega9+', '0n*Vega9++', (), [kFRENCH_TRANS[10]])
            f.add_arc('0n*Vega9++', '0nnVega9', str(ii), [kFRENCH_TRANS[ii]])
    
            if ii == 0:
                f.add_arc('0n*Vega7+', '0nnVega7', '0', ())
                f.add_arc('0n*Vega9++', '0nnVega9', '0', ())
                
            elif ii == 7 or ii == 8 or ii == 9:
                f.add_arc('0n*Vega7+', '0nnVega7', str(ii), [kFRENCH_TRANS[ii]])
        #from '0n*Vega' to '0nnVega' 2-6
        if ii == 2 or ii == 3 or ii ==4 or ii == 5 or ii == 6:
            f.add_arc('0n*Vega7', '0nnVega7', str(ii), [kFRENCH_TRANS[ii+10]])
            f.add_arc('0n*Vega9+', '0nnVega9', str(ii), [kFRENCH_TRANS[ii+10]])
        if ii == 1:
            f.add_arc('0**','0n*', str(ii), [kFRENCH_TRANS[10]])
            f.add_arc('n**','0n*', str(ii), [kFRENCH_TRANS[10]])
            f.add_arc('0n*Vega7', '0n*Vega7+', str(ii), [kFRENCH_AND])
            f.add_arc('0n*Vega7+', '0nnVega7', str(ii), [kFRENCH_TRANS[ii+10]])
            f.add_arc('0n*Vega9+', '0nnVega9', str(ii), [kFRENCH_TRANS[ii+10]])
            
        #from '00*' to '00n'
        f.add_arc('00*', '00n', str(ii), [kFRENCH_TRANS[ii]])
        #from '*n*' to '*nn' 2-9
        if ii != 0 and ii !=9:
            f.add_arc('0n*','0nn', str(ii+1), [kFRENCH_TRANS[ii+1]])
            f.add_arc('0n*+','0nn', str(ii), [kFRENCH_TRANS[ii]])
        #from 'start' to 'nnn' 200,300,...,900
        if ii != 0 and ii !=1:
            f.add_arc('start','n**+', str(ii), [kFRENCH_TRANS[ii]])
            f.add_arc('n**+', 'n**', (), [kFRENCH_TRANS[100]])
        #from 'n**' to 'n0*' 0
        if ii == 0:
            f.add_arc('n**', 'n00', '00', ())
        if ii == 1:
            f.add_arc('start', 'n**', '1', [kFRENCH_TRANS[100]])

        
    #from '*n*' to '*et*' 1
    f.add_arc('0n*','*et*', '1', [kFRENCH_AND])
    #from '*et*' to '*nn' 1
    f.add_arc('*et*','0nn', (), [kFRENCH_TRANS[1]])
    #from '0**' to '*nn' 10-16 
    for ii in xrange(10,17):
        f.add_arc('0**','0nn', str(ii), [kFRENCH_TRANS[ii]])
        f.add_arc('n**','0nn', str(ii), [kFRENCH_TRANS[ii]])
    #from '0**' to '*nn' 20-60
    for ii in xrange(2,7):
        f.add_arc('0**', '0nn', str(ii*10), [kFRENCH_TRANS[ii*10]])
        f.add_arc('n**', '0nn', str(ii*10), [kFRENCH_TRANS[ii*10]])
        
        #from '0**', to *n*
        f.add_arc('0**','0n*', str(ii), [kFRENCH_TRANS[ii*10]])
        #from 'n**' to '0n*'
        f.add_arc('n**', '0n*+', str(ii), [kFRENCH_TRANS[ii*10]])
    for ii in xrange(7,10):
        if ii == 7:
            f.add_arc('0**', '0n*Vega7', str(ii), [kFRENCH_TRANS[60]])
            f.add_arc('n**', '0n*Vega7', str(ii), [kFRENCH_TRANS[60]])
        elif ii == 8:
            f.add_arc('0**', '0n*Vega8', str(ii), [kFRENCH_TRANS[4]])
            f.add_arc('n**', '0n*Vega8', str(ii), [kFRENCH_TRANS[4]])
            f.add_arc('0n*Vega8', '0n*Vega8+', (), [kFRENCH_TRANS[20]])
        elif ii == 9:
            f.add_arc('0**', '0n*Vega9', str(ii), [kFRENCH_TRANS[4]])
            f.add_arc('n**', '0n*Vega9', str(ii), [kFRENCH_TRANS[4]])
            f.add_arc('0n*Vega9', '0n*Vega9+', (), [kFRENCH_TRANS[20]])
            
    f.add_arc('n**', '0n*+', '0', ())

    return f

if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
    f = french_count()
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))

