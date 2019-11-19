// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018
// modified by Matt Easton, October 2019

#include "TImpactData.h"
#include <iostream>
#include <string>
#include <vector>
#include "Style_mje.C"

// Implements class `TImpactData`
ClassImp(TImpactData);

// Parameters
// - limit for bunch count, required for load method
const Int_t    _MAX_BUNCH_COUNT       = 99;
// - settings for trees and branches
const char    *_BUNCHES_TREENAME      = "bunches";
const char    *_BUNCHES_TREETITLE     = "Bunch data";
const char    *_BUNCHES_BRANCHNAME    = "bunches";
const char    *_PHASE_TREENAME        = "phase";
const char    *_PHASE_TREETITLE       = "Phase space output data";
const char    *_PHASE_BRANCHNAME      = "phase.out";
const char    *_ENDSLICE_TREENAME     = "endslice";
const char    *_ENDSLICE_TREETITLE    = "End slice data";
const char    *_ENDSLICE_BRANCHNAME   = "endslice";
// - settings for bunch count plot
const char    *_BUNCHES_FILENAME      = "bunch-count.eps";
const char    *_BUNCHES_FILETYPE      = "eps";
const char    *_BUNCHES_CANVAS_NAME   = "impact_bunch_count_plot";
const char    *_BUNCHES_CANVAS_TITLE  = "Impact-T bunch count plot";
const char    *_BUNCHES_XAXIS_TITLE   = "z-position (m)";
const char    *_BUNCHES_YAXIS_TITLE   = "Total number of macro-particles";
const Int_t    _BUNCHES_CANVAS_WIDTH  =    802;
const Int_t    _BUNCHES_CANVAS_HEIGHT =    525;
// - settings for phase space plot
const char    *_PHASE_FILENAME        = "phase";
const char    *_PHASE_FILEEXTENSION   = ".eps";
const char    *_PHASE_FILETYPE        = "eps";
const char    *_PHASE_CANVAS_NAME     = "impact_phase_plot";
const char    *_PHASE_CANVAS_TITLE    = "Impact-T phase space plot";
const Int_t    _PHASE_CANVAS_WIDTH    = 802;
const Int_t    _PHASE_CANVAS_HEIGHT   = 825;
// - settings for special phase space numbers
const Int_t    _PHASE_START           = 40;
const Int_t    _PHASE_END             = 50;
// - settings for final energy plot
const char    *_ENERGY_FILENAME       = "energy.eps";
const char    *_ENERGY_FILETYPE       = "eps";
const char    *_ENERGY_CANVAS_NAME    = "impact_final_energy_plot";
const char    *_ENERGY_CANVAS_TITLE   = "Impact-T final energy plot";
const char    *_ENERGY_XAXIS_TITLE    = "Final energy (MeV)";
const char    *_ENERGY_YAXIS_TITLE    = "Number of macro-particles";
const Int_t    _ENERGY_CANVAS_WIDTH   = 802;
const Int_t    _ENERGY_CANVAS_HEIGHT  = 525;
const Int_t    _ENERGY_BINS_DEFAULT   = 100;

// Default constructor
TImpactData::TImpactData():
    _bunchCount(1), _sliceCount(0), _firstSlice(0), _lastSlice(0),
    _particleCount(0)
{
    this->SetDefaultBunchNames();
    this->_CreateNullTrees();
}

// Constructor given bunch count only
TImpactData::TImpactData(Int_t bunchCount):
    _bunchCount(bunchCount), _sliceCount(0), _firstSlice(0), _lastSlice(0),
    _particleCount(0)
{
    this->SetDefaultBunchNames();
    this->_CreateNullTrees();
}

// Constructor given bunch count and bunch names
TImpactData::TImpactData(Int_t bunchCount, std::vector<std::string> bunchNames):
   _bunchCount(bunchCount), _sliceCount(0), _firstSlice(0), _lastSlice(0),
   _particleCount(0)
{
    this->SetBunchNames(bunchNames);
    this->_CreateNullTrees();
}

