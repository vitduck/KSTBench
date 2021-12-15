#!/usr/bin/env python3

import os 
import re
import sys
import inspect
import logging
import pprint
import packaging.version
import datetime
import prerequisite

from tabulate import tabulate
from utils    import syscmd
from cpu      import lscpu, cpu_info
from gpu      import nvidia_smi, gpu_info
from env      import module_list
from slurm    import slurm_nodelist

class Bmt: 
    version = '0.6'
    
    # initialize root logger 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '# %(message)s')

    def __init__(self, prefix='./', sif=None, nodes=0, ngpus=0, ntasks=0, omp=1):
        self.name     = ''
        self.header   = []
        self.result   = [] 

        self._bin     = ''
        self._args    = {} 
        
        self.host     = slurm_nodelist()
        self.hostfile = 'hostfile'

        self.cpu      = lscpu(self.host[0])
        self.gpu      = nvidia_smi(self.host[0])

        self.sif      = sif 

        self.prefix   = os.path.abspath(prefix)
        self.rootdir  = os.path.dirname(inspect.stack()[-1][1])
        self.bindir   = os.path.join(self.prefix, 'bin')
        self.builddir = os.path.join(self.prefix, 'build')
        self.outdir   = os.path.join(self.prefix, 'output', datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S"))
        self.input    = ''
        self.output   = ''

        self._nodes   = nodes  or len(self.host)
        self._ngpus   = ngpus  or len(self.gpu.keys())
        self._ntasks  = ntasks
        self.omp      = omp

        self.buildcmd = []
        self.runcmd   = ''
        
        # NVIDIA/NGC 
        if self.sif:
            self.sif  = os.path.abspath(self.sif)
     
    # bin decorator 
    @property 
    def bin(self): 
        return self._bin

    @bin.setter 
    def bin(self, bin): 
        self._bin = os.path.join(self.bindir, bin)
  
    # nodes decorator 
    @property 
    def nodes(self): 
        return self._nodes

    @nodes.setter 
    def nodes(self, nodes): 
        self._nodes = nodes

    # ntasks decorator 
    @property 
    def ntasks(self): 
        return self._ntasks

    @ntasks.setter 
    def ntasks(self, ntasks): 
        self._ntasks = ntasks

    # ngpus decorator
    @property 
    def ngpus(self): 
        return self._ngpus

    @ngpus.setter
    def ngpus(self, ngpus): 
        self._ngpus = ngpus 

    # override attributes with cmd line arguments
    @property 
    def args(self): 
        return self._args 

    @args.setter 
    def args(self, args): 
        self._args = args 

        for opt in args:   
            if args[opt]: 
                setattr(self, opt, args[opt]) 

    # print object attributeis for debug purpose 
    def debug(self): 
        pprint.pprint(vars(self))
    
    # check for minimum software/hardware requirements 
    def check_prerequisite(self, module, min_ver):  
        # insert hostname after ssh 
        cmd     = prerequisite.cmd[module].replace('ssh', f'ssh {self.host[0]}')
        regex   = prerequisite.regex[module]
        version = re.search(regex, syscmd(cmd)).group(1)
                
        if packaging.version.parse(version) < packaging.version.parse(min_ver):
            logging.error(f'{module} >= {min_ver} is required by {self.name}')
            sys.exit() 

    # OpenMPI: write hostfile
    def write_hostfile(self): 
        with open(self.hostfile, 'w') as fh:
            for host in self.host[0:self.nodes]:
                fh.write(f'{host} slots={self.ntasks}\n')

    # returns if previously built binary exists 
    def build(self):
        os.makedirs(self.builddir, exist_ok=True) 
        os.makedirs(self.bindir  , exist_ok=True) 

        for cmd in self.buildcmd: 
            syscmd(cmd)

    def mkoutdir(self):  
        os.makedirs(self.outdir, exist_ok=True) 
        os.chdir(self.outdir)

    def run(self, redirect=0):
        logging.info(f'{"Output":7} : {os.path.relpath(self.output, self.rootdir)}')
       
        # redirect output to file 
        if redirect: 
            syscmd(self.runcmd, self.output) 
        else: 
            syscmd(self.runcmd)

        self.parse()
    
    def parse(self):  
        pass

    def info(self): 
        cpu_info(self.cpu)
        gpu_info(self.gpu)

        module_list()

    def summary(self, sort=0, order='>'): 
        cpu_model = '' 
        gpu_model = self.gpu['0'][0]

        # Intel CPU
        if re.search('^Intel', self.cpu['Model']): 
            cpu_model = "-".join(self.cpu['Model'].split()[1:4]) 
        # AMD CPU
        else: 
            cpu_model = "-".join(self.cpu['Model'].split()[1:3]) 

        # NGC 
        if self.sif: 
            self.name = self.name + '/NGC'

        print(f'\n>> {self.name}: {" / ".join([cpu_model, gpu_model])}')

        # sort data 
        if sort:  
            if order == '>': 
                self.result =  sorted(self.result, key=lambda x : float(x[-1]), reverse=True)
            else:
                self.result =  sorted(self.result, key=lambda x : float(x[-1]))

        print(tabulate(self.result, self.header, tablefmt='psql', floatfmt='.2f', numalign='decimal', stralign='right'))
