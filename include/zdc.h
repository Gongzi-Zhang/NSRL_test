/* const information about the prototype and run */
#ifndef __zdc__
#define __zdc__

#include <iostream>
#include <vector>
#include <map>
#include <cmath>
#include <stdlib.h>
#include <cassert>
#include "calo.h"
#include "utilities.h"

using namespace std;

namespace zdc {
    const char* ZDCROOT = (assert(getenv("ZDCROOT") != NULL), true)
	? getenv("ZDCROOT")
	: ".";
    const char* ZDCBACKUP = "/media/arratialab/zdc/NSRL_test/";

    // Run 2024
    const char* run24Start	= "2024-04-24";
    const char* run24End	= "2024-10-21";
    const char* run24PPStart	= "2024-04-24";
    const char* run24PPEnd	= "2024-09-30";
    const char* run24AuAuStart	= "2024-10-05";
    const char* run24AuAuEnd	= "2024-10-21";
    const int   run24StartRun	= 12;
    const int	run24EndRun	= 2587;
    const int	run24PPStartRun = 12;
    const int	run24PPEndRun	= 2235;
    const int   run24AuAuStartRun = 2324;
    const int   run24AuAuEndRun	= 2587;

	  int   run = 1000;

    // Trigger
    map<int, const char*> trigger = 
    {
	{-2,	"mip"}, 
	{-1,	"ptrg"},
	{0,	"others"},
	{1,	"T1"},	{16,	"T1"},
	{2,	"T2"},	{32,	"T2"},
	{4,	"T3"},	{64,	"T3"},
	{8,	"T4"},  {128,	"T4"},
	{3,	"T1 && T2"},
	{5,	"T1 && T3"},
	{6,	"T2 && T3"},
	{7,	"T1 && T2 && T3"},
	{12,	"T3 && T4"},
	{28,	"T1 || (T3 && T4)"},
	{48,	"T1 || T2"},
	{60,	"T1 || T2 || (T3 && T4)"},
	{67,	"(T1 && T2) || T3"},
	{112,	"T1 || T2 || T3"},
	{131,	"(T1 && T2) || T4"},
	{240,	"T1 && T2 && T3 && T4"},
    };

    // geometry and channels
    /* CAEN:	  CAEN unit
     * channel:   channel count: 0-192
     * layer:	  sampling layers
     * board:	  PCB count: 0-44
     * quadrant:  quadrant count in a layer: 0-3
     * sipm:      SiPM count in a PCB: 0-6
     */
    	  int nCAENs = 3;
    const int CAENMax = 5;
    const int nCAENChannels = 64;
	  int nChannels = nCAENs*nCAENChannels;
          int nLayers = 10;
    const int layerMax = 20;
	  int nHexLayers = 4;
    const int transLayer = 4;	// Layer 5
	  int nSqaLayers = 9;
    const int nLayerBoards = 4;
          int nHexBoards = nHexLayers*nLayerBoards;
          int nSqaBoards = nSqaLayers*nLayerBoards;
	  int nBoards = nHexBoards + nSqaBoards;
    const int boardMax = 80;
    const int nHexBoardChannels = 7;
    const int nSqaBoardChannels = 4;
          int nHexChannels = nHexBoards*nHexBoardChannels;
          int nSqaChannels = nSqaBoards*nSqaBoardChannels;

    const int nEightLayerBoards = 8*nLayerBoards;
    const int nNineLayerBoards  = 9*nLayerBoards;
    const int channelMax = 300;

    const float x0 = 65*cm;
    const float y0 = 0;
    const float z0 = 800*cm;
    const float xw = 192*mm;
    const float yw = 194*mm;
    const float lt = 24.5*mm;    // layer thickness
    const float xmin = x0 - xw/2;
    const float xmax = x0 + xw/2;
    const float ymin = y0 - yw/2;
    const float ymax = y0 + yw/2;
    const float zmax = z0 + nLayers*lt;
    const float etamin = 0.5*log(1 + 4*z0*z0/(xmax*xmax));
    const float etamax = 0.5*log(1 + 4*z0*z0/(xmin*xmin));

    const float gapX = 0*mm;
    const float gapY = 2.54*mm;	// 0.1 in
    const float pcbX = 96*mm;	// simulation value; real value: 177.64 - 45.72
    const float pcbY = 97*mm;	// simulation value; real value: 130.91 - 32.92

