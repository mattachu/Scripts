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
