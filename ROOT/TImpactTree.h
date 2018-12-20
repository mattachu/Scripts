// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include <vector>
#include "TTree.h"
#include "TCanvas.h"
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
    Int_t CellCount() const;
    Int_t SliceCount() const;
    std::vector<std::string> GetBunchNames() const;
    Int_t GetFirstCell() const;
    Int_t GetFirstSlice() const;
    Int_t GetLastCell() const;
    Int_t GetLastSlice() const;
    void SetDefaultBunchNames();
    void SetBunchNames(std::vector<std::string> bunchNames);
    void SetFirstCell(Int_t firstCell);
    void SetFirstSlice(Int_t firstSlice);
    void SetLastCell(Int_t lastCell);
    void SetLastSlice(Int_t lastSlice);

    // Methods to load and plot data
    void Load();
    void PlotBunches();
    void PlotBunches(
        Long_t firstSlice,
        Long_t lastSlice,
        Double_t xmin,
        Double_t xmax,
        Double_t ymin,
        Double_t ymax
    );
    void PlotFinalEnergy(TCanvas *canvas);

protected:
    // Class members
    const Int_t              _bunchCount; // Number of bunches in the simulation
    std::vector<std::string> _bunchNames; // List of names for the bunches
    Int_t                    _cellCount;  // Number of RFQ cells
    Int_t                    _sliceCount; // Number of RFQ cells
    Int_t                    _firstCell;  // FIrst RFQ cell number to plot
    Int_t                    _firstSlice; // FIrst time slice to plot
    Int_t                    _lastCell;   // Last RFQ cell number to plot
    Int_t                    _lastSlice;  // Last time slice to plot

    // Methods to load data from different Impact-T output files
    void _Load(Int_t bunchCount);
    void _LoadBunches(Int_t bunchCount);
    void _LoadEndSlice(Int_t bunchCount);
    void _LoadDSTParticleData(
        std::string filename,
        std::string branchname
    );
    Int_t _GetDSTParticleCount(std::string filename);

    // Methods to produce different plot types
    void _PlotBunchLayer(
        Int_t currentLayer,
        Int_t lastSlice,
        Bool_t isBackLayer
    );

    // Methods to apply styles for different plot types
    void _StyleBunches(
        Int_t bunchCount,
        std::vector<std::string> bunchNames,
        Double_t xmin,
        Double_t xmax,
        Double_t ymin,
        Double_t ymax
    );

    // Utility methods
    void _RenameCurrentGraph(const char *name);
    std::string _BuildCumulativePlotString(
        std::string branchName,
        std::string prefix,
        std::string xaxis,
        Int_t variableCount
    );
    void _UpdateParticleCount(Long_t newCount);
};
