// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include <vector>
#include "TImpactTree.h"
#include "Style_mje.C"

// Implements class `TImpactTree`
ClassImp(TImpactTree);

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
// - settings for final energy plot
std::string    _ENERGY_FILENAME      = "energy.eps";
std::string    _ENERGY_FILETYPE      = "eps";
std::string    _ENERGY_CANVAS_NAME   = "impact_final_energy_plot";
std::string    _ENERGY_CANVAS_TITLE  = "Impact-T final energy plot";
std::string    _ENERGY_XAXIS_TITLE   = "Final energy (MeV)";
std::string    _ENERGY_YAXIS_TITLE   = "Number of macro-particles";
Int_t    const _ENERGY_CANVAS_WIDTH  =    802;
Int_t    const _ENERGY_CANVAS_HEIGHT =    525;
Int_t    const _ENERGY_BINS_DEFAULT  =    100;
Double_t const _ENERGY_XMIN_DEFAULT  =    0.0;
Double_t const _ENERGY_XMAX_DEFAULT  =    1.1;

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
    this->_LoadEndSlice(bunchCount);

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
        this->GetBranch("bunches")->Fill();
    }
    infile.close();

    // Set number of slices for the tree object
    this->_sliceCount = this->GetBranch("bunches")->GetEntries();
    this->_firstSlice = 1;
    this->_lastSlice = this->_sliceCount - 1;
}

// - end slice data from `rfq1.dst` etc.
void TImpactTree::_LoadEndSlice(Int_t bunchCount)
{
    std::string filename = "";
    std::string branchname = "";
    for (Int_t i = 1; i <= bunchCount; i++){
        filename = "rfq" + std::to_string(i) + ".dst";
        branchname = "endslice.bunch" + std::to_string(i);
        this->_LoadDSTParticleData(filename, branchname);
    }
}

// - load particle data from a `.dst` file into a given branch
void TImpactTree::_LoadDSTParticleData(
    std::string filename,
    std::string branchname
)
{
    Int_t Npt = _GetDSTParticleCount(filename);
    Double_t slice[6];
    std::string leafDefinition = "x/D:xp/D:y/D:yp/D:phi/D:W/D";
    this->Branch(branchname.c_str(), &slice, leafDefinition.c_str());
    ifstream infile(filename, std::ios::in | std::ios::binary);
    infile.seekg(23); // skip headers
    for (Int_t i = 1; i <= Npt; i++) {
        if (!infile.good()) break;
        infile.read((char *)(&slice), 48);
        this->GetBranch(branchname.c_str())->Fill();
    }
    infile.close();
}

// - read the number of particles from a given `.dst` file
Int_t TImpactTree::_GetDSTParticleCount(std::string filename)
{
    Int_t Npt = 0;
    ifstream infile(filename, std::ios::in | std::ios::binary);
    infile.seekg(2);
    infile.read((char *)&Npt, 4);
    infile.close();
    this->_UpdateParticleCount(Npt);
    return Npt;
}


// Methods to produce different plot types
// - bunch count cumulative plot for data loaded from `fort.11`
void TImpactTree::PlotBunches()
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

