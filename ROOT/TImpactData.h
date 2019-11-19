// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018
// modified by Matt Easton, October 2019

#ifndef ROOT_TIMPACTDATA_H_
#define ROOT_TIMPACTDATA_H_

#include <string>
#include <vector>
#include "TClass.h"
#include "TTree.h"
#include "TCanvas.h"

class TImpactData
{
public:
    // Constructors and destructors
    TImpactData();
    TImpactData(Int_t bunchCount);
    TImpactData(Int_t bunchCount, std::vector<std::string> bunchNames);
    virtual ~TImpactData();

    // Methods to access members
    const Int_t BunchCount() const;
    const Int_t SliceCount() const;
    const Int_t ParticleCount() const;
    const std::vector<std::string> GetBunchNames() const;
    const Int_t GetFirstSlice() const;
    const Int_t GetLastSlice() const;
    TTree *GetTree(std::string treeName) const;
    void SetDefaultBunchNames();
    void SetBunchNames(std::vector<std::string> bunchNames);
    void SetFirstSlice(Int_t firstSlice);
    void SetLastSlice(Int_t lastSlice);

    // Input and output methods
    void Load();
    void Load(Int_t bpmNumber);
    void Load(std::vector<Int_t> bpmList);
    void Print();
    void PlotBunches();
    void PlotBunches(
        Long_t firstSlice,
        Long_t lastSlice,
        Double_t xmin,
        Double_t xmax,
        Double_t ymin,
        Double_t ymax
    );
    void PlotPhaseSpace(Int_t locationNumber, Int_t bunch = 1);
    void PlotFinalEnergy(Int_t nbins, Double_t xmin, Double_t xmax);

protected:
    // Class members
    TTree                   *_bunchTree;     // Tree containing bunch count data
    TTree                   *_phaseTree;     // Tree containing phase space data
    TTree                   *_endTree;       // Tree containing end slice data
    const Int_t              _bunchCount;    // Number of bunches in the simulation
    std::vector<std::string> _bunchNames;    // List of names for the bunches
    Int_t                    _sliceCount;    // Number of time slices
    Int_t                    _firstSlice;    // First time slice to plot
    Int_t                    _lastSlice;     // Last time slice to plot
    Int_t                    _particleCount; // Number of partilces

    // Methods to create and delete data structures
    void _CreateNullTrees();
    void _CreateDefaultTrees();
    void _CreateBunchTree();
    void _CreatePhaseTree();
    void _CreateEndTree();
    void _DeleteAllTrees();
    void _DeleteBunchTree();
    void _DeletePhaseTree();
    void _DeleteEndTree();

    // Methods to load data from different Impact-T output files
    void _LoadAll(Int_t bunchCount, std::vector<Int_t> bpmList = {});
    void _LoadBunches(Int_t bunchCount);
    void _LoadPhaseSpaceData(Int_t bunchCount, Int_t locationNumber);
    void _LoadPhaseSpace(Int_t bunch, Int_t locationNumber);
    void _LoadEndSlice(Int_t bunchCount);
    void _LoadDSTParticleData(
        std::string filename,
        std::string branchname
    );
    Int_t _GetDSTParticleCount(std::string filename);

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
    void _StylePhaseSpace(Int_t locationNumber, Int_t bunch);
    void _StyleFinalEnergy(
        Int_t bunchCount,
        std::vector<std::string> bunchNames
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
    void _UpdateParticleCount(Long_t newCount);
    bool _FileExists(std::string filename);
};

#endif // ROOT_TIMPACTDATA_H_
