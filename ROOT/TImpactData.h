// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018
// modified by Matt Easton, October 2019

#ifndef TIMPACTDATA_H_
#define TIMPACTDATA_H_

#include <vector>
#include "TTree.h"
#include "TCanvas.h"

class TImpactData
{
public:
    // Class definition
    ClassDef(TImpactData, 1); // Data structure for Impact-T simulations

    // Constructors and destructors
    TImpactData();
    TImpactData(Int_t bunchCount);
    TImpactData(Int_t bunchCount, std::vector<std::string> bunchNames);
    virtual ~TImpactData();

    // Methods to access members
    Int_t BunchCount() const;
    Int_t SliceCount() const;
    std::vector<std::string> GetBunchNames() const;
    Int_t GetFirstSlice() const;
    Int_t GetLastSlice() const;
    void SetDefaultBunchNames();
    void SetBunchNames(std::vector<std::string> bunchNames);
    void SetFirstSlice(Int_t firstSlice);
    void SetLastSlice(Int_t lastSlice);
    virtual TTree *GetTree(std::string treeName);

    // Input and output methods
    virtual void Load();
    virtual void Print();
    void PlotBunches();
    void PlotBunches(
        Long_t firstSlice,
        Long_t lastSlice,
        Double_t xmin,
        Double_t xmax,
        Double_t ymin,
        Double_t ymax
    );

protected:
    // Class members
    TTree                   *_bunchTree;  // Tree containing bunch count data
    const Int_t              _bunchCount; // Number of bunches in the simulation
    std::vector<std::string> _bunchNames; // List of names for the bunches
    Int_t                    _sliceCount; // Number of time slices
    Int_t                    _firstSlice; // First time slice to plot
    Int_t                    _lastSlice;  // Last time slice to plot

    // Methods to create and delete data structures
    virtual void _CreateNullTrees();
    virtual void _CreateDefaultTrees();
    void _CreateBunchTree();
    virtual void _DeleteAllTrees();
    void _DeleteBunchTree();

    // Methods to load data from different Impact-T output files
    virtual void _LoadAll(Int_t bunchCount);
    void _LoadBunches(Int_t bunchCount);

    // Methods to produce different plot types
    void _PlotBunchLayer(
        Int_t currentLayer,
        Int_t firstSlice,
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
    void _CreateCanvas(
        const char *name,
        const char *title,
        const Int_t width,
        const Int_t height
    );
    void _PrintCanvas(
        const char *name,
        const char *filename,
        const char *filetype
    );
    std::string _BuildCumulativePlotString(
        std::string branchName,
        std::string prefix,
        std::string xaxis,
        Int_t variableCount
    );
    void _UpdateSliceCount(Long_t newCount);
    bool _FileExists(std::string filename);
};

#endif // TIMPACTDATA_H_