// Default destructor
TImpactData::~TImpactData()
{
    this->_DeleteAllTrees();
}

// Methods to create and delete data structures
void TImpactData::_CreateNullTrees()
{
    this->_bunchTree = nullptr;
    this->_phaseTree = nullptr;
    this->_endTree = nullptr;
}

void TImpactData::_CreateDefaultTrees()
{
    this->_CreateBunchTree();
    this->_CreatePhaseTree();
}

void TImpactData::_CreateBunchTree()
{
    try {
        this->_DeleteBunchTree();
    }
    catch (...) {}
    this->_bunchTree = new TTree(_BUNCHES_TREENAME, _BUNCHES_TREETITLE);
}

void TImpactData::_CreatePhaseTree()
{
    try {
        this->_DeletePhaseTree();
    } catch (...) {}
    this->_phaseTree = new TTree(_PHASE_TREENAME, _PHASE_TREETITLE);
}

void TImpactData::_CreateEndTree()
{
    this->_endTree = new TTree(_ENDSLICE_TREENAME, _ENDSLICE_TREETITLE);
}

void TImpactData::_DeleteAllTrees()
{
    this->_DeleteBunchTree();
    this->_DeletePhaseTree();
    this->_DeleteEndTree();
}

void TImpactData::_DeleteBunchTree()
{
    try {
        if (this->_bunchTree) {
            this->_bunchTree->Reset();
            this->_bunchTree->Delete();
        }
    }
    catch (...)  {}
    this->_bunchTree = nullptr;
}

void TImpactData::_DeletePhaseTree()
{
    try {
        if (this->_phaseTree) {
            this->_phaseTree->Reset();
            this->_phaseTree->Delete();
        }
    } catch (...)  {}
    this->_phaseTree = nullptr;
}

void TImpactData::_DeleteEndTree()
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
const Int_t TImpactData::BunchCount() const
{
    return this->_bunchCount;
}

const Int_t TImpactData::SliceCount() const
{
    return this->_sliceCount;
}

const Int_t TImpactData::ParticleCount() const
{
    return this->_particleCount;
}

const std::vector<std::string> TImpactData::GetBunchNames() const
{
    return this->_bunchNames;
}

const Int_t TImpactData::GetFirstSlice() const
{
    return this->_firstSlice;
}

const Int_t TImpactData::GetLastSlice() const
{
    return this->_lastSlice;
}

