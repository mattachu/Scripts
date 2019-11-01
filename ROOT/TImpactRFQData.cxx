// Class for loading, plotting and manipulating Impact-T RFQ simulation data
// written by Matt Easton (see http://matteaston.net/work), October 2019
// inherits from the main class TImpactData

#include <vector>
#include "TImpactRFQData.h"
#include "Style_mje.C"

// Implements class `TImpactRFQData`
ClassImp(TImpactRFQData);

// Parameters
// - settings for trees and branches
char const    *_ENDSLICE_TREENAME    = "endslice";
char const    *_ENDSLICE_TREETITLE   = "End slice data";
std::string    _ENDSLICE_BRANCHNAME  = "endslice";
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
TImpactRFQData::TImpactRFQData():
    TImpactData(), _cellCount(0), _firstCell(0), _lastCell(0)
{
    this->_CreateNullTrees();
}

// Constructor given bunch count only
TImpactRFQData::TImpactRFQData(Int_t bunchCount):
    TImpactData(bunchCount), _cellCount(0), _firstCell(0), _lastCell(0)
{
    this->_CreateNullTrees();
}

// Constructor given bunch count and bunch names
TImpactRFQData::TImpactRFQData(Int_t bunchCount, std::vector<std::string> bunchNames):
   TImpactData(bunchCount, bunchNames),
   _cellCount(0), _firstCell(0), _lastCell(0)
{
    this->_CreateNullTrees();
}

// Default destructor
TImpactRFQData::~TImpactRFQData()
{
    this->_DeleteAllTrees();
}

// Methods to create data structures
//   - overloads TImpactData
void TImpactRFQData::_CreateNullTrees()
{
    TImpactData::_CreateNullTrees();
    this->_endTree = nullptr;
}

//   - tree for end slice data from `.dst` file
void TImpactRFQData::_CreateEndTree()
{
    this->_endTree = new TTree(_ENDSLICE_TREENAME, _ENDSLICE_TREETITLE);
}

//   - overloads TImpactData
void TImpactRFQData::_DeleteAllTrees()
{
    TImpactData::_DeleteAllTrees();
    this->_DeleteEndTree();
}

//   - tree for end slice data from `.dst` file
void TImpactRFQData::_DeleteEndTree()
{
    try {
        if (this->_endTree) {
            this->_endTree->Reset();
            this->_endTree->Delete();
        }
    } catch (...)  {}
    this->_endTree = nullptr;
}

// Methods to access members
Int_t TImpactRFQData::CellCount() const
{
    return this->_cellCount;
}

Int_t TImpactRFQData::GetFirstCell() const
{
    return this->_firstCell;
}

Int_t TImpactRFQData::GetLastCell() const
{
    return this->_lastCell;
}

void TImpactRFQData::SetFirstCell(Int_t firstCell)
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

void TImpactRFQData::SetLastCell(Int_t lastCell)
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

TTree *TImpactRFQData::GetTree(std::string treeName)
{
    if (treeName == _ENDSLICE_TREENAME) {
        return this->_endTree;
    }
    else {
        return TImpactData::GetTree(treeName);
    }
    return nullptr;
}

// Methods to load data from Impact-T output files
// - publicly accessible method
//   - overloads TImpactData
void TImpactRFQData::Load(std::vector<Int_t> bpmList = {})
{
    // Set up data structures into which to load data
    this->_DeleteAllTrees();
    this->_CreateDefaultTrees();
    if (!bpmList.empty()) {
        this->_CreateBPMTree();
    }
    this->_CreateEndTree();

    // Load all data
    this->_LoadAll(this->_bunchCount, bpmList);

    // Output data summary
    this->Print();
}

// - wrapper method to load all data types
//   - overloads TImpactData
void TImpactRFQData::_LoadAll(Int_t bunchCount, std::vector<Int_t> bpmList = {})
{
    // Load standard Impact-T data
    TImpactData::_LoadAll(bunchCount, bpmList);
    // Load data types specific to RFQ
    this->_LoadEndSlice(bunchCount);
}

