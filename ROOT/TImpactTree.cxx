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
    for (Int_t i = 1; i <= bunchCount; i++)
    {
        bunchNames.push_back("Bunch " + std::to_string(i));
    }
    this->_bunchNames = bunchNames;
}

void TImpactTree::SetBunchNames(std::vector<std::string> bunchNames)
{
    Int_t bunchCount = this->BunchCount();
    if (bunchNames.size() < bunchCount)
    {
        for (Int_t i = bunchNames.size()+1; i <= bunchCount; i++)
        {
            bunchNames.push_back("Bunch " + std::to_string(i));
        }
    }
    bunchNames.resize(bunchCount);
    this->_bunchNames = bunchNames;
}

void TImpactTree::SetFirstCell(Int_t firstCell)
{
    if (firstCell > this->_cellCount)
    {
        throw std::invalid_argument(
            "Cannot set the cell number higher than the number of cells."
        );
    }
    if (firstCell < 0)
    {
        throw std::invalid_argument("Cannot set negative cell numbers.");
    }

    this->_firstCell = firstCell;
}

void TImpactTree::SetFirstSlice(Int_t firstSlice)
{
    if (firstSlice > this->_sliceCount)
    {
        throw std::invalid_argument(
            "Cannot set the slice number higher than the number of slices."
        );
    }
    if (firstSlice < 0)
    {
        throw std::invalid_argument("Cannot set negative slice numbers.");
    }

    this->_firstSlice = firstSlice;
}

void TImpactTree::SetLastCell(Int_t lastCell)
{
    if (lastCell > this->_cellCount)
    {
        throw std::invalid_argument(
            "Cannot set the cell number higher than the number of cells."
        );
    }
    if (lastCell < 0)
    {
        throw std::invalid_argument("Cannot set negative cell numbers.");
    }
    if (lastCell < this->_firstCell)
    {
        throw std::invalid_argument(
            "Cannot set the last cell number lower than the first cell."
        );
    }

    this->_lastCell = lastCell;
}

void TImpactTree::SetLastSlice(Int_t lastSlice)
{
    if (lastSlice > this->_sliceCount)
    {
        throw std::invalid_argument(
            "Cannot set the slice number higher than the number of slices."
        );
    }
    if (lastSlice < 0)
    {
        throw std::invalid_argument("Cannot set negative slice numbers.");
    }
    if (lastSlice < this->_firstSlice)
    {
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
    if (bunchCount < 1)
    {
        errorString = "Must have at least one bunch.";
        throw std::invalid_argument(errorString.c_str());
    }
    if (bunchCount > _MAX_BUNCH_COUNT)
    {
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
    for (Int_t i = 1; i <= bunchCount; i++)
    {
        leafDefinition += ":n" + std::to_string(i) + "/I";
    }

    // Open the file for reading
    ifstream infile("fort.11");

    // Create a branch for the particle count data
    this->Branch("bunches", &step, leafDefinition.c_str());

    // Read in data from `fort.11`
    while (1)
    {
        if(!infile.good()) break;
        infile >> step.i >> step.t >> step.z >> step.bunches;
        for (Int_t i = 0; i < bunchCount; i++)
        {
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
