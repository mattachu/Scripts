// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include "TTree.h"
#pragma once

class TImpactTree : public TTree {

public:
    ClassDef(TImpactTree, 1); // Data structure for Impact-T simulations

    TImpactTree();
    TImpactTree(Int_t bunchCount, ...);
    ~TImpactTree();

    Int_t BunchCount() const;

protected:
    Int_t _bunchCount; // Number of bunches in Impact-T simulation

}
