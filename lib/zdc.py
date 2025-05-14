import os
import json
from utilities import * 

us = 1
ms = 1e3*us
s = 1e6*us

# config
if 'ZDCROOT' not in os.environ:
    logger.fatal('ZDCROOT not set. Please source setup.sh')
    exit(4)

with open(f'{os.environ["ZDCROOT"]}/database/zdc_config.json', 'r') as f:
    config = json.load(f)

for i in range(0, config['nCAENChannels']):
    config['caen2sipm'][i] = config['caen2sipm'][str(i)]
for i in range(0, config['nSiPMChannels']):
    config['sipm2caen'][i] = config['sipm2caen'][str(i)]

config['ZDCROOT'] = os.environ['ZDCROOT']
config['ZDCBACKUP'] = os.environ['ZDCBACKUP']

def getListFile(run):
    for dir in ['.', config['ZDCROOT'], config['ZDCBACKUP']]:
        file = f'{dir}/Run{run}_list.txt'
        if os.path.exists(file):
            return file
    
    logger.warning(f"Can't find list file for run {run}")
    return ""

def getPedFile(run):
    for dir in ['.', config['ZDCROOT'], config['ZDCBACKUP']]:
        file = f'{dir}/Run{run}_ped.json'
        if os.path.exists(file):
            return file
    
    logger.warning(f"Can't find ped file for run {run}")
    return ''
