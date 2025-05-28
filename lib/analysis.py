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
import ROOT
from utilities import *
import zdc

class Parser:
    def __init__(self, listFile, outFile, mode = 'ptrg'):
        self.listFile = listFile
        if not os.path.isfile(self.listFile):
            logger.fatal(f'list file not found: {self.listFile}')
            exit(4)

        self.outFile = outFile

        self.h1 = {}
        self.xmax = {} 
        if mode == 'ptrg':
            self.xmax = {'LG': 400, 'HG': 800}  
        elif mode == 'mip':
            self.xmax = {'LG': 1000, 'HG': 8000}
        else:
            self.xmax = {'LG': 1000, 'HG': 8000}

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

    def write(self):
        # root output
        fout = ROOT.TFile.Open(self.outFile, "recreate")
        fout.cd()
        for h in self.h1.keys():
            self.h1[h].Write()
        fout.Close()


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
    values = hist.values()  # Bin contents 
    edges = hist.axis().edges() # Bin edges
    bin_centers = (edges[:-1] + edges[1:]) / 2  

    # Step 2: Smooth the data to reduce noise
    window_length = 11  # Must be odd, adjust based on noise level
    polyorder = 2      # Polynomial order for smoothing
    smoothed_values = savgol_filter(values, window_length, polyorder)

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
    pedestal_peak_idx = peaks[bin_centers[peaks] > 100][0]
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
    bin_contents = smoothed_values[peaks_after_dip]
    mip_peak_idx = peaks_after_dip[np.argmax(bin_contents)]
    mip_x = bin_centers[mip_peak_idx]
    landau = ROOT.TF1("landau", "landau", dip_x, 7000)
    landau.SetParameters(smoothed_values[mip_peak_idx], mip_peak_x, 2*(mip_peak_x - dip_x))

    hist.Fit(landau, 'qR')

    mpv = landau.GetParameter(1)
    sigma = landau.Getparameter(2)

    return [pedestal_peak_x, mpv, sigma]
