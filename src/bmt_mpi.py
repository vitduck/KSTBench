#!/usr/bin/env python3

import argparse

from bmt import Bmt

class BmtMpi(Bmt): 
    def __init__(self, mpi=None, **kwargs):
        super().__init__(**kwargs)
        
        self.mpi          = mpi 
        self.mpi.nodelist = self.nodelist

        # set default number of node
        if not self.mpi.node: 
            self.mpi.node = len(self.nodelist)

        # cmdline options
        self.option.description += (
            '    --node           number of nodes\n'
            '    --task           number of MPI tasks per node\n' 
            '    --omp            number of OMP threads\n'
            '    --gpu            number of GPUs\n' )

    @Bmt.args.setter 
    def args(self, args): 
        self._args = args 

        for opt in args:   
            if args[opt]: 
                # Pass attributes to MPI role
                if opt == 'node' or opt == 'task' or opt == 'omp' or opt == 'gpu': 
                    setattr(self.mpi, opt, args[opt]) 
                else: 
                    setattr(self, opt, args[opt]) 

    def getopt(self): 
        self.option.add_argument('--node', type=int, metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('--task', type=int, metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('--omp' , type=int, metavar='', help=argparse.SUPPRESS)
        self.option.add_argument('--gpu' , type=int, metavar='', help=argparse.SUPPRESS)

        super().getopt() 