TTree *TImpactData::GetTree(std::string treeName) const
{
    if (treeName == _BUNCHES_TREENAME) {
        return this->_bunchTree;
    }
    else {
        if (treeName == _PHASE_TREENAME) {
            return this->_phaseTree;
        }
        else {
            if (treeName == _ENDSLICE_TREENAME) {
                return this->_endTree;
            }
            else {
                throw std::invalid_argument("No tree named " + treeName + ".");
            }
        }
    }
    return nullptr;
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
    if (bunchNames.size() < this->_bunchCount) {
        printf("Warning: not enough bunch names given, using some default values.\n");
        for (Int_t i = bunchNames.size()+1; i <= this->_bunchCount; i++) {
            bunchNames.push_back("Bunch " + std::to_string(i));
        }
    }
    else if (bunchNames.size() > this->_bunchCount) {
        printf("Warning: too many bunch names given, some names not used.\n");
    }
    bunchNames.resize(this->_bunchCount);
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
// - publicly accessible methods
void TImpactData::Load()
{
    std::vector<Int_t> bpmList = {};
    this->Load(bpmList);
}

void TImpactData::Load(Int_t bpmNumber)
{
    std::vector<Int_t> bpmList = {bpmNumber};
    this->Load(bpmList);
}

void TImpactData::Load(std::vector<Int_t> bpmList)
{
    // Set up data structures into which to load data
    this->_DeleteAllTrees();
    this->_CreateDefaultTrees();

    // Load all data
    this->_LoadAll(this->_bunchCount, bpmList);

    // Output data summary
    this->Print();
}

// - wrapper method to load all data types
void TImpactData::_LoadAll(Int_t bunchCount, std::vector<Int_t> bpmList = {})
{
    this->_LoadBunches(bunchCount);
    this->_LoadPhaseSpaceData(this->_bunchCount, _PHASE_START);
    if (!bpmList.empty()) {
        for (
            std::vector<Int_t>::iterator it = bpmList.begin();
            it != bpmList.end();
            ++it
        )
        {
            this->_LoadPhaseSpaceData(this->_bunchCount, *it);
        }
    }
    this->_LoadPhaseSpaceData(this->_bunchCount, _PHASE_END);
    if (this->_FileExists("rfq1.dst")) {
        this->_CreateEndTree();
        this->_LoadEndSlice(bunchCount);
    }
}

// - particle count data from `fort.11`
void TImpactData::_LoadBunches(Int_t bunchCount)
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

    // Check for file
    std::string filename = "fort.11";
    if (!this->_FileExists(filename)) {
        throw std::runtime_error("Cannot find file " + filename);
    }

    // Check for tree
    if (!this->_bunchTree) {
        throw std::runtime_error(
            "Cannot load bunches as tree structure is not available."
        );
    }

    // Announce status
    printf("Loading bunch data from file `%s`\n", filename.c_str());

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
    this->_bunchTree->Branch(
        _BUNCHES_BRANCHNAME,
        &step,
        leafDefinition.c_str()
    );

    // Read in data from `fort.11`
    std::ifstream infile(filename.c_str());
    while (1) {
        if (!infile.good()) break;
        infile >> step.i >> step.t >> step.z >> step.bunches;
        if (!infile.good()) break;
        for (Int_t i = 0; i < bunchCount; i++) {
            infile >> step.count[i];
        }
        this->_bunchTree->GetBranch(_BUNCHES_BRANCHNAME)->Fill();
    }
    infile.close();

    // Set number of slices for the tree object
    this->_UpdateSliceCount(
        this->_bunchTree->GetBranch(_BUNCHES_BRANCHNAME)->GetEntries()
    );
}

// - phase space data from output files `fort.xx` for multiple bunches
void TImpactData::_LoadPhaseSpaceData(Int_t bunchCount, Int_t locationNumber)
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
    if (!this->_phaseTree) {
        this->_CreatePhaseTree();
    }

    // Loop for each bunch
    for (Int_t i = 1; i <= bunchCount; i++) {
        this->_LoadPhaseSpace(i, locationNumber);
    }
}

// - phase space data from an output file `fort.xx`
void TImpactData::_LoadPhaseSpace(Int_t bunch, Int_t locationNumber)
{
    // Check for tree
    if (!this->_phaseTree) {
        this->_CreatePhaseTree();
    }

    // Check for file
    Int_t fileNumber = locationNumber + bunch - 1;
    std::string filename = "fort." + std::to_string(fileNumber);
    if (!this->_FileExists(filename)) {
        throw std::runtime_error("Cannot find file " + filename);
    }

    // Announce status
    printf("Loading phase space data from file `%s`\n", filename.c_str());

    // Create structure to hold data
    struct impact_particle_t {
        Double_t x = 0.0;
        Double_t px = 0.0;
        Double_t y = 0.0;
        Double_t py = 0.0;
        Double_t z = 0.0;
        Double_t pz = 0.0;
    };
    impact_particle_t particle;
    std::string leafDefinition = "x/D:px/D:y/D:py/D:z/D:pz/D";

    // Create a branch for the current phase space data
    std::string branchName =
        _PHASE_BRANCHNAME + std::to_string(locationNumber) +
        ".bunch" + std::to_string(bunch);
    this->_phaseTree->Branch(
        branchName.c_str(),
        &particle,
        leafDefinition.c_str()
    );

    // Read in data from file
    std::ifstream infile(filename.c_str());
    while (1) {
        if (!infile.good()) break;
        infile >> particle.x >> particle.px
               >> particle.y >> particle.py
               >> particle.z >> particle.pz;
        if (!infile.good()) break;
        this->_phaseTree->GetBranch(branchName.c_str())->Fill();
    }
    infile.close();

    // Set number of particles for the tree object
    this->_UpdateParticleCount(
        this->_phaseTree->GetBranch(branchName.c_str())->GetEntries()
    );
}

