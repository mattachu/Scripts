// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include "TImpactTree.h"

ClassImp(TImpactTree);

// Default constructor
TImpactTree::TImpactTree() {
    this->_bunchCount = 1;
};

// Constructor given bunch count and bunch names
TImpactTree::TImpactTree(Int_t bunchCount, ...) {
    this->_bunchCount = bunchCount;
}

// Default destructor
TImpactTree::~TImpactTree() {

};

// Methods to access members
Int_t TImpactTree::BunchCount() const {
    return this->_bunchCount;
}
