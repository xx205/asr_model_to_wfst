#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

class CD2FSM:
    def __init__(self):
        # add state '<start>', 'sil' and '<end>' to self.states
        self.states = {'<start>':0, 'sil':1, '<end>':2}
        self.stateid = 3
        self.cluster = {}

    def read_monophone_file(self, filename):
        self.output_symbols = []
        monophone_file = open(filename, 'r')
        while True:
            line = monophone_file.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            monophone = line.split()[0]
            self.output_symbols.append(monophone)
            # add unigram state except 'sil' to self.states
            if not monophone in self.states and monophone != 'sil':
                self.states[monophone] = self.stateid
                self.stateid = self.stateid + 1

        monophone_file.close()
        # add bigram state p1,p2 to self.states
        for p1 in self.output_symbols:
            for p2 in self.output_symbols:
                if p1 != '<eps>' and p1 != 'sil' and p2 != '<eps>' and p2 != 'sil':
                    self.states[p1 + ',' + p2] = self.stateid
                    self.stateid = self.stateid + 1

        self.output_symbols.insert(0, '<eps>')

        output_symbols_file = open('c.outsyms', 'w')
        for i in range(0, len(self.output_symbols)):
            print >> output_symbols_file, self.output_symbols[i], i
        output_symbols_file.close()

    def read_triphone_file(self, filename):
        self.input_symbols = set([])
        triphone_file = open(filename, 'r')

        while True:
            line = triphone_file.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            triphones = line.split()

            self.cluster[triphones[0]] = triphones[-1]
            if not triphones[-1] in self.input_symbols:
                self.input_symbols.add(triphones[-1])
        triphone_file.close()

        self.input_symbols = list(self.input_symbols)
        self.input_symbols.sort()
        self.input_symbols.insert(0, '<eps>')

        input_symbols_file = open('c.insyms', 'w')
        for i in range(0, len(self.input_symbols)):
            print >> input_symbols_file, self.input_symbols[i], i
        input_symbols_file.close()

        # condition 1: '<start>' to 'sil' and 'sil' to '<end>' and 'sil' to 'sil'
        print self.states['<start>'], self.states['sil'], '<eps>', 'sil'
        print self.states['sil'], self.states['<end>'], 'sil', '<eps>'
        print self.states['sil'], self.states['sil'], 'sil', 'sil'

        # condition 2: 'sil' to other unigram states and other unigram states to 'sil'
        for p in self.output_symbols:
            if p != '<eps>' and p != 'sil':
                print self.states['sil'], self.states[p], 'sil', p
                print self.states[p], self.states['sil'], self.cluster['sil-' + p + '+sil'], 'sil'

        # condition 3: each unigram state to bigram states
        for p1 in self.output_symbols:
            for p2 in self.output_symbols: 
                if p1 != '<eps>' and p1 != 'sil' and p2 != '<eps>' and p2 != 'sil':
                    print self.states[p1], self.states[p1 + ',' + p2], self.cluster['sil-' + p1 + '+' + p2], p2

        # condition 4: each bigram state to bigram states and 'sil'
        for p1 in self.output_symbols:
            for p2 in self.output_symbols:
                if p1 != '<eps>' and p1 != 'sil' and p2 != '<eps>' and p2 != 'sil':
                    print self.states[p1 + ',' + p2], self.states['sil'], self.cluster[p1 + '-' + p2 + '+sil'], 'sil'
                    for p3 in self.output_symbols:
                        if p3 != '<eps>' and p3 != 'sil':
                            print self.states[p1 + ',' + p2], self.states[p2 + ',' + p3], self.cluster[p1 + '-' + p2 + '+' + p3], p3
                

        # condition 5: possible auxiliary loops on each states to match the auxiliary lexicon input symbols, like #phi, #1, #2, ...

        # single state in one line indicates a final state
        print self.states['<end>']
        
def main():
    cd2fsm = CD2FSM()
    cd2fsm.read_monophone_file(sys.argv[1])
    cd2fsm.read_triphone_file(sys.argv[2])

if __name__ == '__main__':
    main()
