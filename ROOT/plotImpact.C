// Functions for building plots and graphs from Impact-T data
// written by Matt Easton November 2018

// Functions to produce each different plot type
TCanvas *plotImpactBunches(TTree *impact_data,
                           Int_t bunchCount, Int_t lastSlice);
void plotImpactBunchLayer(TCanvas *impact_canvas, TTree *impact_data,
                          Int_t currentBunch, Int_t lastSlice,
                          Bool_t isBackLayer);

// Style functions to adjust formatting for different plot types
void styleImpactBunches(TCanvas *impact_canvas, Int_t bunchCount);

// Other functions
void renameCurrentGraph(TCanvas *canvas, const char *name);
std::string buildCumulativePlotString(std::string branchName,
                                      std::string prefix,
                                      std::string xaxis,
                                      Int_t variableCount);


// Plot bunch count data loaded from `fort.11`
TCanvas *plotImpactBunches(TTree *impact_data,
                           Int_t bunchCount, Int_t lastSlice) {

    // Check bunch count
    if (bunchCount < 1) {
        throw std::invalid_argument("Must have at least one bunch.");
    }
    // Check last slice
    if (lastSlice < 1) {
        throw std::invalid_argument("Must have at least one data slice.");
    }
    if (lastSlice > impact_data->GetEntries() - 1) {
        throw std::invalid_argument("Selected slice is beyond the last data point.");
    }

    // Set canvas properties
    TCanvas *impact_canvas = new TCanvas("impact_canvas", "Impact-T plots");
    impact_canvas->SetWindowSize(800, 500);

    // Draw the cumulative plots layer by layer, starting at the back
    plotImpactBunchLayer(impact_canvas, impact_data, bunchCount, lastSlice, true);
    for (Int_t i = bunchCount - 1; i > 0; i--) {
        plotImpactBunchLayer(impact_canvas, impact_data, i, lastSlice, false);
    }

    // Apply styles
    styleImpactBunches(impact_canvas, bunchCount);

    // Update canvas
    impact_canvas->Update();
    impact_canvas->Paint();

    // Print to file
    impact_canvas->Print("bunch-count.eps", "eps");

    // Return canvas as result
    return impact_canvas;

}

void plotImpactBunchLayer(TCanvas *impact_canvas, TTree *impact_data,
                          Int_t currentBunch, Int_t lastSlice,
                          Bool_t isBackLayer) {

    // Build correct settings for current layer
    std::string axesDefinition = buildCumulativePlotString("bunches", "n", "z",
                                                           currentBunch);
    std::string graphName = "graph" + std::to_string(currentBunch);
    std::string plotLocation = "";
    if (! isBackLayer) { plotLocation = "same"; }

    // Draw graph
    impact_data->Draw(axesDefinition.c_str(), "", plotLocation.c_str(),
                      lastSlice, 0);

    // Rename graph
    renameCurrentGraph(impact_canvas, graphName.c_str());

    // Return
    return;

}


// Function to format the particle count plot
void styleImpactBunches(TCanvas *impact_canvas, Int_t bunchCount) {

    // Get objects
    TFrame *impact_frame = impact_canvas->GetFrame();
    TPaveText *titleText = (TPaveText * ) impact_canvas->GetPrimitive("title");
    TH1 *impact_hist = (TH1 * ) impact_canvas->GetPrimitive("htemp");
    std::string graphName = "";
    TGraph *graph;

    // Set up background
    impact_frame->SetLineWidth(0);
    titleText->Clear();
    impact_canvas->SetGridx(false);
    impact_canvas->SetGridy(true);

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

    // Set graph draw options
    for (Int_t i = 1; i <= bunchCount; i++) {
        graphName = "graph" + std::to_string(i);
        graph = (TGraph * ) impact_canvas->GetPrimitive(graphName.c_str());
        graph->SetDrawOption("B");
        // Colours and names are hard-coded for now
        switch (i) {
            case 1:
                graph->SetFillColor(38);   // Blue
                impact_legend->AddEntry(graph, "Molecular hydrogen ions", "f");
                break;
            case 2:
                graph->SetFillColor(623);  // Salmon red
                impact_legend->AddEntry(graph, "Protons", "f");
                break;
            case 3:
                graph->SetFillColor(30);   // Green
                impact_legend->AddEntry(graph, "Neutral hydrogen molecules", "f");
                break;
            case 4:
                graph->SetFillColor(42);   // Mustard
                impact_legend->AddEntry(graph, "Neutral atomic hydrogen", "f");
                break;
        }
    }

    // Update canvas
    impact_legend->Draw();
    impact_canvas->Update();
    impact_canvas->Paint();

    // Return
    return;

}


// Function to rename the current graph
void renameCurrentGraph(TCanvas *canvas, const char *name) {

    // Get the current graph
    TGraph *current_graph = (TGraph *) canvas->GetPrimitive("Graph");

    // Reset the graph name (to make it easier to find later)
    current_graph->SetName(name);

    // Return
    return;

}

// Function to create the plot string for a cumulative plot,
//  where the cumulative data variables follow a consequetive naming pattern
std::string buildCumulativePlotString(std::string branchName,
                                      std::string prefix,
                                      std::string xaxis,
                                      Int_t variableCount) {

    // First variable for y-axis
    std::string plotString = branchName + "." + prefix + std::to_string(1);

    // Subsequent variables for y-axis (cumulative)
    for (Int_t i = 2; i <= variableCount; i++) {
        plotString += "+" + branchName + "." + prefix + std::to_string(i);
    }

    // Single variable for x-axis
    plotString += ":" + branchName + "." + xaxis;

    // Return
    return plotString;

}
