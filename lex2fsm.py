#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

class LEX2FSM:
    def __init__(self):
        self.phones_to_words = {}
        self.multiplicity = 0
        # Special states have pre-allocated ids:
        # 0 denotes to initial state, 1 denotes to final state
        self.stateid = 2
        self.add_aux_phones = False

    def read_monolist_file(self, filename):
        self.input_symbols = set([])

        monolist_file = open(filename, 'r')
        while True:
            line = monolist_file.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            monophone = line.split()[0]
            if not monophone in self.input_symbols:
                self.input_symbols.add(monophone)
        monolist_file.close()

        
        self.input_symbols = list(self.input_symbols)
        self.input_symbols.sort()
        self.input_symbols.insert(0, '<eps>')

        # add special symbol for class
        self.input_symbols.append('<spe>')

        if self.add_aux_phones:
            for i in range(0, self.multiplicity):
                self.input_symbols.append('#' + str(i))
            self.input_symbols.append('#phi')

        input_symbols_file = open('l.insyms', 'w')
        for i in range(0, len(self.input_symbols)):
            print >> input_symbols_file, self.input_symbols[i], i
        input_symbols_file.close()

    def read_lexicon_file(self, filename):
        self.output_symbols = set([])

        lexfile = open(filename, 'r')
        while True:
            line = lexfile.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            lexitem = line.split()
            word = lexitem[0]
            # add unseen word to output symbols
            if not word in self.output_symbols:
                self.output_symbols.add(word)

            phones = ' '.join(lexitem[1:])
            if not phones in self.phones_to_words:
                self.phones_to_words[phones] = [word]
            else:
                self.phones_to_words[phones].append(word)

        for v in self.phones_to_words.values():
            if len(v) > self.multiplicity:
                self.multiplicity = len(v)

        for k, v in self.phones_to_words.items():
            for i in range(0, len(v)):
                phones = k.split()
                # start state is 0
                state_list = [0]
                state_list = state_list + range(self.stateid, self.stateid + len(phones) - 1)
                self.stateid = self.stateid + len(phones) - 1
                if self.add_aux_phones:
                    state_list.append(self.stateid)
                    self.stateid = self.stateid + 1
                    phones.append('#' + str(i))
                # end state is 1
                state_list.append(1)
                word = v[i]
                for j in range(0, len(state_list) - 1):
                    if j > 0:
                        word = '<eps>'
                    print state_list[j], state_list[j + 1], phones[j], word

        # single state in one line indicates a final state
        if self.add_aux_phones:
            print 0, 0, '#phi', '#phi'
        print 1
        lexfile.close()

        self.output_symbols = list(self.output_symbols)
        self.output_symbols.sort()
        self.output_symbols.insert(0, '<eps>')
        if self.add_aux_phones:
            self.output_symbols.append('#phi')

        output_symbols_file = open('l.outsyms', 'w')
        for i in range(0, len(self.output_symbols)):
            print >> output_symbols_file, self.output_symbols[i], i
        output_symbols_file.close()

def main():
    lex2fsm = LEX2FSM()
    lex2fsm.read_lexicon_file(sys.argv[1])
    lex2fsm.read_monolist_file(sys.argv[2])

if __name__ == '__main__':
    main()
