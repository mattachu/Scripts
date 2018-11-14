// Function to rename the current graph
void renameCurrentGraph(TCanvas *impact_canvas, const char *name) {

    // Get the current graph
    TGraph *current_graph = (TGraph *) impact_canvas->GetPrimitive("Graph");

    // Reset the graph name (to make it easier to find later)
    current_graph->SetName(name);
}

// Plot particle data loaded from `fort.11` (hard-coded to 4 bunches for now)
TCanvas * plotImpactParticles(TTree *impact_data){

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

    // Update canvas
    impact_canvas->Update();
    impact_canvas->Paint();

    // Return canvas as result
    return impact_canvas;

}
