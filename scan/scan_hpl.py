#!/usr/bin/env python3 

from hpl import Hpl

hpl = Hpl(
    prefix    = '../run/HPL',
    sif       = '../image/hpc-benchmarks:21.4-hpl.sif',
    blocksize = ['256'] ) 

hpl.info()

for nodes in [1]: 
    for ngpus in [1, 2, 4, 6, 8]:
        for omp in [1, 2, 4]: 
            hpl.nodes = nodes
            hpl.ngpus = ngpus
            hpl.omp   = omp
        
            hpl.run() 

hpl.summary()
