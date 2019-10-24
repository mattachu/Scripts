// Class for loading, plotting and manipulating Impact-T RFQ simulation data
// written by Matt Easton (see http://matteaston.net/work), October 2019
// inherits from the main class TImpactTree

#include <vector>
#include "TImpactTree.h"
#include "TCanvas.h"
#pragma once

class TImpactRFQTree : public TImpactTree
{
public:
    // Class definition
    ClassDef(TImpactRFQTree, 1); // Data structure for Impact-T RFQ simulations

    // Constructors and destructors
    TImpactRFQTree();
    TImpactRFQTree(Int_t bunchCount);
    TImpactRFQTree(Int_t bunchCount, std::vector<std::string> bunchNames);
    ~TImpactRFQTree();

    // Methods to access members
    Int_t CellCount() const;
    Int_t GetFirstCell() const;
    Int_t GetLastCell() const;
    void SetFirstCell(Int_t firstCell);
    void SetLastCell(Int_t lastCell);

    // Methods to load and plot data
    void Load(); // overloads TImpactTree
    void PlotFinalEnergy(Int_t nbins, Double_t xmin, Double_t xmax);

protected:
    // Class members
    Int_t                    _cellCount;  // Number of RFQ cells
    Int_t                    _firstCell;  // FIrst RFQ cell number to plot
    Int_t                    _lastCell;   // Last RFQ cell number to plot

    // Methods to load data from different Impact-T output files
    void _Load(Int_t bunchCount); // overloads TImpactTree
    void _LoadEndSlice(Int_t bunchCount);
    void _LoadDSTParticleData(
        std::string filename,
        std::string branchname
    );
    Int_t _GetDSTParticleCount(std::string filename);

    // Methods to apply styles for different plot types
    void _StyleFinalEnergy(
        Int_t bunchCount,
        std::vector<std::string> bunchNames
    );
};
