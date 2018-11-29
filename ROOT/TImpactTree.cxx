// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include <vector>
#include "TImpactTree.h"

// Implements class `TImpactTree`
ClassImp(TImpactTree);

// Parameters
Int_t const _MAX_BUNCH_COUNT = 99; // Required for load method

// Default constructor
TImpactTree::TImpactTree():
    _bunchCount(1), _cellCount(0), _sliceCount(0),
    _firstCell(0), _firstSlice(0), _lastCell(0), _lastSlice(0)
{
    this->SetDefaultBunchNames();
}

// Constructor given bunch count only
TImpactTree::TImpactTree(Int_t bunchCount):
    _bunchCount(bunchCount), _cellCount(0), _sliceCount(0),
    _firstCell(0), _firstSlice(0), _lastCell(0), _lastSlice(0)
{
    this->SetDefaultBunchNames();
}

// Constructor given bunch count and bunch names
TImpactTree::TImpactTree(Int_t bunchCount, std::vector<std::string> bunchNames):
   _bunchCount(bunchCount), _cellCount(0), _sliceCount(0),
   _firstCell(0), _firstSlice(0), _lastCell(0), _lastSlice(0)
{
    this->SetBunchNames(bunchNames);
}

// Default destructor
TImpactTree::~TImpactTree()
{

}

// Methods to access members
Int_t TImpactTree::BunchCount() const
{
    return this->_bunchCount;
}

Int_t TImpactTree::CellCount() const
{
    return this->_cellCount;
}

Int_t TImpactTree::SliceCount() const
{
    return this->_sliceCount;
}

std::vector<std::string> TImpactTree::GetBunchNames() const
{
    return this->_bunchNames;
}

Int_t TImpactTree::GetFirstCell() const
{
    return this->_firstCell;
}

Int_t TImpactTree::GetFirstSlice() const
{
    return this->_firstSlice;
}

Int_t TImpactTree::GetLastCell() const
{
    return this->_lastCell;
}

Int_t TImpactTree::GetLastSlice() const
{
    return this->_lastSlice;
}

void TImpactTree::SetDefaultBunchNames()
{
    std::vector<std::string> bunchNames;
    Int_t bunchCount = this->BunchCount();
    for (Int_t i = 1; i <= bunchCount; i++) {
        bunchNames.push_back("Bunch " + std::to_string(i));
    }
    this->_bunchNames = bunchNames;
}

void TImpactTree::SetBunchNames(std::vector<std::string> bunchNames)
{
    Int_t bunchCount = this->BunchCount();
    if (bunchNames.size() < bunchCount) {
        for (Int_t i = bunchNames.size()+1; i <= bunchCount; i++) {
            bunchNames.push_back("Bunch " + std::to_string(i));
        }
    }
    bunchNames.resize(bunchCount);
    this->_bunchNames = bunchNames;
}

void TImpactTree::SetFirstCell(Int_t firstCell)
{
    if (firstCell > this->_cellCount) {
        throw std::invalid_argument(
            "Cannot set the cell number higher than the number of cells."
        );
    }
    if (firstCell < 0) {
        throw std::invalid_argument("Cannot set negative cell numbers.");
    }

    this->_firstCell = firstCell;
}

void TImpactTree::SetFirstSlice(Int_t firstSlice)
{
    if (firstSlice > this->_sliceCount) {
        throw std::invalid_argument(
            "Cannot set the slice number higher than the number of slices."
        );
    }
    if (firstSlice < 0) {
        throw std::invalid_argument("Cannot set negative slice numbers.");
    }

    this->_firstSlice = firstSlice;
}

void TImpactTree::SetLastCell(Int_t lastCell)
{
    if (lastCell > this->_cellCount) {
        throw std::invalid_argument(
            "Cannot set the cell number higher than the number of cells."
        );
    }
    if (lastCell < 0) {
        throw std::invalid_argument("Cannot set negative cell numbers.");
    }
    if (lastCell < this->_firstCell) {
        throw std::invalid_argument(
            "Cannot set the last cell number lower than the first cell."
        );
    }

    this->_lastCell = lastCell;
}

