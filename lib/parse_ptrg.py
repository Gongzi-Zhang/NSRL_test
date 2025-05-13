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

        self.pedFile = f'{dataDir}/{outputPrefix}_ped.json' 
        logger.info(f'output ped: {self.pedFile}')

        self.h1 = {}
        self.gPed = {}
        self.gPedRms = {}
        self.func = {}
        xmax = {'LG': 500, 'HG': 1000}
        for gain in {'LG', 'HG'}:
            self.func[gain] = ROOT.TF1(gain, "gaus", 0, xmax[gain])
            self.gPed[gain] = ROOT.TGraphErrors()
            self.gPedRms[gain] = ROOT.TGraph()
            for ch in range(0, zdc.config['nSiPMChannels']):
                hname = f'Ch_{ch}_{gain}'
                self.h1[hname] = ROOT.TH1F(hname, hname, 250, 0, xmax[gain])

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

            for line in fin:
                line = line.strip()
                values = line.split()
                if 6 == len(values):    
                    bd = int(values[2])
                    ch = int(values[3])
                    LG = int(values[4])
                    HG = int(values[5])
                elif 4 == len(values) or 7 == len(values):
                    bd = int(values[0])
                    ch = int(values[1])
                    LG = int(values[2])
                    HG = int(values[3])
                else:
                    logger.error(f'Invalide values in event {event}')
                    logger.info(values)
                    continue

                ch += 64*bd
                self.h1[f'Ch_{ch}_LG'].Fill(LG) 
                self.h1[f'Ch_{ch}_HG'].Fill(HG) 

    def fit(self):
        ped = {}
        for gain in {'LG', 'HG'}:
            ped[gain] = {}
            f = self.func[gain]
            ipoint = 0
            for ch in range(0, 64):
                name = f'Ch_{ch}_{gain}'
                h = self.h1[name]
                f.SetParameters(h.GetMaximum(), h.GetMean(), h.GetRMS())
                h.Fit(f, "q")
                mean = f.GetParameter(1)
                rms  = f.GetParameter(2)
                if (mean < 50):
                    logger.warning(f"low pedestal mean in channel {ch}: {mean}")

                # ped[gain][ch] = {"m": mean, "r": rms}
                ped[gain][ch] = [mean, rms]
                self.gPed[gain].SetPoint(ipoint, ch, mean)
                self.gPed[gain].SetPointError(ipoint, 0, rms)
                self.gPedRms[gain].SetPoint(ipoint, ch, rms)
                ipoint += 1

        # json output
        with open(self.pedFile, 'w') as f:
            json.dump(ped, f, indent=2, separators=(',', ': '))

        # root output
        fout = ROOT.TFile.Open(self.outFile, "recreate")
        fout.cd()
        for h in self.h1.keys():
            self.h1[h].Write()
        fout.Close()
