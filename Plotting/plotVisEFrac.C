void plotVisEFrac() {
    TFile *file = TFile::Open("hists.root");

    TH1F *h_plus = (TH1F*)file->Get("Hists/h_visEFrac_plus");
    TH1F *h_neg  = (TH1F*)file->Get("Hists/h_visEFrac_neg");

    h_plus->SetLineColor(kRed);
    h_neg->SetLineColor(kBlue);
    h_plus->SetLineWidth(2);
    h_neg->SetLineWidth(2);

    gStyle->SetOptStat(0);
    
    TCanvas* canv = new TCanvas("canv", "Visible Energy Fraction", 1000, 800);
    canv->SetLeftMargin(0.15);
    h_plus->Draw("HIST");
    h_neg->Draw("HIST SAME");

    TLegend *leg = new TLegend(0.7, 0.7, 0.9, 0.9);
    leg->SetBorderSize(0);
    leg->SetFillStyle(0);
    leg->AddEntry(h_plus, "#tau^{+}", "l");
    leg->AddEntry(h_neg, "#tau^{-}", "l");
    leg->Draw();

    h_plus->SetTitle("Visible Energy Fraction of DM0 Taus; E_{vis} Fraction; Events");

    canv->Update();
    TString wait;
    cout << "Hit ENTER to save and close plot: "; 
    cin >> wait;
    canv->SaveAs("visEFrac.png");
}
