import os
import json
from utilities import * 
from db import *

# config
if 'ZDCROOT' not in os.environ:
    logger.fatal('ZDCROOT not set. Please source setup.sh')
    exit(4)

with open('zdc_config.json', 'r') as f:
    config = json.load(f)

for i in range(0, config['nCAENChannels']):
    config['caen2sipm'][i] = config['caen2sipm'][str(i)]
for i in range(0, config['nSiPMChannels']):
    config['sipm2caen'][i] = config['sipm2caen'][str(i)]

config['ZDCROOT'] = os.environ['ZDCROOT']
config['ZDCBACKUP'] = os.environ['ZDCBACKUP']

# database
class DB:
    def __init__(self):
        createConnection(DBName)

    def query(self, cond, fields="Run"):
        # !!! check fields !!!
        sql = f'''SELECT {fields} FROM {TableName} WHERE {cond};'''
        cursor = executeSql(sql)
        rows = cursor.fetchall()
        if rows is None:
            logger.error(f'no result from the query: {sql}, please check it')
            return False

        result = {column[0]: [] for column in cursor.description}
        for row in rows:
            for idx, column in enumerate(cursor.description):
                result[column[0]].append(row[idx])

        return result

    def getRunValue(self, run, field):
        cond = f'Run = {run}'
        values = self.query(cond, field)
        if values:
            return values[field][0]
        else:
            return False
        
    def getRunType(self, run):
        return self.getRunValue(run, 'Type')

    def getRunFlag(self, run):
        return self.getRunValue(run, 'Flag')

    def getRunPedRun(self, run):
        return int(self.getRunValue(run, 'PedRun'))

    def getRunStartTime(self, run):
        return self.getRunValue(run, 'StartTime')

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


# test
if __name__ == '__main__':
    ''' test '''
    db = DB()
    run = 200
    logger.info(f'run {run} has type of: {db.getRunType(run)}')
    logger.info(f'run {run} has flag of: {db.getRunFlag(run)}')
    logger.info(f'run {run} has ped run of: {db.getRunPedRun(run)}')
