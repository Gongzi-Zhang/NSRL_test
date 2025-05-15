#!/usr/bin/env python3
import os
import sys
import sqlite3
import pandas as pd
import zdc
from utilities import *

DBName = f'{zdc.config["ZDCROOT"]}/database/NSRL_test.db'
TableName = 'Runs'
Conn = ''

FIELDS = [ 'Run', 'Type', 'Flag', 
    'StartTime', 'StopTime', 'Length', 
    'Channels', 
    # 'Beam1', 'Beam2',
    'Trigger', 'T1', 'T2',
    'Events', 'LG', 'HG', 'Ped', 'Vbias', 'Size', 
    'PedRun', 'MIPRun', 'TrgRate',
    'Note' ]
TextFields = ['Type', 'Flag', 'StartTime', 'StopTime', 'Size', 'Note']
FreFields = [ 'Run', 'Type', 'Flag', 
    'StartTime', 'StopTime', 'Length', 
    'Trigger', 
    'Events', 'Size', 
    'Note' ]
TYPES = ['ptrg', 'mip', 'cosmic', 'data', 'cmdata', 'test', 'junk']
FLAGS = ['good', 'bad', 'susp']

FIELD_WIDTH = {
    'Run': 4, 
    'Type': 6, 
    'Flag': 4,
    'StartTime': 16, 
    'StopTime': 16, 
    'Length': 5,    # elapsed time in h
    'Channels': 3,  # number of good channels
    # 'Beam1': 6,
    # 'Beam2': 6,
    'Trigger': 3,   # trigger logic
    'T1': 5,        # in V
    'T2': 5,
    'Events': 7,    # number of events
    'LG': 2,
    'HG': 2,
    'Ped': 3,
    'Size':   4,    # raw data file size in GB
    'PedRun': 4,
    'MIPRun': 4,
    'TrgRate': 8,   # in MHz
    'Note': 30, 
    }

FIELD_TITLE = {
    'Length':   'Len',
    'Channels': 'Chs',
    'Trigger':  'Trg',
    'PedRun': 'PRun',
    'MIPRun': 'MRun'
    }

formatted = True

def setFormat(f):
    global formatted
    formatted = f
    logger.debug(f'Formatted output: {formatted}')

def checkField(field):
    if field in FIELDS:
        return True
    logger.error(f'''unknown field '{field}'. Allowed fields: {FIELDS}''')
    return False

def checkValue(field, value):
    if 'Type' == field:
        if value in TYPES:
            return True
        else:
            logger.error(f'Invalid run type: {value}. Allowed types: {TYPES}')
    elif 'Channels' == field:
        if 1 <= value and value <= 300:
            return True
        else:
            logger.error(f'Invalid channel number: {value}. Allowed range [1, 300]')

    return False

''' create a database connection to a SQLite database '''
def createConnection(db_file):
    global Conn
    if Conn:
        return True

    try:
        Conn = sqlite3.connect(db_file)
        logger.debug(f'connect to sqlite db: {db_file}')
    except sqlite3.Error as e:
        print(e)
        return False
    return True

def closeConnection():
    if not Conn:
        return

    logger.debug(f'close connection to sqlite db: {DBName}')
    Conn.close()

''' execute the sql statement. Return a cursor object '''
def executeSql(sql, values=None):
    try:
        c = Conn.cursor()
        if values is None:
            return c.execute(sql)
        else:
            return c.execute(sql, values)
    except sqlite3.Error as e:
        print(e)
        return None

''' query table existance in the db '''
def queryTable(table):
    sql = f'''SELECT name FROM sqlite_master WHERE type='table' AND name = '{table}';'''
    logger.debug(sql)
    result = executeSql(sql)
    if result.fetchone():
        return True
    else:
        return False

''' formatted output '''
def printSepLine(fields):
    line = '+'
    for f in fields:
        width = len(f)
        if f in FIELD_WIDTH:
            width = FIELD_WIDTH[f]
        line += '-'*(width+2)
        line += '+'
    print(line)

def printHeader(fields):
    header = '|'
    for f in fields:
        width = len(f)
        if f in FIELD_WIDTH:
            width = FIELD_WIDTH[f]
        if f in FIELD_TITLE:
            f = FIELD_TITLE[f]
        header += ' {value:<{width}} '.format(value=f, width=width)
        header += '|'
    print(header)

