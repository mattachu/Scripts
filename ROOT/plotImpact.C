void plotEnergyHistogram(TCanvas *canvas, TImpactTree *impact)
{
    canvas->SetName("impact_energy_hist");
    canvas->SetTitle("Impact-T energy histogram");
    canvas->SetWindowSize(800, 500);
    impact->Draw("endslice.bunch1.W", "", "BAR");
    impact->Draw("endslice.bunch2.W", "", "BAR same");
    impact->Draw("endslice.bunch3.W", "", "BAR same");
    impact->Draw("endslice.bunch4.W", "", "BAR same");
}
