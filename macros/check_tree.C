#include "zdc.h"

// simple histogram for all events
/*
void check_tree(const char* fname = "run.root")
{
    gROOT->SetBatch(1);
    gStyle->SetOptStat(111111);
    TFile * fin = new TFile(fname, "read");
    TTree * traw = (TTree*) fin->Get("raw");

    TCanvas* c = new TCanvas("c", "c", 3000, 3000);
    c->SaveAs("check.pdf[");

    for (int i=0; i<23; i++)
    {
	c->Clear();
	c->Divide(5, 5);
	for (int j=0; j<25; j++)
	{
	    int sipmCh = 25*i+j;
	    if (sipmCh >= zdc::config["nSiPMChannels"])
	    {
		cout << sipmCh << endl;
		continue;
	    }
	    c->cd(j+1);
	    gPad->SetLogy(1);
	    int caenCh = zdc::config["sipm2caen"][sipmCh];
	    traw->Draw(Form("ch_%d.LG>>htemp%d", caenCh, sipmCh));
	    TH1F* htemp = (TH1F*)gDirectory->Get(Form("htemp%d", sipmCh));
	    htemp->SetTitle(Form("Ch %d", sipmCh));
	}
	c->SaveAs("check.pdf");
    }
    c->SaveAs("check.pdf]");
}
*/

// graphs for each event
void check_tree(const char* fname = "run.root", const char* gain = "HG")
{
    gROOT->SetBatch(1);
    gStyle->SetOptStat(111111);
    TFile * fin = new TFile(fname, "read");
    TTree * traw = (TTree*) fin->Get("raw");

    map<int, int> rawADC;
    for (int ch=0; ch<zdc::config["nCAENChannels"]; ch++)
    {
	TBranch *b = (TBranch*) traw->GetBranch(Form("ch_%d", ch));
	b->GetLeaf(gain)->SetAddress(&rawADC[ch]);
    }

    TGraph* g = new TGraph();

    TCanvas* c = new TCanvas("c", "c", 3000, 3000);
    c->SaveAs("check.pdf[");

    for (int ei=0; ei<traw->GetEntries(); ei++)
    {
	traw->GetEntry(ei);

	g->Clear();
	g->SetTitle(Form("Event %d", ei));
	g->SetMarkerStyle(20); // Small filled circle
	g->SetMarkerSize(0.7); // Small size to avoid clutter
	g->SetMarkerColor(kBlue);

	int pi = 0;
	for (int l=0; l<23; l++)
	{
	    for (int j=0; j<25; j++)
	    {
		int sipmCh = 25*l+j;
		if (sipmCh >= zdc::config["nSiPMChannels"])
		    continue;
		int caenCh = zdc::config["sipm2caen"][sipmCh];
		g->SetPoint(pi, sipmCh, rawADC[caenCh]);
		pi++;
	    }
	}
	g->Draw("AP");
	c->SaveAs("check.pdf");
    }
    c->SaveAs("check.pdf]");
}
