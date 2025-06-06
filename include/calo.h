#ifndef __CALO__
#define __CALO__

#include <iostream>
#include <vector>
#include "utilities.h"

// units
const float us = 1;
const float ms = 1e3*us;
const float s = 1e6*us;

const float mm = 1;
const float cm = 10*mm;
const float m = 100*cm;

const float GeV = 1;
const float MeV = 1e-3*GeV;

namespace calo {
    const char* gains[] = {"LG", "HG"};

    int nCAENs = 9;
    int nChannels = 576;
    std::vector<int> nCAENChannels = {64, 64, 64, 64, 64, 64, 64, 64, 64};	// number of channels in each CAEN unit
    std::vector<int> preChannels = {0, 64, 128, 192, 256, 320, 384, 448, 512};	// number of channels before this CAEN unit

    void setnCAENChannels(std::vector<int> nCh)
    {
	nCAENs = nCh.size();
	if (!nCAENs)
	{
	    std::cerr << WARNING << "empty value for number of channels in each CAEN unit" << std::endl;
	    return;
	}
	nCAENChannels.clear();
	preChannels.clear();
	nCAENChannels = nCh;
	preChannels = std::vector<int> (nCAENs, 0);
	nChannels = nCh[0];

	for (int i=1; i<nCAENs; i++)
	{
	    nChannels += nCh[i];
	    preChannels[i] = preChannels[i-1] + nCh[i-1];
	}
    }
}

#endif
