// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018
// modified by Matt Easton, October 2019

#include <vector>
#include "TImpactData.h"
#include "Style_mje.C"

// Implements class `TImpactData`
ClassImp(TImpactData);

// Parameters
// - limit for bunch count, required for load method
Int_t    const _MAX_BUNCH_COUNT       = 99;
// - settings for bunch count plot
std::string    _BUNCHES_FILENAME      = "bunch-count.eps";
std::string    _BUNCHES_FILETYPE      = "eps";
std::string    _BUNCHES_CANVAS_NAME   = "impact_bunch_count_plot";
std::string    _BUNCHES_CANVAS_TITLE  = "Impact-T bunch count plot";
std::string    _BUNCHES_XAXIS_TITLE   = "z-position (m)";
std::string    _BUNCHES_YAXIS_TITLE   = "Total number of macro-particles";
Int_t    const _BUNCHES_CANVAS_WIDTH  =    802;
Int_t    const _BUNCHES_CANVAS_HEIGHT =    525;
Double_t const _BUNCHES_XMIN_DEFAULT  =    0.0;
Double_t const _BUNCHES_XMAX_DEFAULT  =    1.8;
Double_t const _BUNCHES_YMIN_DEFAULT  =  90000;
Double_t const _BUNCHES_YMAX_DEFAULT  = 102000;

// Default constructor
TImpactData::TImpactData():
    _bunchCount(1), _sliceCount(0), _firstSlice(0), _lastSlice(0)
{
    this->SetDefaultBunchNames();
    this->_CreateTrees();
}

// Constructor given bunch count only
TImpactData::TImpactData(Int_t bunchCount):
    _bunchCount(bunchCount), _sliceCount(0), _firstSlice(0), _lastSlice(0)
{
    this->SetDefaultBunchNames();
    this->_CreateTrees();
}

// Constructor given bunch count and bunch names
TImpactData::TImpactData(Int_t bunchCount, std::vector<std::string> bunchNames):
   _bunchCount(bunchCount), _sliceCount(0), _firstSlice(0), _lastSlice(0)
{
    this->SetBunchNames(bunchNames);
    this->_CreateTrees();
}

// Default destructor
TImpactData::~TImpactData()
{
    this->_bunchTree->Delete();
}

// Methods to create data structures
void TImpactData::_CreateTrees()
{
    this->_bunchTree = new TTree();
}

// Methods to access members
Int_t TImpactData::BunchCount() const
{
    return this->_bunchCount;
}

Int_t TImpactData::SliceCount() const
{
    return this->_sliceCount;
}

std::vector<std::string> TImpactData::GetBunchNames() const
{
    return this->_bunchNames;
}

Int_t TImpactData::GetFirstSlice() const
{
    return this->_firstSlice;
}

Int_t TImpactData::GetLastSlice() const
{
    return this->_lastSlice;
}

void TImpactData::SetDefaultBunchNames()
{
    std::vector<std::string> bunchNames;
    Int_t bunchCount = this->BunchCount();
    for (Int_t i = 1; i <= bunchCount; i++) {
        bunchNames.push_back("Bunch " + std::to_string(i));
    }
    this->_bunchNames = bunchNames;
}

void TImpactData::SetBunchNames(std::vector<std::string> bunchNames)
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

void TImpactData::SetFirstSlice(Int_t firstSlice)
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

void TImpactData::SetLastSlice(Int_t lastSlice)
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
void TImpactData::Load()
{
    // Load all data
    this->_Load(this->_bunchCount);
    // Output data summary
    this->Print();
}

// - wrapper method to load all data types
void TImpactData::_Load(Int_t bunchCount)
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
}

// - particle count data from `fort.11`
void TImpactData::_LoadBunches(Int_t bunchCount)
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
    this->_bunchTree->Branch("bunches", &step, leafDefinition.c_str());

    // Read in data from `fort.11`
    ifstream infile("fort.11");
    while (1) {
        if (!infile.good()) break;
        infile >> step.i >> step.t >> step.z >> step.bunches;
        for (Int_t i = 0; i < bunchCount; i++) {
            infile >> step.count[i];
        }
        this->_bunchTree->GetBranch("bunches")->Fill();
    }
    infile.close();

    // Set number of slices for the tree object
    this->_sliceCount = this->_bunchTree->GetBranch("bunches")->GetEntries();
    this->_UpdateSliceCount(this->_sliceCount);
    this->_firstSlice = 1;
    this->_lastSlice = this->_sliceCount - 1;
}

