/* const information about the prototype and run */
#ifndef __ZDC__
#define __ZDC__

#include <cstdio>
#include <cmath>
#include <cassert>
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <stdlib.h>
#include <string>
#include <nlohmann/json.hpp>
#include "calo.h"
#include "utilities.h"

using namespace std;

namespace zdc {
    const char* ZDCROOT = (assert(getenv("ZDCROOT") != NULL), true)
	? getenv("ZDCROOT")
	: ".";
    const char* ZDCBACKUP = "/media/arratialab/CALI/NSRL_test/";

    // config
    auto getConfig()
    {
	char buf[1024];
	sprintf(buf, "%s/database/zdc_config.json", ZDCROOT);
	ifstream configFile(buf);
	auto configIn = nlohmann::json::parse(configFile);
	auto config = nlohmann::json::object();

	// Copy all top-level fields except caen2sipm
	for (auto& [key, value] : configIn.items()) {
	    if (key != "caen2sipm" && key != "sipm2caen" && key != "sipmLayer" && key != "sipmPos") {
		config[key] = value;
	    }
	}

	for (int i=0; i<config["nCAENChannels"]; i++) 
	{
	    config["caen2sipm"][i] = configIn["caen2sipm"][to_string(i)];
	}
	for (int i=0; i<config["nSiPMChannels"]; i++) 
	{
	    string key = to_string(i);
	    config["sipm2caen"][i] = configIn["sipm2caen"][key];
	    config["sipmLayer"][i] = configIn["sipmLayer"][key];
	    config["sipmPos"][i] = configIn["sipmPos"][key];
	}

	return config;
    }
    auto config = getConfig();
    const char* gains[] = {"HG", "LG"};

    // run dependent info
    void setRun(const int run)
    {
    }

    string getFile(const char* fname)
    {
	char rootFile[1024];
	char dirs[3][1024];
	sprintf(dirs[0], ".");
	sprintf(dirs[1], "%s/data", ZDCROOT);
	sprintf(dirs[2], "%s/data", ZDCBACKUP);
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
	for (int i=0; i<config["nSiPMChannels"]; i++) 
	{
	    int caenCh = config["sipm2caen"][i];
	    int layer = config["sipmLayer"][i];
	    auto pos = config["sipmPos"][i];
	    cout << "sipm channel: " << i << "\t"
		 << "caen channel: " << caenCh << "\t"
		 << "layer: "  << layer << "\t"
		 << "pos: " << pos[0] << ", " << pos[1] << ", " << pos[2]
		 << endl;
	}
    }
}

#endif
