#ifndef __CALIBRATE__
#define __CALIBRATE__
/* calibrate a run:
 * 1. ped subtraction
 * 2. MIP conversion
 */

#include <map>
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TLeaf.h"
#include "TH2F.h"
#include "TProfile.h"
#include "TF1.h"
#include "TCanvas.h"
#include "TText.h"
#include "zdc.h"
#include "analysis.h"

using namespace std;

class calibrate {
  public:
    calibrate() {}
    ~calibrate() {}
    void setRootFile(string fin) { rootFile = fin; }
    void setPed(ped_t p) { ped = p; }
    void setMIP(mip_t m);
    void setOutDir(string f) { fdir = f; }
    void getLGMIP();
    void init();
    void fillCorADC();
    void fillCorMIP();
    void write();

  private:
    string rootFile;
    string fdir;
    ped_t ped;
    mip_t mip;

    // histograms
    TFile *fio;
    TTree *traw, *tcor, *tmip;
    map<int, TH2F*> h2;
    map<int, map<string, float>> corADC;
    map<int, map<string, float>> corMIP;
    map<string, map<string, float>> values;
};

void calibrate::setMIP(mip_t m)
{
    for (int ch = 0; ch<zdc::config["nCAENChannels"]; ch++)
    {
	if (m.find(ch) == m.end())
	{
	    cerr << WARNING << "channel " << ch << " has no MIP value" << endl;
	    mip[ch]["LG"] = 1e20;
	    mip[ch]["HG"] = 1e20;
	    continue;
	}
	for (const auto& gain : zdc::gains)
	{
	    if (m[ch].find(gain) == m[ch].end())
	    {
		cerr << WARNING << "channel " << ch << " has no " << gain << " MIP value" << endl;
		mip[ch][gain] = 1e20;
		continue;
	    }
	    mip[ch][gain] = m[ch][gain];
	    if (0 == m[ch][gain])   // set zero MIP value to infinity
		mip[ch][gain] = 1e20;
	}
    }
}

void calibrate::init()
{
    fio = new TFile(rootFile.c_str(), "update");
    for (const char *var : {/*"cor",*/ "mip"})
      if (fio->Get(var))
          fio->Delete(Form("%s;*", var));

    traw = (TTree*) fio->Get("raw");
    tcor = new TTree("cor", "corrected ADC values");
    tmip = new TTree("mip", "corrected MIP values");
    for (int ch=0; ch<zdc::config["nCAENChannels"]; ch++)
    {
	tcor->Branch(Form("ch_%d", ch), 0, "LG/F:HG/F");
	tmip->Branch(Form("ch_%d", ch), 0, "LG/F:HG/F");
	for (const auto& gain : zdc::gains)
	{
	    corADC[ch][gain] = 0;
	    corMIP[ch][gain] = 0;
	    tcor->GetBranch(Form("ch_%d", ch))->GetLeaf(gain)->SetAddress(&corADC[ch][gain]);
	    tmip->GetBranch(Form("ch_%d", ch))->GetLeaf(gain)->SetAddress(&corMIP[ch][gain]);
	}
	h2[ch] = new TH2F(Form("ch_%d", ch), Form("ch %d", ch), 100, 0, 500, 100, 0, 8000);
    }
    for (const char* var : {"hit_mul", "event_e", "event_x", "event_y", "event_z"})
    {
	tcor->Branch(var, 0, "LG/F:HG/F");
	tmip->Branch(var, 0, "LG/F:HG/F");
	for (const auto& gain : zdc::gains)
	{
	    values[var][gain] = 0;
	    tcor->GetBranch(var)->GetLeaf(gain)->SetAddress(&values[var][gain]);
	    tmip->GetBranch(var)->GetLeaf(gain)->SetAddress(&values[var][gain]);
	}
    }
}

void calibrate::fillCorADC()
{
    if (!traw->GetEntries())
    {
	cerr << FATAL << "no entry in the roofile: " << rootFile << endl;
	return;
    }

    map<int, map<string, int>> rawADC;
    for (int ch=0; ch<zdc::config["nCAENChannels"]; ch++)
    {
	TBranch *b = (TBranch*) traw->GetBranch(Form("ch_%d", ch));
	for (const auto& gain : zdc::gains)
	{
	    rawADC[ch][gain] = 0;
	    b->GetLeaf(gain)->SetAddress(&rawADC[ch][gain]);
	}
    }

    for (int ei=0; ei<traw->GetEntries(); ei++)
    {
	traw->GetEntry(ei);
	for (int ch=0; ch<zdc::config["nCAENChannels"]; ch++)
	{
	    for (const auto& gain : zdc::gains)
	    {
		corADC[ch][gain] = rawADC[ch][gain] - ped[ch][gain].mean;
		if (corADC[ch][gain] < 5*ped[ch][gain].rms)
		    corADC[ch][gain] = 0;
	    }
	    if (corADC[ch]["LG"] > 0 && corADC[ch]["HG"] < 7600 && corADC[ch]["HG"] > 0)
		h2[ch]->Fill(corADC[ch]["LG"], corADC[ch]["HG"]);
	}
    }
}

void calibrate::getLGMIP()
{
    int ncol = 8;
    int nrow = 1 + (zdc::config["nCAENChannels"].get<int>() - 1)/ncol;
    TCanvas *c = new TCanvas("c", "c", ncol*600, nrow*600);
    c->Divide(ncol, nrow, 0, 0);
    for (int ch=0; ch<zdc::config["nCAENChannels"]; ch++)
    {
	c->cd(ch+1);
	TProfile * proX = h2[ch]->ProfileX(Form("ch%d_profileX", ch));
	TF1 *fit = new TF1(Form("ch%d_fit", ch), "[0] + [1]*x", 0, 300);
	fit->SetParameters(0, 30);
	proX->Fit(fit, "q R ROB=0.95");
	if (h2[ch]->GetEntries() > 300)
	    mip[ch]["LG"] = mip[ch]["HG"] / fit->GetParameter(1);

	h2[ch]->Draw("COLZ");
	fit->Draw("same");
	TText *t = new TText(0.6, 0.2, Form("slope = %.2f", fit->GetParameter(1)));
	t->SetNDC();
	t->SetTextColor(kRed);
	t->Draw();
    }
    c->SaveAs(Form("%s/HG_vs_LG.png", fdir.c_str()));
}

void calibrate::fillCorMIP()
{
    getLGMIP();
    for (int ei=0; ei<tcor->GetEntries(); ei++)
    {
	tcor->GetEntry(ei);
	for (int ch=0; ch<zdc::config["nCAENChannels"]; ch++)
	{
	    for (const auto& gain : zdc::gains)
	    {
		corMIP[ch][gain] = corADC[ch][gain] / mip[ch][gain];
		if (corMIP[ch][gain] < 0.3)
		    corMIP[ch][gain] = 0;
	    }
	}
    }
}

void calibrate::write()
{
    fio->cd();
    // tcor->Write();
    tmip->Write();
    fio->Close();
}
#endif
