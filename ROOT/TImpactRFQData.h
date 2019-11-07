// Class for loading, plotting and manipulating Impact-T RFQ simulation data
// written by Matt Easton (see http://matteaston.net/work), October 2019
// inherits from the main class TImpactTree

#ifndef TIMPACTRFQDATA_H_
#define TIMPACTRFQDATA_H_

#include <vector>
#include "TImpactData.h"
#include "TCanvas.h"

class TImpactRFQData : public TImpactData
{
public:
    // Class definition
    ClassDefOverride(TImpactRFQData, 1); // Data structure for Impact-T RFQ simulations

    // Constructors and destructors
    TImpactRFQData();
    TImpactRFQData(Int_t bunchCount);
    TImpactRFQData(Int_t bunchCount, std::vector<std::string> bunchNames);
    virtual ~TImpactRFQData();

    // Methods to access members
    Int_t CellCount() const;
    Int_t GetFirstCell() const;
    Int_t GetLastCell() const;
    void SetFirstCell(Int_t firstCell);
    void SetLastCell(Int_t lastCell);
    TTree *GetTree(std::string treeName) override;

    // Input and output methods
    void Load() override;
    void Load(Int_t bpmNumber) override;
    void Load(std::vector<Int_t> bpmList) override;
    void Print() override;
    void PlotFinalEnergy(Int_t nbins, Double_t xmin, Double_t xmax);

protected:
    // Class members
    TTree                   *_endTree;    // Tree containing end slice data
    Int_t                    _cellCount;  // Number of RFQ cells
    Int_t                    _firstCell;  // FIrst RFQ cell number to plot
    Int_t                    _lastCell;   // Last RFQ cell number to plot

    // Methods to create and delete data structures
    void _CreateNullTrees() override;
    void _CreateEndTree();
    void _DeleteAllTrees() override;
    void _DeleteEndTree();

    // Methods to load data from different Impact-T output files
    void _LoadAll(Int_t bunchCount, std::vector<Int_t> bpmList = {}) override;
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

    // Utility methods
    void _UpdateParticleCount(Long_t newCount) override;
};

#endif // TIMPACTRFQDATA_H_