def printRecord(record):
    if not record:
        return

    row = '|'
    for f in record:
        width = len(f)
        if f in FIELD_WIDTH:
            width = FIELD_WIDTH[f]
        row += ' {value:<{width}} '.format(value=str(record[f]), width=width)
        row += '|'
    print(row)

''' print query results '''
def showQuery(cursor):
    if not cursor:
        return False

    fields = [des[0] for des in cursor.description]

    if formatted:
        printSepLine(fields)
        printHeader(fields)
        printSepLine(fields)
        for row in cursor.fetchall():
            printRecord(dict(zip(fields, row)))
            printSepLine(fields)
    else:
        for row in cursor.fetchall():
            for i in range(0, len(row)):
                print(f'{row[i]}', end='\t')
            print()

    return True

''' show all tables in the db '''
def showTables():
    sql = f'''SELECT name AS tables FROM sqlite_master WHERE type='table';'''
    logger.debug(sql)
    result = executeSql(sql)
    showQuery(result)

''' drop a table '''
def dropTable(table):
    if not queryTable(table):
        print(f'''table '{table}' doesn't exist''')
        return False
    yesno = input(f'''are you sure you want to drop table '{table}': y[es], n[o]\n''')
    if 'y' == yesno:
        yesno2 = input(f'''confirm dropping table '{table}': y[es], n[o]\n''')
        if 'y' == yesno2:
            sql = f'''DROP TABLE IF EXISTS {table};'''
            logger.debug(sql)
            if executeSql(sql):
                Conn.commit()
                return True
        else:
            print('cancel dropping')
            return False
    else:
        print('cancel dropping')
        return False

''' table specific '''
''' create a new table '''
def createTable():
    sql = f''' CREATE TABLE IF NOT EXISTS {TableName} (
                Run integer PRIMARY KEY,
                Type text,
                Flag text,
                StartTime text,
                StopTime text,
                Length integer,
                Channels integer,
                Trigger integer,
                T1 float,
                T2 float,
                Events integer,
                LG integer,
                HG integer,
                Ped integer,
                Vbias float,
                Size integer,
                PedRun integer,
                MIPRun integer,
                TrgRate float,
                Note text
            );'''
    logger.debug(sql)
    if not executeSql(sql):
        return False
    Conn.commit()
    return True

''' query data in the table: return all records as a list'''
def queryRecords(conditions='1=1', col="*"):
    sql = f'''SELECT {col} FROM {TableName} WHERE {conditions};'''
    logger.debug(sql)
    return executeSql(sql)

def insertRecord(record):
    if 'Run' in record:
        result = queryRecords(f"Run={record['Run']}")
        if result.fetchone():
            logger.warning(f'''record for Run={record['Run']} already exist, will skip it''')
            printRecord(record)
            return False

    valid = True
    for f in ('Type', 'Channels'):
        if f in record:
            valid &= checkValue(f, record[f])
    if not valid:
        logger.error(f'invalid value in the following record, will not insert it')
        print(record)
        return False

    columns = ', '.join(record.keys())
    placeholders = ':' + ', :'.join(record.keys())
    sql = f'''INSERT INTO {TableName}({columns}) VALUES({placeholders});'''
    logger.debug(sql)
    executeSql(sql, record)
    Conn.commit()

    return True

''' insert records from a csv file to a table '''
def insertRecords(filename):
    if not os.path.exists(filename):
        logger.error(f'file does not exist: {filename}')
        return False
    for i, row in pd.read_csv(filename).iterrows():
        insertRecord(row.to_dict())
    return True

''' update a record in the table '''
def updateRecord(kvalue, field, value):
    if field == 'Run':
        logger.warning("Can't update primary key: Run")
        return False
    if field in TextFields:
        sql = f'''UPDATE {TableName} SET {field} = '{value}' WHERE Run = {kvalue};'''
    else:
        sql = f'''UPDATE {TableName} SET {field} = {value} WHERE Run = {kvalue};'''
    logger.debug(sql)
    if executeSql(sql):
        Conn.commit()
        return True

''' delete a record in a table using primary key values '''
def deleteRecord(kvalue):
    conditions = f'Run = {kvalue}'
    result = queryRecords(conditions)
    if not result:
        print('WARNING\tindicated record does not exist in table {TableName}')
        return False
    showQuery(result)
    yesno = input(f'''are you sure you want to delete above record in table '{TableName}': y[es], n[o]\n''')
    if 'y' == yesno:
        yesno2 = input(f'confirm deleting record (Run = {kvalue}) in table {TableName}: y[es], n[o]\n')
        if 'y' == yesno2:
            sql = f'DELETE FROM {TableName} WHERE Run = {kvalue};'
            logger.debug(sql)
            if executeSql(sql):
                logger.info('successfully delete the record')
                Conn.commit()
                return True
        else:
            print('cancel deletion')
            return False
    else:
        print('cancel deletion')
        return False

