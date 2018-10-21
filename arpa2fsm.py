#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import math

class ARPA2FSM:
    def __init__(self):
        # Special states have pre-allocated ids:
        # 1: initial state, 0: backoff state for unigram
        # 2: entrance state '<s>’, 3: exit state '</s>', 
        self.states = {'<start>':1, '<eps>':0, '</s>':3, '<s>':2}
        self.stateid = 4
        self.ngramcount = {}
        self.add_aux_phones = True

    def read_lexicon_file(self, filename):
        self.output_symbols = set([])

        lexicon_file = open(filename, 'r')
        while True:
            line = lexicon_file.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            word = line.split()[0]
            self.output_symbols.add(word)
        lexicon_file.close()

        self.output_symbols = list(self.output_symbols)
        self.output_symbols.sort()
        self.output_symbols.insert(0, '<eps>')

        self.input_symbols = list(self.output_symbols)
        if self.add_aux_phones:
            self.input_symbols.append('#phi')

        input_symbols_file = open('g.insyms', 'w')
        for i in range(0, len(self.input_symbols)):
            print >> input_symbols_file, self.input_symbols[i], i
        input_symbols_file.close()

        output_symbols_file = open('g.outsyms', 'w')
        for i in range(0, len(self.output_symbols)):
            print >> output_symbols_file, self.output_symbols[i], i
        output_symbols_file.close()

        self.output_symbols = set(self.output_symbols)
        
    def add_default_backoff_path(self, state):
        # The state is at least a bigram state (since it is not found),
        # otherwise the state is a unigram state or unigram backoff state, 
        # which implies the ARPA format file is ill-formed
        if state.find(',') != -1:
            bo = state[state.find(',') + 1:]
            if not bo in self.states:
                self.states[bo] = self.stateid
                self.stateid = self.stateid + 1
                if self.add_aux_phones:
                    print self.states[state], self.states[bo], '#phi', '<eps>', 0
                else:
                    print self.states[state], self.states[bo], '<eps>', '<eps>', 0
                self.add_default_backoff_path(bo)
            else:
                if self.add_aux_phones:
                    print self.states[state], self.states[bo], '#phi', '<eps>', 0
                else:
                    print self.states[state], self.states[bo], '<eps>', '<eps>', 0

    def read_arpa_file(self, filename):
        arpa_file = open(filename, 'r')
        order = 0
        # first state in the first line indicates initial state
        print self.states['<start>'], self.states['<s>'], '<s>', '<s>', 0
        while True:
            line = arpa_file.readline()
            if not line:
                print >> sys.stderr, 'Ill-formed ARPA format file: no \\end\\ keyword found'
                break
            line = line.strip()
            if not line:
                continue
            if line.startswith('\\data\\'):
                continue
            if line.startswith('ngram'):
                nc = map(lambda x:int(x), line.split()[1].split('='))
                self.ngramcount[nc[0]] = nc[1]
                continue
            if line.endswith('grams:'):
                order = int(line[1:line.find('-')])
                continue
            if line.startswith('\\end\\'):
                break

            ngramitem = line.split()
            # reject OOV words
            oov = False
            for word in ngramitem[1:order + 1]:
                if not word in self.output_symbols:
                    oov = True
                    break
            if oov == True:
                continue

            prob = float(ngramitem[0]) * math.log(10) * -1
            backoffprob = 0
            if len(ngramitem) == order + 2:
                backoffprob = float(ngramitem[order + 1]) * math.log(10) * -1

            if order == 1:
                prev = '<eps>'
                next = ngramitem[1]
                bo = '<eps>'
                # '</s>' is added to self.states
                if not next in self.states:
                    self.states[next] = self.stateid
                    self.stateid = self.stateid + 1
                if next != '<s>':
                    print self.states[prev], self.states[next], ngramitem[order], ngramitem[order], prob
                if next != '</s>':
                    if self.add_aux_phones:
                        print self.states[next], self.states[bo], '#phi', '<eps>', backoffprob
                    else:
                        print self.states[next], self.states[bo], '<eps>', '<eps>', backoffprob

            elif order > 1 and order < len(self.ngramcount):
                prev = ','.join(ngramitem[1:order])
                if ngramitem[order] == '</s>':
                    next = '</s>'
                else:
                    next = prev + ',' + ngramitem[order]
                bo = ','.join(ngramitem[2:order + 1])
                if not prev in self.states:
                    self.states[prev] = self.stateid
                    self.stateid = self.stateid + 1
                if not next in self.states:
                    self.states[next] = self.stateid
                    self.stateid = self.stateid + 1

                # if bo is not represented in self.states yet, then
                if not bo in self.states:
                    self.states[bo] = self.stateid
                    self.stateid = self.stateid + 1
                    self.add_default_backoff_path(bo)
                    
                if self.add_aux_phones:
                    print self.states[next], self.states[bo], '#phi', '<eps>', backoffprob
                else:
                    print self.states[next], self.states[bo], '<eps>', '<eps>', backoffprob
                
                print self.states[prev], self.states[next], ngramitem[order], ngramitem[order], prob

            else:
                prev = ','.join(ngramitem[1:order])
                if ngramitem[order] == '</s>':
                    next = '</s>'
                else:
                    next = ','.join(ngramitem[2:order + 1])
                if not prev in self.states:
                    self.states[prev] = self.stateid
                    self.stateid = self.stateid + 1
                if not next in self.states:
                    self.states[next] = self.stateid
                    self.stateid = self.stateid + 1
                    self.add_default_backoff_path(next)
                print self.states[prev], self.states[next], ngramitem[order], ngramitem[order], prob
        # single state in one line indicates a final state
        print self.states['</s>']
        arpa_file.close()

def main():
    arpa2fsm = ARPA2FSM()
    arpa2fsm.read_lexicon_file(sys.argv[1])
    arpa2fsm.read_arpa_file(sys.argv[2])

if __name__ == '__main__':
    main()
