#include "zdc.h"

void check_hist(const char* fname = "hist.root")
{
    gROOT->SetBatch(1);
    gStyle->SetOptStat(111111);
    TFile * fin = new TFile(fname, "read");

    TCanvas* c = new TCanvas("c", "c", 3000, 3000);
    c->SaveAs("check.pdf[");

    c->Divide(5, 5);
    for (int i=0; i<23; i++)
    {
	c->Clear();
	c->Divide(5, 5);
	for (int j=0; j<25; j++)
	{
	    int sipmCh = 25*i+j;
	    if (sipmCh >= zdc::config["nSiPMChannels"])
	    {
		// cout << sipmCh << endl;
		continue;
	    }
	    c->cd(j+1);
	    gPad->SetLogy(1);
	    int caenCh = zdc::config["sipm2caen"][sipmCh];
	    TH1F* h = (TH1F*) fin->Get(Form("Ch_%d_HG", caenCh));
	    h->SetTitle(Form("%d", sipmCh));
	    if (h)
	    {
		h->Draw("HIST");
		cout << sipmCh << "\t" <<  h->GetBinCenter(h->GetMaximumBin()) << endl;
	    }
	}
	c->SaveAs("check.pdf");
    }
    c->SaveAs("check.pdf]");
}
