// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include <vector>
#include "TTree.h"
#pragma once

class TImpactTree : public TTree
{
public:
    // Class definition
    ClassDef(TImpactTree, 1); // Data structure for Impact-T simulations

    // Constructors and destructors
    TImpactTree();
    TImpactTree(Int_t bunchCount);
    TImpactTree(Int_t bunchCount, std::vector<std::string> bunchNames);
    ~TImpactTree();

    // Methods to access members
    Int_t BunchCount() const;
    std::vector<std::string> BunchNames() const;
    Int_t CellCount() const;
    Int_t SliceCount() const;
    Int_t GetFirstCell() const;
    Int_t GetFirstSlice() const;
    Int_t GetLastCell() const;
    Int_t GetLastSlice() const;
    void SetFirstCell(Int_t firstCell);
    void SetFirstSlice(Int_t firstSlice);
    void SetLastCell(Int_t lastCell);
    void SetLastSlice(Int_t lastSlice);

protected:
    Int_t                    _bunchCount; // Number of bunches in the simulation
    std::vector<std::string> _bunchNames; // List of names for the bunches
    Int_t                    _cellCount;  // Number of RFQ cells
    Int_t                    _sliceCount; // Number of RFQ cells
    Int_t                    _firstCell;  // FIrst RFQ cell number to plot
    Int_t                    _firstSlice; // FIrst time slice to plot
    Int_t                    _lastCell;   // Last RFQ cell number to plot
    Int_t                    _lastSlice;  // Last time slice to plot
};