''' insert records to a table '''
def insertToTable():
    mode = int(input('please select the insert mode: 1 [csv file], 2 [manual input]\n'))
    if 1 == mode:
        filename = input('please input the file path: ')
        if not insertRecords(filename):
            return False
    elif 2 == mode:
        print(f'''please input the following fields for table '{TableName}':''')
        values = {}
        values['Run'] = int(input('Run number: '))
        values['Type'] = input(f'Type {TYPES}: ').strip() or 'data'
        values['Flag'] = input(f'Flag {FLAGS}: ').strip() or 'good'
        values['StartTime'] = input('StartTime: ').strip()
        values['StopTime'] = input('StopTime: ').strip()
        values['Length'] = float(input('Length/h: '))
        values['Channels'] = int(input('#Channels: '))
        # values['Beam1'] = float(input('Beam1: ') or 100)
        # values['Beam2'] = float(input('Beam2: ') or 100)
        values['Trigger'] = int(input('Trigger Logic: '))
        values['T1'] = float(input('T1: ') or 0.005)
        values['T2'] = float(input('T2: ') or 0.005)
        values['Events'] = int(input('#Events: '))
        values['Size'] = input('Size: ').strip()
        values['LG'] = int(input('LG: ') or 30)
        values['HG'] = int(input('HG: ') or 55)
        values['Ped'] = int(input('Ped: ') or 160)
        values['PedRun'] = int(input('PedRun: '))
        values['MIPRun'] = int(input('MIPRun: '))
        values['TrgRate'] = float(input('TrgRate: '))
        values['Note'] = input('Note: ').strip()
        if not insertRecord(values):
            return False
    else:
        logger.error(f'unrecognised mode {mode}')
        return False
    return True

''' update a record in the table '''
def update():
    kvalue = int(input(f'select the record `Run` that you want to update: '))
    conditions = f'Run = {kvalue}'
    result = queryRecords(conditions)
    if not result.fetchone():
        logger.error(f'''indicated record (Run = {kvalue}) does not exist in table '{TableName}' ''')
        return False

    print('record before updating:')
    showQuery(queryRecords(conditions))

    field_prompt = f'0[quit]'
    for i in range(1, len(FIELDS)):
        field_prompt += f', {i}[{FIELDS[i]}]'
    index = int(input(f'which field you want to update: {field_prompt}: '))
    if index < 0 or index >= len(FIELDS):
        logger.error(f'invalid index {index}')
        return False
    if index == 0:
        print(f'quit the update')
        return True
    field = FIELDS[index]
    value = input(f'''updated value for {field}: ''')
    updateRecord(kvalue, field, value)

    print('record after updating:')
    showQuery(queryRecords(conditions))

def exportRecords(fname):
    if os.path.exists(fname):
        logger.error(f'{fname} already exists, please backup it')
        return False
    db_df = pd.read_sql_query(f'SELECT * from {TableName};', Conn)
    db_df.to_csv(fname, index=False)
    return True

''' use the function carefully '''
def doQuery():
    sql = input('input the sql query: ').strip()
    showQuery(executeSql(sql))

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


if __name__ == '__main__':
    if not createConnection(DBName):
        print('Error! cannot create the database connection.')
        exit()

    ''' command loop '''
    command = None
    while command != 'q':
        line = input('c[reate table], S[how tables], s[how], i[nsert], u[pdate], e[xport to csv], d[elete record], E[xecute query], D[rop table], q[uit]\n').strip()
        val = line.split()
        command = val[0]

        if command == 'c':
            createTable()
        elif command == 'S':
            showTables()
        elif command == 's':
            showQuery(queryRecords())
        elif command == 'i':
            insertToTable()
        elif command == 'u':
            update()
        elif command == 'e':
            fname = input('what is the output file name: ')
            exportRecords(fname)
        elif command == 'd':
            kvalue = int(input('input the Run you want to delete: '))
            deleteRecord(kvalue)
        elif command == 'E':
            doQuery()
        elif command == 'D':
            dropTable(TableName)

    closeConnection()