void TImpactTree::PlotBunches(
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

void TImpactTree::_PlotBunchLayer(
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
    this->Draw(axesDefinition.c_str(), "", plotOptions.c_str(), lastSlice, 0);

    // Rename graph
    this->_RenameCurrentGraph(graphName.c_str());
}

// - final energy histograms
void TImpactTree::PlotFinalEnergy(
    Int_t nbins = _ENERGY_BINS_DEFAULT,
    Double_t xmin = _ENERGY_XMIN_DEFAULT,
    Double_t xmax = _ENERGY_XMAX_DEFAULT
)
{
    Int_t bunchCount = this->_bunchCount;
    std::string branchName = "";
    std::string plotString = "";
    std::string plotOptions = "";
    std::string histName = "";

    // Create canvas
    this->_CreateCanvas(
        _ENERGY_CANVAS_NAME.c_str(),
        _ENERGY_CANVAS_TITLE.c_str(),
        _ENERGY_CANVAS_WIDTH,
        _ENERGY_CANVAS_HEIGHT
    );

    // Plot each histogram as a separate layer
    for (Int_t i = 1; i <= bunchCount; i++) {
        histName = _ENERGY_CANVAS_NAME + "_hist" + std::to_string(i);
        branchName = "endslice.bunch" + std::to_string(i);
        plotString = branchName + ".W";
        plotString += ">>" + histName + "("
            + std::to_string(nbins) + ","
            + std::to_string(xmin) + ","
            + std::to_string(xmax) + ")";
        if (i==1) {
            plotOptions = "hist";
        }
        else {
            plotOptions = "hist same";
        }
        TBranch *thisBranch = this->GetBranch(branchName.c_str());
        Long_t branchEntries = thisBranch->GetEntries();
        this->Draw(plotString.c_str(), "", plotOptions.c_str(), branchEntries);
    }

    // Apply styles
    this->_StyleFinalEnergy(this->_bunchCount, this->_bunchNames);

    // Print to file
    this->_PrintCanvas(
        _ENERGY_CANVAS_NAME.c_str(),
        _ENERGY_FILENAME.c_str(),
        _ENERGY_FILETYPE.c_str()
    );
}

// Methods to apply styles for different plot types
void TImpactTree::_StyleBunches(
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

void TImpactTree::_StyleFinalEnergy(
    Int_t bunchCount,
    std::vector<std::string> bunchNames
)
{
    // Apply my style settings
    load_style_mje();
    gROOT->SetStyle("mje");

    // Get objects
    TCanvas *canvas = (TCanvas *)(
        gROOT->GetListOfCanvases()->FindObject(_ENERGY_CANVAS_NAME.c_str())
    );
    canvas->cd();
    TFrame *frame = canvas->GetFrame();
    TPaveText *titleText = (TPaveText *)(canvas->GetPrimitive("title"));
    std::string histName = "";
    histName = _ENERGY_CANVAS_NAME + "_hist1";
    TH1 *hist = (TH1 *)(canvas->GetPrimitive(histName.c_str()));
    // std::string graphName = "";
    // TGraph *graph;

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
    hist->GetXaxis()->SetTitle(_ENERGY_XAXIS_TITLE.c_str());
    hist->GetXaxis()->SetTitleFont(132);
    hist->GetXaxis()->SetTitleSize(0.05);
    hist->GetXaxis()->CenterTitle(kTRUE);
    hist->GetXaxis()->SetLabelFont(132);
    hist->GetXaxis()->SetLabelSize(0.035);
    // y-axis
    hist->GetYaxis()->SetTicks("+");
    hist->GetYaxis()->SetTickSize(0.01);
    hist->GetYaxis()->SetTitleOffset(-1.02);
    hist->GetYaxis()->SetLabelOffset(-0.01);
    hist->GetYaxis()->SetTitle(_ENERGY_YAXIS_TITLE.c_str());
    hist->GetYaxis()->SetTitleFont(132);
    hist->GetYaxis()->SetTitleSize(0.05);
    hist->GetYaxis()->CenterTitle(kTRUE);
    hist->GetYaxis()->SetLabelFont(132);
    hist->GetYaxis()->SetLabelSize(0.035);

    // Add legend
    TLegend *legend = new TLegend(0.11, 0.9, 0.51, 0.7);
    legend->SetTextFont(132);
    legend->SetTextSize(0.03);
    legend->SetLineColor(17);
    legend->SetLineStyle(1);
    legend->SetLineWidth(1);

    // Set histogram draw options
    for (Int_t i = 1; i <= bunchCount; i++) {
        histName = _ENERGY_CANVAS_NAME + "_hist" + std::to_string(i);
        hist = (TH1 *)(canvas->GetPrimitive(histName.c_str()));
        switch (i % 4) {
        case 1:
            hist->SetFillColor(38);   // Blue
            hist->SetLineColor(kBlue + 3);
            break;
        case 2:
            hist->SetFillColor(623);  // Salmon red
            hist->SetLineColor(kRed + 3);
            break;
        case 3:
            hist->SetFillColor(30);   // Green
            hist->SetLineColor(kGreen + 3);
            break;
        case 0:
            hist->SetFillColor(42);   // Mustard
            hist->SetLineColor(kYellow + 3);
            break;
        }
        hist->SetLineWidth(1);
        hist->SetLineStyle(1);
        legend->AddEntry(hist, bunchNames.at(i-1).c_str(), "f");
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
void TImpactTree::_RenameCurrentGraph(const char *name)
{
    TGraph *thisGraph = (TGraph *)(gPad->GetPrimitive("Graph"));
    if (thisGraph) {
        thisGraph->SetName(name);
    }
}

// - create a new canvas
void TImpactTree::_CreateCanvas(
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
void TImpactTree::_PrintCanvas(
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

// - update the number of entries in the tree
void TImpactTree::_UpdateParticleCount(Long_t newCount)
{
    Long_t currentCount = this->GetEntries();
    if (newCount > currentCount) {
        this->SetEntries(newCount);
    }
}
