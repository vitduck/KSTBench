#!/usr/bin/env python3 

import re
import logging

from utils import syscmd

def cpu_info(host): 
    cpu   = {} 
    numa  = []
    lscpu = syscmd(f'ssh {host} lscpu')
    
    for line in lscpu.splitlines(): 
        if re.search('^CPU\(s\)', line): 
            cpu['CPUs'] = line.split()[-1]
        if re.search('Model name', line): 
            cpu['Model'] = ' '.join(line.split()[2:])
        if re.search('Thread\(s\)', line): 
            cpu['Threads'] = line.split()[-1]
        if re.search('^NUMA node\d+', line): 
            numa.append(line.split()[-1])
        if re.search('Flags', line): 
            avx = re.findall('(avx\w+)\s+', line)
            cpu['AVXs'] = ', '.join([flag.upper() for flag in avx])

        cpu['NUMA'] = numa
    
    print()
    logging.info('CPU')
    logging.info(f'{"Model:":<9}{cpu["Model"]}')
    logging.info(f'{"CPUs:":<9}{cpu["CPUs"]}')
    logging.info(f'{"Threads:":<9}{cpu["Threads"]}')

    for i in range(0, len(cpu['NUMA'])): 
        numa = f'NUMA {++i}:'
        logging.info(f'{numa:9}{cpu["NUMA"][i]}')

    logging.info(f'{"AVXs:":9}{cpu["AVXs"]}')
    print()