// Methods to output data
// - publicly accessible method
void TImpactData::Print()
{
    // Print tree summary
    printf("Bunch data tree:\n");
    this->_bunchTree->Print();
}

// Methods to produce different plot types
// - bunch count cumulative plot for data loaded from `fort.11`
void TImpactData::PlotBunches()
{
    // Default values
    Long_t firstSlice = 0;
    Long_t lastSlice = this->_lastSlice;
    Double_t xmin = _BUNCHES_XMIN_DEFAULT;
    Double_t xmax = _BUNCHES_XMAX_DEFAULT;
    Double_t ymin = _BUNCHES_YMIN_DEFAULT;
    Double_t ymax = _BUNCHES_YMAX_DEFAULT;
    this->PlotBunches(firstSlice, lastSlice, xmin, xmax, ymin, ymax);
}

void TImpactData::PlotBunches(
    Long_t firstSlice,
    Long_t lastSlice,
    Double_t xmin,
    Double_t xmax,
    Double_t ymin,
    Double_t ymax
)
{
    // Check parameters
    if (firstSlice < 0) {
        throw std::invalid_argument("Slice values cannot be negative.");
    }
    if (firstSlice > this->_lastSlice) {
        throw std::invalid_argument("First slice value too high.");
    }
    if (lastSlice < 0) {
        throw std::invalid_argument("Slice values cannot be negative.");
    }
    if (lastSlice > this->_lastSlice) {
        throw std::invalid_argument("Last slice value too high.");
    }
    Int_t bunchCount = this->_bunchCount;
    std::vector<std::string> bunchNames = this->_bunchNames;

    // Create canvas
    this->_CreateCanvas(
        _BUNCHES_CANVAS_NAME.c_str(),
        _BUNCHES_CANVAS_TITLE.c_str(),
        _BUNCHES_CANVAS_WIDTH,
        _BUNCHES_CANVAS_HEIGHT
    );

    // Draw the cumulative plots layer by layer, starting at the back
    for (Int_t i = bunchCount; i > 0; i--) {
        this->_PlotBunchLayer(i, lastSlice, (i==bunchCount));
    }

    // Apply styles
    this->_StyleBunches(bunchCount, bunchNames, xmin, xmax, ymin, ymax);

    // Print to file
    this->_PrintCanvas(
        _BUNCHES_CANVAS_NAME.c_str(),
        _BUNCHES_FILENAME.c_str(),
        _BUNCHES_FILETYPE.c_str()
    );
}

void TImpactData::_PlotBunchLayer(
    Int_t currentLayer,
    Int_t lastSlice,
    Bool_t isBackLayer
)
{
    // Build correct settings for current layer
    std::string axesDefinition =
        this->_BuildCumulativePlotString("bunches", "n", "z", currentLayer);
    std::string graphName = "graph" + std::to_string(currentLayer);
    std::string plotOptions = "";
    if (!isBackLayer) plotOptions = "same";

    // Draw graph
    TCanvas *canvas = (TCanvas *)(
        gROOT->GetListOfCanvases()->FindObject(_BUNCHES_CANVAS_NAME.c_str())
    );
    canvas->cd();
    this->_bunchTree->Draw(
        axesDefinition.c_str(),
        "",
        plotOptions.c_str(),
        lastSlice,
        0);

    // Rename graph
    this->_RenameCurrentGraph(graphName.c_str());
}