// - end slice data from `rfq1.dst` etc.
void TImpactData::_LoadEndSlice(Int_t bunchCount)
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
        branchname = _ENDSLICE_BRANCHNAME;
        branchname += ".bunch" + std::to_string(i);
        this->_LoadDSTParticleData(filename, branchname);
    }
}

// - load particle data from a `.dst` file into a given branch
void TImpactData::_LoadDSTParticleData(
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
    std::ifstream infile(filename, std::ios::in | std::ios::binary);
    infile.seekg(23); // skip headers
    for (Int_t i = 1; i <= Npt; i++) {
        if (!infile.good()) break;
        infile.read((char *)(&slice), 48);
        this->_endTree->GetBranch(branchname.c_str())->Fill();
    }
    infile.close();
}

// - read the number of particles from a given `.dst` file
Int_t TImpactData::_GetDSTParticleCount(std::string filename)
{
    Int_t Npt = 0;
    std::ifstream infile(filename, std::ios::in | std::ios::binary);
    infile.seekg(2);
    infile.read((char *)&Npt, 4);
    infile.close();
    this->_UpdateParticleCount(Npt);
    return Npt;
}

// Methods to output data
// - publicly accessible method
void TImpactData::Print()
{
    // Print tree summaries
    if (this->_bunchTree) {
        printf("Bunch data tree:\n");
        this->_bunchTree->Print();
    }
    if (this->_phaseTree) {
        printf("Phase space data tree:\n");
        this->_phaseTree->Print();
    }
    if (this->_endTree) {
        printf("End-slice data tree:\n");
        this->_endTree->Print();
    }
}

// Methods to produce different plot types
// - bunch count cumulative plot for data loaded from `fort.11`
void TImpactData::PlotBunches()
{
    // Default values
    Long_t firstSlice = this->_firstSlice;
    Long_t lastSlice = this->_lastSlice;
    Double_t xmin = 0;
    Double_t xmax = 0;
    Double_t ymin = 0;
    Double_t ymax = 0;
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
    // Check for tree
    if (!this->_bunchTree) {
        throw std::runtime_error(
            "Cannot load bunches as tree structure is not available."
        );
    }

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
        _BUNCHES_CANVAS_NAME,
        _BUNCHES_CANVAS_TITLE,
        _BUNCHES_CANVAS_WIDTH,
        _BUNCHES_CANVAS_HEIGHT
    );

    // Draw the cumulative plots layer by layer, starting at the back
    for (Int_t i = bunchCount; i > 0; i--) {
        this->_PlotBunchLayer(i, firstSlice, lastSlice, (i == bunchCount));
    }

    // Apply styles
    this->_StyleBunches(bunchCount, bunchNames, xmin, xmax, ymin, ymax);

    // Print to file
    this->_PrintCanvas(
        _BUNCHES_CANVAS_NAME,
        _BUNCHES_FILENAME,
        _BUNCHES_FILETYPE
    );
}