    // run dependent info
    void setRun(const int r)
    {
	run = r;
	if (run < 3)
	{
	    nCAENs = 1;
	    nChannels = 56;
	    nHexLayers = 2;
	    nHexBoards = 8;
	    nHexChannels = 56;
	    nSqaLayers = 0;
	    nSqaBoards = 0;
	    nSqaChannels = 0;
	    calo::setnCAENChannels({56});
	}
	else if (run < 4)
	{
	    nCAENs = 3;
	    nChannels = 176;
	    nHexLayers = 4;
	    nHexBoards = 16;
	    nHexChannels = 112;
	    nSqaLayers = 4;
	    nSqaBoards = 16;
	    nSqaChannels = 64;
	    calo::setnCAENChannels({64, 64, 48});
	}
	else
	{
            nCAENs = 3;
	    nChannels = 192;
	    nHexLayers = 4;
	    nHexBoards = 16;
	    nHexChannels = 112;
	    nSqaLayers = 6;
	    nSqaBoards = 20;
	    nSqaChannels = 80;
	    calo::setnCAENChannels({64, 64, 64});
	}
    }

    typedef struct {
	int layer;	// starts from 0
	int quadrant;	// 0-3
	int sipm;	// 0-3 or 0-6
    } SiPM;

    struct sipmXY{
	float x, y;
	
	inline void   operator=(sipmXY a)   { x=a.x; y=a.y; }
	inline sipmXY operator-()	    { return {-x, -y}; }
	inline sipmXY operator-(sipmXY a)   { return {x-a.x, y-a.y}; }
	inline sipmXY operator+(sipmXY a)   { return {x+a.x, y+a.y}; }
	inline bool   operator==(sipmXY a)  { return (x == a.x) && (y == a.y); }
    };

    int boardLabel[][nLayerBoards] = {
    // top right, top left, bottom left, bottom right
	{ 1,  2,  3,  4},   // hexagon
	{ 5,  6,  7,  8},   // hexagon
	{10,  9, 11, 12},   // hexagon
	{26, 13, 25, 28},   // hexagon
	{30, 41, 14, 37},   // transition: top 2 square, bottom 2 hexagon
	{38, 54, 21, 18},   // square
	{44, 22, 58, 47},   // square
	{50, 57, 33, 31},   // square
	{ 0, 15, 46, 24},   // square, the bottom right board number is unknown, guess it to be 24
	{ 0, 20, 45, 36},   // square
	{42, 49, 23, 16},   // square
	{17, 52, 19, 51},   // square
	{55, 43, 32, 39},   // square
	{34, 56, 35, 59},   // sauqre
	{ 0,  0,  0, 29},   // sauqre
    };

    // left right PCBs are rotated w.r.t. each other
    sipmXY pcbAnchor[] = {
	{-gapX/2, gapY/2 + pcbY},   // top right PCB, anchor at top left point
	{ gapX/2, gapY/2},	    // top left PCB, anchor at top bottom right point
	{ gapX/2, -(gapY/2 + pcbY)},	// bottom left PCB, anchor at bottom right point
	{-gapX/2, -gapY/2},	    // bottom right PCB, anchor at top left point
    };
					    
    sipmXY hexBoardSipmXY[nHexBoardChannels] = {
	{50.01*mm, 80.90*mm},
	{77.64*mm, 64.95*mm},
	{22.37*mm, 64.95*mm},
	{50.01*mm, 48.99*mm},
	{77.64*mm, 33.04*mm},
	{22.37*mm, 33.04*mm},
	{50.01*mm, 17.08*mm},
    };
    sipmXY sqaBoardSipmXY[nSqaBoardChannels] = {
	{73.9*mm, 72.89*mm},
	{26.1*mm, 72.89*mm},
	{73.9*mm, 25.09*mm},
	{26.1*mm, 25.09*mm},
    };
    sipmXY hexBoardSipmXY_topdown[nHexBoardChannels] = {
	{50.01*mm, 80.90*mm},
	{22.37*mm, 64.95*mm},
	{77.64*mm, 64.95*mm},
	{50.01*mm, 48.99*mm},
	{77.64*mm, 33.04*mm},
	{22.37*mm, 33.04*mm},
	{50.01*mm, 17.08*mm},
    };
    sipmXY sqaBoardSipmXY_topdown[nSqaBoardChannels] = {
	{26.1*mm, 72.89*mm},
	{73.9*mm, 72.89*mm},
	{26.1*mm, 25.09*mm},
	{73.9*mm, 25.09*mm},
    };

    SiPM getSipm(const int ch)
    {
	if (ch < 0 || ch >= nChannels)
	{
	    cerr << ERROR << "Invalid channel number:" << ch << endl;
	    cout << INFO << "Allowed channel range: 0 - " << nChannels - 1 << endl;
	    return {-1, -1, -1};
	}

	SiPM re;
	int restCh = 0;
	int board = -1;
	int sipm = -1;
	if (ch < nHexChannels)
	{
	    board = ch / nHexBoardChannels;
	    sipm = ch % nHexBoardChannels;
	}
	else 
	{
	    restCh = ch - nHexChannels;
	    board = nHexBoards + restCh / nSqaBoardChannels;
	    sipm = restCh % nSqaBoardChannels;

	    if (board >= nEightLayerBoards)
		board += 1;
	    if (board >= nNineLayerBoards)
		board += 1;

            // special cases
	    if (run < 265) 
	    {	
		if (board == 37)
		    board = 40;
	    }
	}

	re.layer = board / nLayerBoards;
	re.quadrant = board % nLayerBoards;
	re.sipm = sipm;

	return re;
    }

