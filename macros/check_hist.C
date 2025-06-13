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
	for (int j=0; j<25; j++)
	{
	    c->cd(j+1);
	    gPad->SetLogy(1);
	    int ch = 25*i+j;
	    TH1F* h = (TH1F*) fin->Get(Form("Ch_%d_HG", ch));
	    if (h)
		h->Draw("HIST");
	}
	c->SaveAs("check.pdf");
    }
    c->SaveAs("check.pdf]");
}
