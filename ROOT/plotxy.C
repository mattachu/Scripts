// Macro for plotting simple x-y graphs in ROOT, with my preferred formatting
// written by Matt Easton (see http://matteaston.net/work), December 2018

#include "Style_mje.C"

// Parameters
std::string _PLOTXY_FILENAME      = "rootplot.eps";
std::string _PLOTXY_CANVAS_NAME   = "plotxy_canvas";
std::string _PLOTXY_CANVAS_TITLE  = "Scatter plot x-y";
Int_t const _PLOTXY_CANVAS_WIDTH  = 800;
Int_t const _PLOTXY_CANVAS_HEIGHT = 500;
std::string _PLOTXY_GRAPH_NAME   = "plotxy_graph";

// Plot function
void plotxy(
    Int_t n,
    Double_t x[],
    Double_t y[],
    std::string xtitle = "x",
    std::string ytitle = "y",
    std::string title = _PLOTXY_CANVAS_TITLE,
    Int_t width = _PLOTXY_CANVAS_WIDTH,
    Int_t height = _PLOTXY_CANVAS_HEIGHT,
    std::string filename = _PLOTXY_FILENAME
)
{
    // Load style
    load_style_mje();
    gROOT->SetStyle("mje");

    // Set up canvas
    TCanvas *canvas = (TCanvas *) gROOT->FindObject(_PLOTXY_CANVAS_NAME.c_str());
    if (!canvas) {
        canvas = new TCanvas(_PLOTXY_CANVAS_NAME.c_str());
    }
    canvas->SetTitle(title.c_str());
    canvas->SetWindowSize(width, height);
    canvas->UseCurrentStyle();

    // Create and format graph
    TGraph* graph = new TGraph(n, x, y);
    graph->SetName(_PLOTXY_GRAPH_NAME.c_str());
    graph->SetMarkerStyle(20);
    graph->SetMarkerSize(0.7);
    graph->SetMarkerColor(38);
    graph->SetLineWidth(2);
    graph->SetLineColor(38);
    graph->GetXaxis()->SetTitle(xtitle.c_str());
    graph->GetXaxis()->SetTitleFont(132);
    graph->GetXaxis()->SetTitleSize(0.05);
    graph->GetXaxis()->CenterTitle(kTRUE);
    graph->GetXaxis()->SetLabelFont(132);
    graph->GetXaxis()->SetLabelSize(0.035);
    graph->GetYaxis()->SetTitle(ytitle.c_str());
    graph->GetYaxis()->SetTitleFont(132);
    graph->GetYaxis()->SetTitleSize(0.05);
    graph->GetYaxis()->CenterTitle(kTRUE);
    graph->GetYaxis()->SetLabelFont(132);
    graph->GetYaxis()->SetLabelSize(0.035);
    graph->Draw("ALP");

    // Resize frame to fill the canvas
    canvas->GetFrame()->SetBBoxX1(30);
    canvas->GetFrame()->SetBBoxX2(width - 30 - 10);
    canvas->GetFrame()->SetBBoxY1(10);
    canvas->GetFrame()->SetBBoxY2(height - 30 - 10);

    // Update canvas
    canvas->Update();
    canvas->Paint();

    // Print to file
    canvas->Print(filename.c_str(), "eps");
}