// - end slice data from `rfq1.dst` etc.
void TImpactRFQData::_LoadEndSlice(Int_t bunchCount)
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

    // Check for tree
    if (!this->_endTree) {
        this->_CreateEndTree();
    }

    // Load data to a new branch for each bunch
    std::string filename = "";
    std::string branchname = "";
    for (Int_t i = 1; i <= bunchCount; i++){
        filename = "rfq" + std::to_string(i) + ".dst";
        branchname = _ENDSLICE_BRANCHNAME + ".bunch" + std::to_string(i);
        this->_LoadDSTParticleData(filename, branchname);
    }
}

// - load particle data from a `.dst` file into a given branch
void TImpactRFQData::_LoadDSTParticleData(
    std::string filename,
    std::string branchname
)
{
    // Check for file
    if (!this->_FileExists(filename)) {
        throw std::runtime_error("Cannot find file: " + filename);
    }

    // Check for tree
    if (!this->_endTree) {
        throw std::runtime_error(
            "Cannot load DST data as tree structure is not available."
        );
    }

    // Announce status
    printf("Loading end slice data from file `%s`\n", filename.c_str());

    // Create structure to hold data
    Int_t Npt = _GetDSTParticleCount(filename);
    Double_t slice[6];
    std::string leafDefinition = "x/D:xp/D:y/D:yp/D:phi/D:W/D";

    // Create a branch for the given data
    this->_endTree->Branch(branchname.c_str(), &slice, leafDefinition.c_str());

    // Read in data from the given filename
    ifstream infile(filename, std::ios::in | std::ios::binary);
    infile.seekg(23); // skip headers
    for (Int_t i = 1; i <= Npt; i++) {
        if (!infile.good()) break;
        infile.read((char *)(&slice), 48);
        this->_endTree->GetBranch(branchname.c_str())->Fill();
    }
    infile.close();
}

// - read the number of particles from a given `.dst` file
Int_t TImpactRFQData::_GetDSTParticleCount(std::string filename)
{
    Int_t Npt = 0;
    ifstream infile(filename, std::ios::in | std::ios::binary);
    infile.seekg(2);
    infile.read((char *)&Npt, 4);
    infile.close();
    this->_UpdateParticleCount(Npt);
    return Npt;
}

// Methods to output data
// - publicly accessible method
void TImpactRFQData::Print()
{
    // Print standard Impact data output
    TImpactData::Print();
    // Print end slice tree summary
    if (this->_endTree) {
        printf("End-slice data tree:\n");
        this->_endTree->Print();
    }
}

// Methods to produce different plot types
// - final energy histograms from `rfq1.dst`
void TImpactRFQData::PlotFinalEnergy(
    Int_t nbins = _ENERGY_BINS_DEFAULT,
    Double_t xmin = _ENERGY_XMIN_DEFAULT,
    Double_t xmax = _ENERGY_XMAX_DEFAULT
)
{
    // Check for tree
    if (!this->_endTree) {
        throw std::runtime_error(
            "Cannot load end slice data as tree structure is not available."
        );
    }

    // Set detaults
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
        branchName = _ENDSLICE_BRANCHNAME + ".bunch" + std::to_string(i);
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
        TBranch *thisBranch = this->_endTree->GetBranch(branchName.c_str());
        Long_t branchEntries = thisBranch->GetEntries();
        this->_endTree->Draw(
            plotString.c_str(),
            "",
            plotOptions.c_str(),
            branchEntries);
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
void TImpactRFQData::_StyleFinalEnergy(
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
    if (!canvas) {
        throw std::runtime_error(
            "Cannot find canvas object."
        );
    }
    canvas->cd();
    TFrame *frame = canvas->GetFrame();
    if (!frame) {
        throw std::runtime_error(
            "Cannot find plot frame object."
        );
    }
    TPaveText *titleText = (TPaveText *)(canvas->GetPrimitive("title"));
    std::string histName = "";
    histName = _ENERGY_CANVAS_NAME + "_hist1";
    TH1 *hist = (TH1 *)(canvas->GetPrimitive(histName.c_str()));
    if (!hist) {
        throw std::runtime_error(
            "Cannot find histogram object."
        );
    }

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
// - update the number of particle entries in the trees
void TImpactRFQData::_UpdateParticleCount(Long_t newCount)
{
    // Run standard Impact data method
    TImpactData::_UpdateParticleCount(newCount);
    // Also update end slice tree
    if (this->_endTree) {
        Long_t currentCount = this->_endTree->GetEntries();
        if (newCount > currentCount) {
            this->_endTree->SetEntries(newCount);
        }
    }
}
