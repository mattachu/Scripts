// Functions for building plots and graphs from Impact-T data
// written by Matt Easton November 2018

// Functions to produce each different plot type
TCanvas *plotImpactParticles(TTree *impact_data);

// Style functions to adjust formatting for different plot types
void styleImpactParticles(TCanvas *impact_canvas);

// Other functions
void renameCurrentGraph(TCanvas *impact_canvas, const char *name);


// Plot bunch count data loaded from `fort.11` (hard-coded to 4 bunches for now)
TCanvas *plotImpactParticles(TTree *impact_data){

    // Set canvas properties
    TCanvas *impact_canvas = new TCanvas("impact_canvas", "Impact-T plots");
    impact_canvas->SetWindowSize(800, 500);

    // Draw the first dataset (back layer, all four bunches)
    impact_data->Draw("bunches.n1+bunches.n2+bunches.n3+bunches.n4:bunches.z",
                      "", "", 4563, 0);
    renameCurrentGraph(impact_canvas, "graph4");
    // Draw the second dataset (next layer, without the fourth bunch)
    impact_data->Draw("bunches.n1+bunches.n2+bunches.n3:bunches.z", "", "same",
                      4563, 0);
    renameCurrentGraph(impact_canvas, "graph3");
    // Draw the third dataset (next layer, without the third and fourth bunches)
    impact_data->Draw("bunches.n1+bunches.n2:bunches.z", "", "same", 4563, 0);
    renameCurrentGraph(impact_canvas, "graph2");
    // Draw the fourth dataset (top layer, first bunch only)
    impact_data->Draw("bunches.n1:bunches.z", "", "same", 4563, 0);
    renameCurrentGraph(impact_canvas, "graph1");

    // Apply styles
    styleImpactParticles(impact_canvas);

    // Update canvas
    impact_canvas->Update();
    impact_canvas->Paint();

    // Print to file
    impact_canvas->Print("bunch-count.eps", "eps");

    // Return canvas as result
    return impact_canvas;

}


// Function to format the particle count plot
void styleImpactParticles(TCanvas *impact_canvas) {

    // Get objects
    TFrame *impact_frame = impact_canvas->GetFrame();
    TPaveText *titleText = (TPaveText * ) impact_canvas->GetPrimitive("title");
    TH1 *impact_hist = (TH1 * ) impact_canvas->GetPrimitive("htemp");
    TGraph *g1 = (TGraph * ) impact_canvas->GetPrimitive("graph1");
    TGraph *g2 = (TGraph * ) impact_canvas->GetPrimitive("graph2");
    TGraph *g3 = (TGraph * ) impact_canvas->GetPrimitive("graph3");
    TGraph *g4 = (TGraph * ) impact_canvas->GetPrimitive("graph4");

    // Set up background
    impact_frame->SetLineWidth(0);
    titleText->Clear();
    impact_canvas->SetGridx(false);
    impact_canvas->SetGridy(true);

    // Set graph draw options
    g1->SetDrawOption("B");
    g2->SetDrawOption("B");
    g3->SetDrawOption("B");
    g4->SetDrawOption("B");
    g1->SetFillColor(38);   // Blue
    g2->SetFillColor(623);  // Salmon red
    g3->SetFillColor(30);   // Green
    g4->SetFillColor(42);   // Mustard

    // Set axes options
    // - font code 132 is Times New Roman, medium, regular, scalable
    // x-axis
    impact_hist->GetXaxis()->SetTicks("-");
    impact_hist->GetXaxis()->SetTickSize(0.01);
    impact_hist->GetXaxis()->SetTitleOffset(-1.0);
    impact_hist->GetXaxis()->SetLabelOffset(-0.04);
    impact_hist->GetXaxis()->SetTitle("z-position (m)");
    impact_hist->GetXaxis()->SetTitleFont(132);
    impact_hist->GetXaxis()->SetTitleSize(0.045);
    impact_hist->GetXaxis()->SetLabelFont(132);
    impact_hist->GetXaxis()->SetLabelSize(0.03);
    impact_hist->GetXaxis()->SetLimits(0, 1.8);
    impact_hist->GetXaxis()->SetRangeUser(0, 1.8);
    // y-axis
    impact_hist->GetYaxis()->SetTicks("+");
    impact_hist->GetYaxis()->SetTickSize(0.01);
    impact_hist->GetYaxis()->SetTitleOffset(-0.8);
    impact_hist->GetYaxis()->SetLabelOffset(-0.01);
    impact_hist->GetYaxis()->SetTitle("Total number of macro-particles");
    impact_hist->GetYaxis()->SetTitleFont(132);
    impact_hist->GetYaxis()->SetTitleSize(0.045);
    impact_hist->GetYaxis()->SetLabelFont(132);
    impact_hist->GetYaxis()->SetLabelSize(0.03);
    impact_hist->GetYaxis()->SetLimits(90000, 102000);
    impact_hist->GetYaxis()->SetRangeUser(90000, 102000);

    // Add legend
    TLegend *impact_legend = new TLegend(0.540, 0.122, 0.841, 0.292);
    impact_legend->SetTextFont(132);
    impact_legend->SetTextSize(0.03);
    impact_legend->AddEntry(g4, "Neutral atomic hydrogen", "f");
    impact_legend->AddEntry(g3, "Neutral hydrogen molecules", "f");
    impact_legend->AddEntry(g2, "Protons", "f");
    impact_legend->AddEntry(g1, "Molecular hydrogen ions", "f");
    impact_legend->Draw();

    // Update canvas
    impact_canvas->Update();
    impact_canvas->Paint();

}


// Function to rename the current graph
void renameCurrentGraph(TCanvas *impact_canvas, const char *name) {

    // Get the current graph
    TGraph *current_graph = (TGraph *) impact_canvas->GetPrimitive("Graph");

    // Reset the graph name (to make it easier to find later)
    current_graph->SetName(name);
}
