#!/usr/bin/env python
import sys
import argparse

class LAT2FSM:
    def __init__(self):
        self.N = 0
        self.L = 0
        self.symbolMap = {}
        self.transitions = []
        self.endstates = []
        self.scalefactor = 0
    def readLattice(self, filename, eps, sent_start, sent_end):
        f = open(filename, 'r')
        for line in f:
            if line.startswith("lmscale="):
                list = line.split();
                self.scalefactor = float(list[0][8:]);
            if line.startswith('N='):
                list = line.split()
                self.N = list[0][2:]
                self.L = list[1][2:]
            if line.startswith('I='):
                list = line.split()
                I = list[0][2:]
                W = list[2][2:]
                if (eps != None and W == '!NULL'):
                    W = eps
                if (W == sent_end):
                    self.endstates.append(I)
                self.symbolMap[I] = W
            if line.startswith('J='):
                list = line.split()
                S = list[1][2:]
                E = list[2][2:]
                C = str(-1 * (float(list[3][2:]) + float(list[4][2:]) * self.scalefactor))
                self.transitions.append([S, E, self.symbolMap[E], self.symbolMap[E], C])
                # start state should be the FROM state of the first transition in finite state machine text file
                if self.symbolMap[E] == sent_start:
                    self.transitions[0], self.transitions[-1] = self.transitions[-1], self.transitions[0]

    def writeFSM(self, filename):
        f = open(filename, 'w')
        for t in self.transitions:
            for i in t:
                f.write(i + ' ')
            f.write('\n')
        for e in self.endstates:
            f.write(e + '\n')

def main():
    parser = argparse.ArgumentParser(description = "Python module that converts HTK lattice to FSM")
    parser.add_argument(dest = "lattice",
                        help = "HTK lattice")
    parser.add_argument(dest = "fsm",
                        help = "finite state machine text file")
    parser.add_argument("-e", "--eps", dest = "eps", default = "<eps>",
                        help = "use given argument as epsilon symbol (default: '<eps>')")
    parser.add_argument("-ss", "--sent_start", dest = "sent_start", default = "<s>",
                        help = "indicate the sentence start symbol in HTK lattice (default: '<s>')")
    parser.add_argument("-se", "--sent_end", dest = "sent_end", default = "</s>",
                        help = "indicate the sentence end symbol in HTK lattice (default: '</s>')")

    args = parser.parse_args()
    lat2fsm = LAT2FSM()
    lat2fsm.readLattice(args.lattice, args.eps, args.sent_start, args.sent_end)
    lat2fsm.writeFSM(args.fsm)

if __name__ == '__main__':
    main()