// Methods to apply styles for different plot types
void TImpactData::_StyleBunches(
    Int_t bunchCount,
    std::vector<std::string> bunchNames,
    Double_t xmin,
    Double_t xmax,
    Double_t ymin,
    Double_t ymax
)
{
    // Apply my style settings
    load_style_mje();
    gROOT->SetStyle("mje");

    // Get objects
    TCanvas *canvas = (TCanvas *)(
        gROOT->GetListOfCanvases()->FindObject(_BUNCHES_CANVAS_NAME.c_str())
    );
    canvas->cd();
    TFrame *frame = canvas->GetFrame();
    TPaveText *titleText = (TPaveText *)(canvas->GetPrimitive("title"));
    TH1 *hist = (TH1 *)(canvas->GetPrimitive("htemp"));
    std::string graphName = "";
    TGraph *graph;

    // Set up background
    frame->SetLineWidth(0);
    if (titleText) {
        titleText->Clear();
    }
    canvas->SetGridx(false);
    canvas->SetGridy(true);

    // Set axes options
    // - font code 132 is Times New Roman, medium, regular, scalable
    // x-axis
    hist->GetXaxis()->SetTicks("-");
    hist->GetXaxis()->SetTickSize(0.01);
    hist->GetXaxis()->SetTitleOffset(-1.0);
    hist->GetXaxis()->SetLabelOffset(-0.04);
    hist->GetXaxis()->SetTitle(_BUNCHES_XAXIS_TITLE.c_str());
    hist->GetXaxis()->SetTitleFont(132);
    hist->GetXaxis()->SetTitleSize(0.05);
    hist->GetXaxis()->CenterTitle(kTRUE);
    hist->GetXaxis()->SetLabelFont(132);
    hist->GetXaxis()->SetLabelSize(0.035);
    hist->GetXaxis()->SetLimits(xmin, xmax);
    hist->GetXaxis()->SetRangeUser(xmin, xmin);
    // y-axis
    hist->GetYaxis()->SetTicks("+");
    hist->GetYaxis()->SetTickSize(0.01);
    hist->GetYaxis()->SetTitleOffset(-0.8);
    hist->GetYaxis()->SetLabelOffset(-0.01);
    hist->GetYaxis()->SetTitle(_BUNCHES_YAXIS_TITLE.c_str());
    hist->GetYaxis()->SetTitleFont(132);
    hist->GetYaxis()->SetTitleSize(0.05);
    hist->GetYaxis()->CenterTitle(kTRUE);
    hist->GetYaxis()->SetLabelFont(132);
    hist->GetYaxis()->SetLabelSize(0.035);
    hist->GetYaxis()->SetLimits(ymin, ymax);
    hist->GetYaxis()->SetRangeUser(ymin, ymax);

    // Add legend
    TLegend *legend = new TLegend(0.540, 0.122, 0.841, 0.292);
    legend->SetTextFont(132);
    legend->SetTextSize(0.03);
    legend->SetLineColor(17);
    legend->SetLineStyle(1);
    legend->SetLineWidth(1);

    // Set graph draw options
    for (Int_t i = 1; i <= bunchCount; i++) {
        graphName = "graph" + std::to_string(i);
        graph = (TGraph *)(canvas->GetPrimitive(graphName.c_str()));
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
        graph->SetLineWidth(0);
        graph->SetLineStyle(0);
        legend->AddEntry(graph, bunchNames.at(i-1).c_str(), "f");
    }

    // Axes on top
    hist->GetXaxis()->Pop();
    hist->GetYaxis()->Pop();

    // Update canvas
    legend->Draw();
    canvas->Update();
    canvas->Paint();
}

// Utility methods
// - rename the current graph
void TImpactData::_RenameCurrentGraph(const char *name)
{
    TGraph *thisGraph = (TGraph *)(gPad->GetPrimitive("Graph"));
    if (thisGraph) {
        thisGraph->SetName(name);
    }
}

// - create a new canvas
void TImpactData::_CreateCanvas(
    const char *name,
    const char *title,
    const Int_t width,
    const Int_t height
)
{
    TCanvas *canvas = (TCanvas *)(gROOT->GetListOfCanvases()->FindObject(name));
    if (!canvas) {
        canvas = gROOT->MakeDefCanvas();
    }
    canvas->SetName(name);
    canvas->SetTitle(title);
    canvas->SetWindowSize(width, height);
    canvas->cd();
}

// - print a canvas to file
void TImpactData::_PrintCanvas(
    const char *name,
    const char *filename,
    const char *filetype
)
{
    TCanvas *canvas = (TCanvas *)(gROOT->GetListOfCanvases()->FindObject(name));
    if (!canvas) {
        std::string errorString = "Could not find canvas ";
        errorString += name;
        throw std::invalid_argument(errorString.c_str());
    }
    canvas->Update();
    canvas->Paint();
    canvas->Print(filename, filetype);
}

// - create the plot string for a cumulative plot
std::string TImpactData::_BuildCumulativePlotString(
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

// - update the number of time slice entries in the trees
void TImpactData::_UpdateSliceCount(Long_t newCount)
{
    // Bunch count tree
    Long_t currentCount = this->_bunchTree->GetEntries();
    if (newCount > currentCount) {
        this->_bunchTree->SetEntries(newCount);
    }
}