void TImpactTree::SetLastSlice(Int_t lastSlice)
{
    if (lastSlice > this->_sliceCount) {
        throw std::invalid_argument(
            "Cannot set the slice number higher than the number of slices."
        );
    }
    if (lastSlice < 0) {
        throw std::invalid_argument("Cannot set negative slice numbers.");
    }
    if (lastSlice < this->_firstSlice) {
        throw std::invalid_argument(
            "Cannot set the last slice number lower than the first slice."
        );
    }

    this->_lastSlice = lastSlice;
}

// Methods to load data from Impact-T output files
// - publicly accessible method
void TImpactTree::Load()
{
    this->_Load(this->_bunchCount);
}

// - wrapper method to load all data types
void TImpactTree::_Load(Int_t bunchCount)
{
    // Check parameters
    std::string errorString = "";
    if (bunchCount < 1) {
        errorString = "Must have at least one bunch.";
        throw std::invalid_argument(errorString.c_str());
    }
    if (bunchCount > _MAX_BUNCH_COUNT) {
        errorString = "Cannot handle more than " +
                      std::to_string(_MAX_BUNCH_COUNT) + " bunches.";
        throw std::invalid_argument(errorString.c_str());
    }

    // Load each data type from the relevant files
    this->_LoadBunches(bunchCount);

    // Output data summary
    this->Print();
}

// - particle count data from `fort.11`
void TImpactTree::_LoadBunches(Int_t bunchCount)
{
    // Create structure to hold data
    struct impact_step_t {
        Long_t i = 0;
        Double_t t = 0.0, z = 0.0;
        Int_t bunches = 0;
        Int_t count[_MAX_BUNCH_COUNT];
    };
    impact_step_t step;
    std::string leafDefinition = "i/L:t/D:z/D:bunches/I";
    for (Int_t i = 1; i <= bunchCount; i++) {
        leafDefinition += ":n" + std::to_string(i) + "/I";
    }

    // Create a branch for the particle count data
    this->Branch("bunches", &step, leafDefinition.c_str());

    // Read in data from `fort.11`
    ifstream infile("fort.11");
    while (1) {
        if (!infile.good()) break;
        infile >> step.i >> step.t >> step.z >> step.bunches;
        for (Int_t i = 0; i < bunchCount; i++) {
            infile >> step.count[i];
        }
        this->Fill();
    }
    infile.close();

    // Set number of slices for the tree object
    this->_sliceCount = this->GetBranch("bunches")->GetEntries();
    this->_firstSlice = 1;
    this->_lastSlice = this->_sliceCount - 1;
}

// Methods to produce different plot types
// - bunch count cumulative plot for data loaded from `fort.11`
void TImpactTree::PlotBunches()
{
    TCanvas *canvas = new TCanvas(
        "impact_bunch_count_plot",
        "Impact-T bunch count plot"
    );
    this->_PlotBunches(
        canvas,
        this->_bunchCount,
        this->_lastSlice,
        this->_bunchNames,
        0, 1.8,       // xmin, xmax
        90000, 102000 // ymin, ymax
    );
}

void TImpactTree::_PlotBunches(
    TCanvas *canvas,
    Int_t bunchCount,
    Int_t lastSlice,
    std::vector<std::string> bunchNames,
    Double_t xmin,
    Double_t xmax,
    Double_t ymin,
    Double_t ymax
)
{
    // Check parameters
    if (bunchCount < 1) {
        throw std::invalid_argument("Must have at least one bunch.");
    }
    if (bunchCount > this->_bunchCount) {
        throw std::invalid_argument("Trying to plot too many bunches.");
    }
    if (lastSlice < 1) {
        throw std::invalid_argument("Must have at least one data slice.");
    }
    if (lastSlice > this->_lastSlice) {
        throw std::invalid_argument("Trying to plot too many data slices.");
    }

    // Set canvas properties
    canvas->SetWindowSize(800, 500);

    // Draw the cumulative plots layer by layer, starting at the back
    for (Int_t i = bunchCount; i > 0; i--) {
        this->_PlotBunchLayer(canvas, i, lastSlice, (i==bunchCount));
    }

    // // Apply styles
    this->_StyleBunches(canvas, bunchCount, bunchNames, xmin, xmax, ymin, ymax);

    // Update canvas
    canvas->Update();
    canvas->Paint();

    // Print to file
    canvas->Print("bunch-count.eps", "eps");
}

