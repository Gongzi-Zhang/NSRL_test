// the main entrance for all sub commands

#include <iostream>
#include <string>

#include "utilities.h"
#include "zdc.h"
#include "db.h"
#include "analysis.h"
#include "convert.h"
#include "calibrate.h"
// #include "QA.h"
// #include "MIP.h"
// #include "makeMyrec.h"
// #include "clustering.h"

using namespace std;

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
	cerr << FATAL << "incorrected number of parameters" << endl;
	cerr << INFO << "usage: " << argv[0] << " [convert,calibrate,QA,MIP,makerec,clustering] run" << endl;
	exit(4);
    }

    string command = argv[1];
    const int run = atoi(argv[2]);
    // zdc::setRun(run);
    zdcDB db;

    string runType = db.getRunType(run);
    string runFlag = db.getRunFlag(run);

    if (runFlag != "good")
    {
	cerr << WARNING << "not a good run: " << run << endl;
	exit(1);
    }

    if (command == "convert")
    {
	if (runType != "data" && runType != "cmdata")
	{
	    cout << ERROR << "not a data run: " << run << endl;
	    exit(1);
	}

	char outName[1024];
	sprintf(outName, "%s/data/Run%d.root", zdc::ZDCROOT, run);

	string listFile = zdc::getListFile(run);
	listReader* reader = new listReader(listFile.c_str());

	eventBuilder *builder = new eventBuilder(reader);
	treeMaker *maker = new treeMaker(builder);
	maker->setStartTime(reader->getStartTime());
	maker->setOfName(outName);
	maker->init();
	maker->fill();
	maker->write();

	delete builder;
	delete maker;

	delete reader;
    }
    else if (command == "calibrate")
    {
	if (runType != "data" && runType != "cmdata")
	{
	    cerr << ERROR << "not a data/cmdata run: " << run << endl;
	    exit(1);
	}

	const int pedRun = db.getPedRun(run);
	ped_t ped;
	if (!getPedestal(pedRun, ped))
	{
	    cerr << FATAL << "unable to read pedestal" << endl;
	    exit(2);
	}

	const int mipRun = db.getMIPRun(run);
	mip_t mip;
	if (!getMIP(mipRun, mip))
	{
	    cerr << FATAL << "unable to read mip" << endl;
	    exit(2);
	}
	char buf[1024];
	sprintf(buf, "Run%d.root", run);
	string rootFile = zdc::getFile(buf);

	memset(buf, 0, sizeof(buf));
	sprintf(buf, "%s/figures/%d", zdc::ZDCROOT, run);
	if (!dirExists(buf))
	    mkdir(buf, 0755);

	calibrate *cab = new calibrate();
	cab->setRootFile(rootFile.c_str());
	cab->setOutDir(buf);
	cab->setPed(ped);
	cab->setMIP(mip);
	cab->init();
	cab->fillCorADC();
	cab->fillCorMIP();
	cab->write();
	delete cab;
    }
    /*
    else if (command == "QA")
    {
	if (runType != "data")
	{
	    cerr << ERROR << "not a data run: " << run << endl;
	    exit(1);
	}

	char fdir[1024];                                                            
	sprintf(fdir, "%s/figures/%d/", zdc::ZDCROOT, run);                       
	if (!dirExists(fdir))                                                       
	    mkdir(fdir, 0755);                                                      
	string rootFile = zdc::getRootFile(run);
										    
	QA *qa = new QA();                                                          
	qa->setRunType(runType.c_str());                                            
	qa->setRootFile(rootFile.c_str());                                                  
	qa->setOutDir(fdir);                                                        
	qa->setDeltaT(-5*3600); // switch to NY time zone                           
	qa->init();                                                                 
	qa->fill();                                                                 
	qa->plot();                                                                 
	delete qa;    
    }
    else if (command == "MIP")	// MIP analysis for mip runs
    {
	if (runType != "mip")
	{
	    cerr << ERROR << "Not a MIP run: " << run << endl;
	    exit(1);
	}

	char fdir[1024];
	sprintf(fdir, "%s/figures/%d/", zdc::ZDCROOT, run);
	if (!dirExists(fdir))
	    mkdir(fdir, 0755);

	string rootFile = zdc::getRootFile(run);

	char mipOut[1024];
	sprintf(mipOut, "%s/data/Run%d_MIP.json", zdc::ZDCROOT, run);

	MIPfinder *finder = new MIPfinder();
	finder->setRootFile(rootFile.c_str());
	finder->setOutDir(fdir);
	finder->setOutFile(mipOut);
	finder->init();
	finder->readADC();
	// finder->findMIP();
	finder->plot();
	finder->write();

	delete finder;
    }
    else if (command == "makerec")  // extract caliHits for cluster reconstruction
    {
	if (runType != "data")
	{
	    cerr << WARNING << "not a data run: " << run << endl;
	    exit(1);
	}

	string rootFile = zdc::getRootFile(run);

	makeMyrec *maker = new makeMyrec();
	maker->setInFile(rootFile);
	maker->init();
	maker->make();

	delete maker;
    }	
    else if (command == "clustering")  // clustering hits
    {
	if (runType != "data")
	{
	    cerr << WARNING << "not a data run: " << run << endl;
	    exit(1);
	}
	char buf[1024];
	sprintf(buf, "Run%d.myrec.root", run);
	string recFile = zdc::getFile(buf);

	clustering *cs = new clustering();
	cs->setInput(recFile);
	// cs->setOutput(fdir);
	cs->setNeighborX(6*cm);
	cs->setNeighborY(5*cm);
	cs->setNeighborZ(1.3);
	cs->setMinClusterNhits(3);
	cs->setMinClusterCenterE(5);
	cs->setMinClusterHitE(0.5);
	cs->setMinClusterE(20);
	cs->init();
	cs->process();
	delete cs;
    }
     */
}
