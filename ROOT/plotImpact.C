// Plot particle data loaded from `fort.11` (hard-coded to 4 bunches for now)
TCanvas * plotImpactParticles(TTree *impact_data){

    // Set canvas properties
    TCanvas *impact_canvas = new TCanvas("impact_canvas", "Impact-T plots");
    impact_canvas->SetWindowSize(800, 500);

    // Draw the first dataset (back layer, all four bunches)
    impact_data->Draw("bunches.n1+bunches.n2+bunches.n3+bunches.n4:bunches.z", "", "");
    // Draw the second dataset (next layer, without the fourth bunch)
    impact_data->Draw("bunches.n1+bunches.n2+bunches.n3:bunches.z", "", "same");
    // Draw the third dataset (next layer, without the third and fourth bunches)
    impact_data->Draw("bunches.n1+bunches.n2:bunches.z", "", "same");
    // Draw the fourth dataset (top layer, first bunch only)
    impact_data->Draw("bunches.n1:bunches.z", "", "same");

    // Update canvas
    impact_canvas->Update();
    impact_canvas->Paint();

    // Return canvas as result
    return impact_canvas;

}