void TImpactData::_PlotBunchLayer(
    Int_t currentLayer,
    Int_t firstSlice,
    Int_t lastSlice,
    Bool_t isBackLayer
)
{
    // Build correct settings for current layer
    std::string axesDefinition =
        this->_BuildCumulativePlotString(
            _BUNCHES_BRANCHNAME,
            "n",
            "z",
            currentLayer);
    std::string graphName = "graph" + std::to_string(currentLayer);
    std::string plotOptions = "";
    if (!isBackLayer) plotOptions = "same";

    // Draw graph
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(_BUNCHES_CANVAS_NAME)
    );
    if (!canvas) {
        throw std::runtime_error(
            "Cannot find canvas object."
        );
    }
    canvas->cd();
    const char *axes = axesDefinition.c_str();
    const char *plot = plotOptions.c_str();
    try {
        this->_bunchTree->Draw(axes, "", plot, lastSlice, firstSlice);
    }
    catch (...) {
        std::string errorString =
            "Error calling this->_bunchTree->Draw(" +
            axesDefinition + ", """", " + plotOptions + ", " +
            std::to_string(lastSlice) + ", " + std::to_string(firstSlice) + ")";
        throw std::runtime_error(errorString.c_str());
    }

    // Rename graph
    this->_RenameCurrentGraph(graphName.c_str());
}

// - phase space plots from output files `fort.xx`
void TImpactData::PlotPhaseSpace(Int_t locationNumber, Int_t bunch = 1)
{
    // Check bunch number
    if (bunch > this->_bunchCount) {
        throw std::invalid_argument("No data for bunch " + std::to_string(bunch));
    }

    // Check for tree
    if (!this->_phaseTree) {
        throw std::runtime_error(
            "Cannot load phase space output data as tree structure is not available."
        );
    }

    // Check for branch
    std::string branchName =
        _PHASE_BRANCHNAME + std::to_string(locationNumber) +
        ".bunch" + std::to_string(bunch);
    if (!this->_phaseTree->GetBranch(branchName.c_str())) {
        throw std::invalid_argument(
            "No phase space data for location " + std::to_string(locationNumber) +
            " bunch " + std::to_string(bunch)
        );
    }

    // Create canvas and divide into five parts (one title and four subplots)
    std::string canvasName = _PHASE_CANVAS_NAME;
    this->_CreateCanvas(
        canvasName.c_str(),
        _PHASE_CANVAS_TITLE,
        _PHASE_CANVAS_WIDTH,
        _PHASE_CANVAS_HEIGHT
    );
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(canvasName.c_str())
    );
    canvas->Divide(1, 2, 0, 0);
    TPad *pad = static_cast<TPad *>(canvas->GetPad(2));
    pad->Divide(2, 2);

    // Plot four phase spaces
    pad->cd(1);
    std::string axesDefinition = branchName + ".px:" + branchName + ".x";
    this->_phaseTree->Draw(axesDefinition.c_str(), "");
    pad->cd(2);
    axesDefinition = branchName + ".py:" + branchName + ".y";
    this->_phaseTree->Draw(axesDefinition.c_str(), "");
    pad->cd(3);
    axesDefinition = branchName + ".pz:" + branchName + ".z";
    this->_phaseTree->Draw(axesDefinition.c_str(), "");
    pad->cd(4);
    axesDefinition = branchName + ".y:" + branchName + ".x";
    this->_phaseTree->Draw(axesDefinition.c_str(), "");

    // Apply styles
    this->_StylePhaseSpace(locationNumber, bunch);

    // Print to file
    std::string filename = "";
    filename += _PHASE_FILENAME;
    filename += "-";
    switch (locationNumber) {
        case _PHASE_START:
            filename += "start";
            break;
        case _PHASE_END:
            filename += "end";
            break;
        default:
            filename += std::to_string(locationNumber);
            break;
    }
    if (this->_bunchCount > 1) {
        filename += "-bunch" + std::to_string(bunch);
    }
    filename +=  _PHASE_FILEEXTENSION;
    this->_PrintCanvas(_PHASE_CANVAS_NAME, filename.c_str(), _PHASE_FILETYPE);
}

// - final energy histograms from `rfq1.dst`
void TImpactData::PlotFinalEnergy(
    Int_t nbins = _ENERGY_BINS_DEFAULT,
    Double_t xmin = 0.0,
    Double_t xmax = 0.0
)
{
    // Check for tree
    if (!this->_endTree) {
        throw std::runtime_error(
            "Cannot load end slice data as tree structure is not available."
        );
    }

    // Create canvas
    this->_CreateCanvas(
        _ENERGY_CANVAS_NAME,
        _ENERGY_CANVAS_TITLE,
        _ENERGY_CANVAS_WIDTH,
        _ENERGY_CANVAS_HEIGHT
    );
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(_ENERGY_CANVAS_NAME)
    );

    // Plot each histogram as a separate layer
    for (Int_t i = 1; i <= this->_bunchCount; ++i) {
        std::string histName = _ENERGY_CANVAS_NAME;
        histName += "_hist" + std::to_string(i);
        std::string branchName = _ENDSLICE_BRANCHNAME;
        branchName += ".bunch" + std::to_string(i);
        std::string plotString = branchName + ".W";
        plotString += ">>" + histName + "("
            + std::to_string(nbins) + ","
            + std::to_string(xmin) + ","
            + std::to_string(xmax) + ")";
        std::string plotOptions = "hist";
        if (i > 1) {
            plotOptions += " same";
        }
        TBranch *thisBranch = this->_endTree->GetBranch(branchName.c_str());
        Long_t n = thisBranch->GetEntries();
        canvas = static_cast<TCanvas *>(
            gROOT->GetListOfCanvases()->FindObject(_ENERGY_CANVAS_NAME)
        );
        canvas->cd();
        this->_endTree->Draw(plotString.c_str(), "", plotOptions.c_str(), n);
    }

    // Apply styles
    this->_StyleFinalEnergy(this->_bunchCount, this->_bunchNames);

    // Print to file
    this->_PrintCanvas(_ENERGY_CANVAS_NAME, _ENERGY_FILENAME, _ENERGY_FILETYPE);
}

// Methods to apply styles for different plot types
// - bunch count cumulative plot for data loaded from `fort.11`
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
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(_BUNCHES_CANVAS_NAME)
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
    TPaveText *titleText = static_cast<TPaveText *>(
        canvas->GetPrimitive("title")
    );
    TH1 *hist = static_cast<TH1 *>(canvas->GetPrimitive("htemp"));
    if (!hist) {
        throw std::runtime_error(
            "Cannot find histogram object."
        );
    }
    std::string graphName = "";
    TGraph *graph;

    // Set up background
    frame->SetLineWidth(0);
    if (titleText) {
        titleText->Clear();
    }
    canvas->SetGridx(kFALSE);
    canvas->SetGridy(kTRUE);

    // Set axes options
    // - font code 132 is Times New Roman, medium, regular, scalable
    // x-axis
    hist->GetXaxis()->SetTicks("-");
    hist->GetXaxis()->SetTickSize(0.01);
    hist->GetXaxis()->SetTitleOffset(-1.0);
    hist->GetXaxis()->SetLabelOffset(-0.04);
    hist->GetXaxis()->SetTitle(_BUNCHES_XAXIS_TITLE);
    hist->GetXaxis()->SetTitleFont(132);
    hist->GetXaxis()->SetTitleSize(0.05);
    hist->GetXaxis()->CenterTitle(kTRUE);
    hist->GetXaxis()->SetLabelFont(132);
    hist->GetXaxis()->SetLabelSize(0.035);
    if (xmin != xmax) {
        hist->GetXaxis()->SetLimits(xmin, xmax);
        hist->GetXaxis()->SetRangeUser(xmin, xmin);
    }
    // y-axis
    hist->GetYaxis()->SetTicks("+");
    hist->GetYaxis()->SetTickSize(0.01);
    hist->GetYaxis()->SetTitleOffset(-0.8);
    hist->GetYaxis()->SetLabelOffset(-0.01);
    hist->GetYaxis()->SetTitle(_BUNCHES_YAXIS_TITLE);
    hist->GetYaxis()->SetTitleFont(132);
    hist->GetYaxis()->SetTitleSize(0.05);
    hist->GetYaxis()->CenterTitle(kTRUE);
    hist->GetYaxis()->SetLabelFont(132);
    hist->GetYaxis()->SetLabelSize(0.035);
    if (xmin != xmax) {
        hist->GetYaxis()->SetLimits(ymin, ymax);
        hist->GetYaxis()->SetRangeUser(ymin, ymax);
    }

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
        graph = static_cast<TGraph *>(canvas->GetPrimitive(graphName.c_str()));
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

// - phase space plots from output files `fort.xx`
void TImpactData::_StylePhaseSpace(Int_t locationNumber, Int_t bunch)
{
    // Apply my style settings
    load_style_mje();
    gROOT->SetStyle("mje");

    // Get canvas
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(_PHASE_CANVAS_NAME)
    );
    if (!canvas) {
        throw std::runtime_error(
            "Cannot find canvas object."
        );
    }

    // Add title
    canvas->cd(1);
    std::string titleString = "Phase space at ";
    switch (locationNumber) {
        case _PHASE_START:
            titleString += "simulation start";
            break;
        case _PHASE_END:
            titleString += "simulation end";
            break;
        default:
            titleString += "BPM " + std::to_string(locationNumber);
            break;
    }
    if (this->_bunchCount > 1) {
        titleString += " for bunch" + std::to_string(bunch);
    }
    TPaveLabel *title = new TPaveLabel(
        0.05, 0.05, 0.95, 0.95,
        titleString.c_str(),
        "NB" // no border
    );
    title->SetFillColor(0);
    title->SetTextFont(132);
    title->Draw();

    // Resize pads
    canvas->SetMargin(0.0, 0.0, 0.0, 0.0);
    canvas->GetPad(1)->SetPad(0.0, 0.96, 1.0, 1.0);
    canvas->GetPad(2)->SetPad(0.0, 0.0, 1.0, 0.96);

    // Set subplot options
    // - font code 132 is Times New Roman, medium, regular, scalable
    for (Int_t i = 1; i <= 4; i++) {
        // Connect to correct pad
        canvas->GetPad(2)->cd(i);
        // Set background lines
        gPad->GetFrame()->SetLineWidth(1);
        gPad->SetGridx(kFALSE);
        gPad->SetGridy(kFALSE);
        // Set margins
        gPad->SetLeftMargin(0.15);
        gPad->SetRightMargin(0.05);
        gPad->SetTopMargin(0.05);
        gPad->SetBottomMargin(0.10);
        // Get histogram and graph objects
        TH1 *hist = static_cast<TH1 *>(gPad->GetPrimitive("htemp"));
        if (!hist) {
            throw std::runtime_error(
                "Cannot find histogram object."
            );
        }
        TGraph *graph = static_cast<TGraph *>(gPad->GetPrimitive("Graph"));
        if (!graph) {
            throw std::runtime_error(
                "Cannot find graph object."
            );
        }
        // Set points
        graph->SetMarkerStyle(20);
        graph->SetMarkerSize(0.2);
        // Set x-axis
        hist->GetXaxis()->SetTicks("-");
        hist->GetXaxis()->SetTickSize(0.01);
        hist->GetXaxis()->SetTitleOffset(-1.0);
        hist->GetXaxis()->SetLabelOffset(-0.04);
        hist->GetXaxis()->SetTitleFont(132);
        hist->GetXaxis()->SetTitleSize(0.05);
        hist->GetXaxis()->CenterTitle(kFALSE);
        hist->GetXaxis()->SetLabelFont(132);
        hist->GetXaxis()->SetLabelSize(0.035);
        hist->GetXaxis()->Pop();
        // Set y-axis
        hist->GetYaxis()->SetTicks("+");
        hist->GetYaxis()->SetTickSize(0.01);
        hist->GetYaxis()->SetTitleOffset(-1.4);
        hist->GetYaxis()->SetLabelOffset(-0.01);
        hist->GetYaxis()->SetTitleFont(132);
        hist->GetYaxis()->SetTitleSize(0.05);
        hist->GetYaxis()->CenterTitle(kFALSE);
        hist->GetYaxis()->SetLabelFont(132);
        hist->GetYaxis()->SetLabelSize(0.035);
        hist->GetYaxis()->Pop();
        // Set labels
        switch (i) {
            case 1:
                hist->GetXaxis()->SetTitle("x");
                hist->GetYaxis()->SetTitle("px");
                break;
            case 2:
                hist->GetXaxis()->SetTitle("y");
                hist->GetYaxis()->SetTitle("py");
                break;
            case 3:
                hist->GetXaxis()->SetTitle("z");
                hist->GetYaxis()->SetTitle("pz");
                break;
            case 4:
                hist->GetXaxis()->SetTitle("x");
                hist->GetYaxis()->SetTitle("y");
                break;
        }
    }

    // Update canvas
    canvas->Update();
    canvas->Paint();
}

// - final energy histograms from `rfq1.dst`
void TImpactData::_StyleFinalEnergy(
    Int_t bunchCount,
    std::vector<std::string> bunchNames
)
{
    // Apply my style settings
    load_style_mje();
    gROOT->SetStyle("mje");

    // Get objects
    TCanvas *canvas = (TCanvas *)(
        gROOT->GetListOfCanvases()->FindObject(_ENERGY_CANVAS_NAME)
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
    std::string histName = _ENERGY_CANVAS_NAME;
    histName += "_hist1";
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
    hist->GetXaxis()->SetTitle(_ENERGY_XAXIS_TITLE);
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
    hist->GetYaxis()->SetTitle(_ENERGY_YAXIS_TITLE);
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
        histName = _ENERGY_CANVAS_NAME;
        histName += "_hist" + std::to_string(i);
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
void TImpactData::_RenameCurrentGraph(const char *name)
{
    TGraph *thisGraph = static_cast<TGraph *>(gPad->GetPrimitive("Graph"));
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
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(name)
    );
    if (!canvas) {
        canvas = gROOT->MakeDefCanvas();
    }
    canvas->Clear();
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
    TCanvas *canvas = static_cast<TCanvas *>(
        gROOT->GetListOfCanvases()->FindObject(name)
    );
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
    // Update member
    if (newCount > this->_sliceCount) {
        this->_sliceCount = newCount;
    }
    // Update first and last
    this->_firstSlice = 1;
    this->_lastSlice = this->_sliceCount - 1;
    // Bunch count tree
    if (this->_bunchTree) {
        if (newCount > this->_bunchTree->GetEntries()) {
            this->_bunchTree->SetEntries(newCount);
        }
    }
}

// - update the number of particle entries in the trees
void TImpactData::_UpdateParticleCount(Long_t newCount)
{
    // Update member
    if (newCount > this->_particleCount) {
        this->_particleCount = newCount;
    }
    // Phase space tree
    if (this->_phaseTree) {
        if (newCount > this->_phaseTree->GetEntries()) {
            this->_phaseTree->SetEntries(newCount);
        }
    }
    // End slice tree
    if (this->_endTree) {
        Long_t currentCount = this->_endTree->GetEntries();
        if (newCount > currentCount) {
            this->_endTree->SetEntries(newCount);
        }
    }
}

// - check if a file exists
bool TImpactData::_FileExists(std::string filename)
{
    FileStat_t stat;
    return (gSystem->GetPathInfo(filename.c_str(), stat) == 0);
}
