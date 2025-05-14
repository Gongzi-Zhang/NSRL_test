#!/usr/bin/env python3
# coding: utf-8

'''
parse ptrg file
    * input: ptrg_list.txt
    * output: ptrg_ped.json, ptrg_hist.root
'''

import os
import sys
import pandas as pd
import json
import ROOT
from utilities import *
import zdc

class parsePtrg:
    def __init__(self, listFile, outputPrefix, dataDir = '.'):
        self.listFile = listFile
        if not os.path.isfile(self.listFile):
            logger.fatal(f'list file not found: {self.listFile}')
            exit(4)


        self.dataDir = dataDir
        self.outFile = f'{dataDir}/{outputPrefix}_hist.root'
        logger.info(f'output hist: {self.outFile}')

        self.pedFile = f'{dataDir}/{outputPrefix}_ped.json' 
        logger.info(f'output ped: {self.pedFile}')

        self.h1 = {}
        self.func = {}
        self.xmax = {'LG': 400, 'HG': 800}
        for gain in ['LG', 'HG']:
            for ch in range(0, zdc.config['nCAENChannels']):
                hname = f'Ch_{ch}_{gain}'
                self.h1[hname] = ROOT.TH1F(hname, hname, 200, 0, self.xmax[gain])

        for bd in range(0, zdc.config['nCAENs']):
            hname = f'Bd_{bd}_rate'
            self.h1[hname] = ROOT.TH1F(hname, hname, 100, 0, 100)

        ROOT.gROOT.SetBatch(1)

    def parse(self):
        with open(self.listFile, 'r') as fin:
            ''' skip the first 9 lines '''
            for l in range(9):
                next(fin)

            ch = 0
            bd = 0
            LG = 0
            HG = 0
            TS = {}
            for bd in range(0, zdc.config['nCAENs']):
                TS[bd] = -9999e10

            for line in fin:
                ts = 0
                line = line.strip()
                values = line.split()
                if 7 == len(values) :
                    bd = int(values[0])
                    ch = int(values[1])
                    LG = int(values[2])
                    HG = int(values[3])
                    ts = float(values[4])
                elif 6 == len(values):    
                    bd = int(values[2])
                    ch = int(values[3])
                    LG = int(values[4])
                    HG = int(values[5])
                elif 4 == len(values):
                    bd = int(values[0])
                    ch = int(values[1])
                    LG = int(values[2])
                    HG = int(values[3])
                else:
                    logger.error(f'Invalide values in event {event}')
                    logger.info(values)
                    continue

                ch += 64*bd
                if 0 < LG and LG < self.xmax['LG']:
                    self.h1[f'Ch_{ch}_LG'].Fill(LG) 
                if 0 < HG and HG < self.xmax['HG']:
                    self.h1[f'Ch_{ch}_HG'].Fill(HG) 

                if (ts != 0):
                    self.h1[f'Bd_{bd}_rate'].Fill(1e6/(ts - TS[bd]))
                    TS[bd] = ts

    def fit(self):
        ped = {}
        for gain in ['LG', 'HG']:
            ped[gain] = {}
            for ch in range(0, zdc.config["nCAENChannels"]):
                name = f'Ch_{ch}_{gain}'
                h = self.h1[name]
                f = ROOT.TF1(gain, "gaus", 0, h.GetMean()+100)
                f.SetParameters(h.GetMaximum(), h.GetMean(), h.GetRMS())
                f.SetParLimits(1, 0, h.GetMean()+50)
                h.Fit(f, "qR", "", 0, h.GetMean()+100)
                mean = f.GetParameter(1)
                rms  = f.GetParameter(2)
                if (mean < 50):
                    logger.warning(f"low pedestal mean in channel {ch} {gain}: {mean}")

                # ped[gain][ch] = {"m": mean, "r": rms}
                ped[gain][ch] = [mean, rms]

        # json output
        with open(self.pedFile, 'w') as f:
            json.dump(ped, f, indent=2, separators=(',', ': '))

        # root output
        fout = ROOT.TFile.Open(self.outFile, "recreate")
        fout.cd()
        for h in self.h1.keys():
            self.h1[h].Write()
        fout.Close()
