// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include <vector>
#include "TImpactTree.h"

ClassImp(TImpactTree);

// Default constructor
TImpactTree::TImpactTree()
{
    this->_bunchCount = 1;
    this->_bunchNames = {"Bunch 1"};
    this->_cellCount = 0;
    this->_sliceCount = 0;
    this->_firstCell = 0;
    this->_firstSlice = 0;
    this->_lastCell = 0;
    this->_lastSlice = 0;
}

// Constructor given bunch count only
TImpactTree::TImpactTree(Int_t bunchCount)
{
    std::vector<std::string> bunchNames;

    // Bunch count
    this->_bunchCount = bunchCount;

    // Default list of bunch names
    for (Int_t i = 1; i <= bunchCount; i++)
    {
        bunchNames.push_back("Bunch " + std::to_string(i));
    }
    this->_bunchNames = bunchNames;

    // Default cell and slice counts
    this->_cellCount = 0;
    this->_sliceCount = 0;
    this->_firstCell = 0;
    this->_firstSlice = 0;
    this->_lastCell = 0;
    this->_lastSlice = 0;
}

// Constructor given bunch count and bunch names
TImpactTree::TImpactTree(
    Int_t bunchCount,
    std::vector<std::string> bunchNames)
{

    // Bunch count
    this->_bunchCount = bunchCount;

    // List of bunch names
    if (bunchNames.size() < bunchCount)
    {
        for (Int_t i = bunchNames.size()+1; i <= bunchCount; i++)
        {
            bunchNames.push_back("Bunch " + std::to_string(i));
        }
    }
    bunchNames.resize(bunchCount);
    this->_bunchNames = bunchNames;

    // Default cell and slice counts
    this->_cellCount = 0;
    this->_sliceCount = 0;
    this->_firstCell = 0;
    this->_firstSlice = 0;
    this->_lastCell = 0;
    this->_lastSlice = 0;
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

std::vector<std::string> TImpactTree::BunchNames() const
{
    return this->_bunchNames;
}

Int_t TImpactTree::CellCount() const
{
    return this->_cellCount;
}

Int_t TImpactTree::SliceCount() const
{
    return this->_sliceCount;
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
    if (bunchCount < 1)
    {
        throw std::invalid_argument("Must have at least one bunch.");
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
        std::vector<Int_t> count;
    };
    impact_step_t step;
    step.count.resize(bunchCount);
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
            infile >> step.count.at(i);
        }
        this->Fill();
    }
    infile.close();

    // Set number of slices for the tree object
    this->_sliceCount = this->GetBranch("bunches")->GetEntries();
    this->_firstSlice = 1;
    this->_lastSlice = this->_sliceCount;
}

