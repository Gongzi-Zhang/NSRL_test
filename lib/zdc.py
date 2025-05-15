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

def getFile(f):
    for dir in ['.', config['ZDCROOT'], config['ZDCBACKUP']]:
        file = f'{dir}/{f}'
        if os.path.exists(file):
            return file
    
    logger.warning(f"Can't find file {f}")
    return ""
