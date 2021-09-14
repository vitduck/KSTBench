#!/usr/bin/env python3

from qe import Qe

qe = Qe(
    prefix = '../run/QE',
    input  = '../input/QE/Si_512.in')

qe.build()
qe.run()
qe.summary()