    sipmXY getSipmXY(const int ch)
    {
	/*  Top down channel number
	 *  Hexagonal tiles
	 *  Right: top middle - up left - up right - middle middle - down right - down left - bottom middle
	 *  Left:  top middle - up right - up left - middle middle - down left - down right - bottom middle
	 *  1,4,5,8,10,12,26: 6-5-4-3-1-2-0 (right side)
	 *  2,3,6,7,9,11,13:  0-2-1-3-4-5-6 (left)
	 *  28: 0-1-2-3-4-5-6 (right)
	 *  25: 0-1-2-3-4-5-6 (left)
	 *  37: 0-1-2-3 (right)
	 *  14: 0-2-1-3 (left)
	 *
	 * Square tiles
	 * Right: top right - top left - bottom right - bottom left
	 * Left:  top right - top left - bottom right - bottom left
	 *  30,44,47,31: 3-2-1-0 (right)
	 *  41,21,15,46,20: 0-1-2-3 (left)
	 *  38,18,24: 0-1-2-3 (right)
	 *  54,22,58,57,33: 1-0-3-2 (left)
	 *  50: 2-3-0-1 (right)
	 */
	SiPM sp = getSipm(ch);
	if (sp.layer < 0)
	    return {0, 0};

	sipmXY pos;
	int bl = boardLabel[sp.layer][sp.quadrant];
	if (25 == bl)   // left side hexagonal
	    pos = hexBoardSipmXY_topdown[sp.sipm];
	else if (28 == bl || 37 == bl)	// right side hexagonal, flip the index
	    pos = hexBoardSipmXY_topdown[nHexBoardChannels - 1 - sp.sipm];
	else if (  41 == bl || 21 == bl || 15 == bl || 46 == bl || 20 == bl 
		|| 45 == bl || 49 == bl || 23 == bl || 52 == bl || 19 == bl
		|| 43 == bl || 32 == bl // left side square
		|| 30 == bl || 44 == bl || 47 == bl || 31 == bl || 36 == bl
		|| 42 == bl || 39 == bl	// right side square
		)    
	    pos = sqaBoardSipmXY_topdown[sp.sipm];
	else if (18 == bl || 38 == bl || 24 == bl || 16 == bl || 17 == bl)	// right side square, flip the index
	    pos = sqaBoardSipmXY_topdown[nSqaBoardChannels - 1 - sp.sipm];
	else if (sp.layer < nHexLayers) // general hex tile
	    pos = hexBoardSipmXY[sp.sipm];
	else if (sp.layer == transLayer && sp.quadrant > 1)
	    pos = hexBoardSipmXY[sp.sipm];
	else    // general square tile
	    pos = sqaBoardSipmXY[sp.sipm];

	if (0 == sp.quadrant || 3 == sp.quadrant)
	    pos = -pos;

	return pos + pcbAnchor[sp.quadrant];
    }

    string getFile(const char* fname)
    {
	char rootFile[1024];
	char dirs[3][1024];
	sprintf(dirs[0], ".");
	sprintf(dirs[1], "%s/data", zdcROOT);
	sprintf(dirs[2], "%s/data", backupDir);
	for (char* dir : dirs)
	{
	    sprintf(rootFile, "%s/%s", dir, fname);
	    if (fileExists(rootFile))
		return rootFile;
	}

	cerr << ERROR << "can't find file: " << fname << endl;
	return "";
    }

    string getListFile(const int run)
    {
	char buf[1024];
	sprintf(buf, "Run%d_list.txt", run);
	return getFile(buf);
    }

    string getRootFile(const int run)
    {
	char buf[1024];
	sprintf(buf, "Run%d.root", run);
	return getFile(buf);
    }

    void printSipmInfo(const int ch = 0)
    {
	assert(ch <= nChannels);
	SiPM sp = getSipm(ch);
	printf("Channel: %d\n", ch);
	printf("Board: %d\n", sp.layer*nLayerBoards + sp.quadrant);
	printf("Board Label: %d\n", boardLabel[sp.layer][sp.quadrant]);
	printf("Layer: %d\n", sp.layer);
	printf("Quadrant in Layer: %d\n", sp.quadrant);
	printf("SiPM in Board: %d\n", sp.sipm);
	sipmXY pos = getSipmXY(ch);
	printf("X:\t%.2f cm\tY:\t%.2f cm\n", pos.x/cm, pos.y/cm);
    }
}

#endif
