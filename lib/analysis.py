#!/usr/bin/env python3
# coding: utf-8

'''
Useful analysis functions:
    * parser: parse a list file
        * input: run_list.txt
        * output: run_hist.root
    * fit_ptrg
        * input: a ROOT histogram
    * fit_mip
        * input: a ROOT histogram
'''

import os
import numpy as np
from scipy.signal import savgol_filter, find_peaks
import json
import ROOT
from utilities import *
import zdc

class Parser:
    def __init__(self, listFile, outFile, pedFile = '', mode = 'ptrg'):
        self.listFile = listFile
        if not os.path.isfile(self.listFile):
            logger.fatal(f'list file not found: {self.listFile}')
            exit(4)

        self.outFile = outFile

        self.ped = {}
        for gain in ['LG', 'HG']:
            self.ped[gain] = {}
            for ch in range(0, zdc.config['nCAENChannels']):
                self.ped[gain][ch] = [0, 0]
        if mode == 'mip':
            if os.path.isfile(pedFile):
                self.ped = get_ped(pedFile)
            else:
                logger.warning('No ped file specified, use 0 value')

        self.mode = mode

        self.h1 = {}
        self.h2 = {}
        self.xmax = {} 
        if mode == 'ptrg':
            self.xmax = {'LG': 800, 'HG': 2000}  
        elif mode == 'mip':
            self.xmax = {'LG': 1000, 'HG': 8000}
        else:
            self.xmax = {'LG': 1000, 'HG': 8000}

        # 1D hist
        for ch in range(0, zdc.config['nCAENChannels']):
            for gain in ['LG', 'HG']:
                hname = f'Ch_{ch}_{gain}'
                self.h1[hname] = ROOT.TH1F(hname, hname, 200, 0, self.xmax[gain])

        # 2D hist
        if mode == 'mip':
            for ch in range(0, zdc.config['nCAENChannels']):
                hname = f'Ch_{ch}'
                self.h2[hname] = ROOT.TH2F(hname, hname, 200, 0, self.xmax['LG'], 200, 0, self.xmax['HG'])

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
                if (self.mode == 'ptrg'):
                    self.h1[f'Ch_{ch}_LG'].Fill(LG) 
                    self.h1[f'Ch_{ch}_HG'].Fill(HG) 
                elif (self.mode == 'mip'):
                    corLG = LG - self.ped['LG'][ch][0]
                    corHG = HG - self.ped['HG'][ch][0]

                    # exclude cross talk
                    if (corHG / corLG < 12):
                        continue

                    if 0 < LG and LG < self.xmax['LG']:
                        self.h1[f'Ch_{ch}_LG'].Fill(LG) 
                        if 0 < HG and HG < self.xmax['HG']:
                            self.h2[f'Ch_{ch}'].Fill(corLG, corHG)

                    if 0 < HG and HG < self.xmax['HG']:
                        self.h1[f'Ch_{ch}_HG'].Fill(HG) 

                if (ts != 0):
                    self.h1[f'Bd_{bd}_rate'].Fill(1e6/(ts - TS[bd]))
                    TS[bd] = ts

    def write(self):
        # root output
        fout = ROOT.TFile.Open(self.outFile, "recreate")
        fout.cd()
        for h in self.h1.keys():
            self.h1[h].Write()
        for h in self.h2.keys():
            self.h2[h].Write()
        fout.Close()

def get_ped(pedFile):
    with open(pedFile, 'r') as f:
        pedIn = json.load(f)

    pedOut = {}
    for gain in ['LG', 'HG']:
        pedOut[gain] = {}
        values = pedIn[gain]
        for ch, [m, r] in values.items():
            pedOut[gain][int(ch)] = [m, r]

    return pedOut


# fit a hist with a gaussian function to get the ped
def fit_ptrg(hist: ROOT.TH1F): 
    maxBin = hist.GetMaximumBin()
    mean = hist.GetBinCenter(maxBin)
    f = ROOT.TF1("fit", "gaus", 0, mean+100)
    f.SetParameters(hist.GetMaximum(), mean, hist.GetRMS())
    f.SetParLimits(1, 0, mean+50)
    hist.Fit(f, "qR", "", 0, mean+100)
    mean = f.GetParameter(1)
    rms  = f.GetParameter(2)
    return [mean, rms]



# fit a hist with a landau function to get the mip
def fit_mip(hist: ROOT.TH1F):
    name = hist.GetName()

    # Step 1: Extract bin contents and edges
    bin_centers = np.array([hist.GetBinCenter(i) for i in range(1, hist.GetNbinsX() + 1)])
    bin_values  = np.array([hist.GetBinContent(i) for i in range(1, hist.GetNbinsX() + 1)])

    # Step 2: Smooth the data to reduce noise
    window_length = 11  # Must be odd, adjust based on noise level
    polyorder = 2      # Polynomial order for smoothing
    smoothed_values = savgol_filter(bin_values, window_length, polyorder)

    # Step 3: Detect peaks in the smoothed spectrum
    peaks, properties = find_peaks(smoothed_values, prominence=1, height=1)

    # Step 4: Detect dips (local minima) between peaks
    inverted_values = -smoothed_values
    dips, _ = find_peaks(inverted_values, prominence=1)

    # Step 5: Identify the pedestal and MIP peaks
    if len(peaks) < 1:
        logger.warning(f"No peaks found in histogram {name}")
        return [0, 0, 0]

    # Pedestal peak is the highest significant peak
    pedestal_peaks = peaks[bin_centers[peaks] > 100]
    if (pedestal_peaks.size == 0):
        logger.warning(f'No pedestal peak found in histogram {name}')
        return [0, 0, 0]
    pedestal_peak_idx = pedestal_peaks[0]
    pedestal_peak_x = bin_centers[pedestal_peak_idx]

    # Find the dip closest to 2000
    if len(dips) > 0:
        dip_distances = np.abs(bin_centers[dips] - 2000)
        closest_dip_idx = dips[np.argmin(dip_distances)]  # Index of the dip closest to 2000
    else:
        logger.warning(f"No dips found in histogram {name}!")
        return [0, 0, 0]
    dip_x = bin_centers[closest_dip_idx]

    # MIP peak is the highest peak after the dip
    peaks_after_dip = peaks[peaks > closest_dip_idx]
    if (peaks_after_dip.size == 0):
        logger.warning(f'No mip peak found in histogram {name}')
        return [0, 0, 0]
    bin_contents = smoothed_values[peaks_after_dip]
    mip_peak_idx = peaks_after_dip[np.argmax(bin_contents)]
    mip_x = bin_centers[mip_peak_idx]
    landau = ROOT.TF1("landau", "landau", dip_x, 7000)
    landau.SetParameters(smoothed_values[mip_peak_idx], mip_x, 2*(mip_x - dip_x))

    hist.Fit(landau, 'qR')

    mpv = landau.GetParameter(1)
    sigma = landau.GetParameter(2)

    return [pedestal_peak_x, mpv, sigma]

# fit a 2D hist to get the HG/LG ratio
def fit_HG2LG(hist: ROOT.TH2F): 
    profile = hist.ProfileX("profileX")
    f1 = TF1("fit", "[0] + [1]*x", 0, 1000)
    f1.SetParameters(0, 30)
    profile.Fit(f1, "q R ROB=0.95")