void TImpactTree::_PlotBunchLayer(
    TCanvas *canvas,
    Int_t currentLayer,
    Int_t lastSlice,
    Bool_t isBackLayer
)
{
    // Build correct settings for current layer
    std::string axesDefinition =
        this->_BuildCumulativePlotString("bunches", "n", "z", currentLayer);
    std::string graphName = "graph" + std::to_string(currentLayer);
    std::string plotLocation = "";
    if (!isBackLayer) plotLocation = "same";

    // Draw graph
    canvas->Update();
    this->Draw(axesDefinition.c_str(), "", plotLocation.c_str(), lastSlice, 0);

    // Rename graph
    this->_RenameCurrentGraph(canvas, graphName.c_str());
}

// Methods to apply styles for different plot types
void TImpactTree::_StyleBunches(
    TCanvas *canvas,
    Int_t bunchCount,
    std::vector<std::string> bunchNames,
    Double_t xmin,
    Double_t xmax,
    Double_t ymin,
    Double_t ymax
)
{
    // Get objects
    TFrame *frame = canvas->GetFrame();
    TPaveText *titleText = (TPaveText *) canvas->GetPrimitive("title");
    TH1 *hist = (TH1 *) canvas->GetPrimitive("htemp");
    std::string graphName = "";
    TGraph *graph;

    // Set up background
    frame->SetLineWidth(0);
    titleText->Clear();
    canvas->SetGridx(false);
    canvas->SetGridy(true);

    // Set axes options
    // - font code 132 is Times New Roman, medium, regular, scalable
    // x-axis
    hist->GetXaxis()->SetTicks("-");
    hist->GetXaxis()->SetTickSize(0.01);
    hist->GetXaxis()->SetTitleOffset(-1.0);
    hist->GetXaxis()->SetLabelOffset(-0.04);
    hist->GetXaxis()->SetTitle("z-position (m)");
    hist->GetXaxis()->SetTitleFont(132);
    hist->GetXaxis()->SetTitleSize(0.045);
    hist->GetXaxis()->SetLabelFont(132);
    hist->GetXaxis()->SetLabelSize(0.03);
    hist->GetXaxis()->SetLimits(xmin, xmax);
    hist->GetXaxis()->SetRangeUser(xmin, xmin);
    // y-axis
    hist->GetYaxis()->SetTicks("+");
    hist->GetYaxis()->SetTickSize(0.01);
    hist->GetYaxis()->SetTitleOffset(-0.8);
    hist->GetYaxis()->SetLabelOffset(-0.01);
    hist->GetYaxis()->SetTitle("Total number of macro-particles");
    hist->GetYaxis()->SetTitleFont(132);
    hist->GetYaxis()->SetTitleSize(0.045);
    hist->GetYaxis()->SetLabelFont(132);
    hist->GetYaxis()->SetLabelSize(0.03);
    hist->GetYaxis()->SetLimits(ymin, ymax);
    hist->GetYaxis()->SetRangeUser(ymin, ymax);

    // Add legend
    TLegend *legend = new TLegend(0.540, 0.122, 0.841, 0.292);
    legend->SetTextFont(132);
    legend->SetTextSize(0.03);

    // Set graph draw options
    for (Int_t i = 1; i <= bunchCount; i++) {
        graphName = "graph" + std::to_string(i);
        graph = (TGraph *) canvas->GetPrimitive(graphName.c_str());
        graph->SetDrawOption("B");
        switch (i % 4) {
        case 1:
            graph->SetFillColor(38);   // Blue
            break;
        case 2:
            graph->SetFillColor(623);  // Salmon red
            break;
        case 3:
            graph->SetFillColor(30);   // Green
            break;
        case 0:
            graph->SetFillColor(42);   // Mustard
            break;
        }
        legend->AddEntry(graph, bunchNames.at(i-1).c_str(), "f");
    }

    // Update canvas
    legend->Draw();
    canvas->Update();
    canvas->Paint();
}

// Utility methods
// - rename the current graph
void TImpactTree::_RenameCurrentGraph(TCanvas *canvas, const char *name)
{
    TGraph *current_graph = (TGraph *) canvas->GetPrimitive("Graph");
    current_graph->SetName(name);
}

// - create the plot string for a cumulative plot
std::string TImpactTree::_BuildCumulativePlotString(
    std::string branchName,
    std::string prefix,
    std::string xaxis,
    Int_t variableCount
)
{
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
