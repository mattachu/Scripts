// Class for loading, plotting and manipulating Impact-T data in ROOT
// written by Matt Easton (see http://matteaston.net/work), November 2018

#include <vector>
#include "TImpactTree.h"

ClassImp(TImpactTree);

// Default constructor
TImpactTree::TImpactTree() {
    this->_bunchCount = 1;
}

// Constructor given bunch count only
TImpactTree::TImpactTree(Int_t bunchCount) {
    std::vector<std::string> bunchNames;

    // Bunch count
    this->_bunchCount = bunchCount;

    // List of bunch names
    for (Int_t i = 1; i <= bunchCount; i++) {
        bunchNames.push_back("Bunch " + std::to_string(i));
    }
    this->_bunchNames = bunchNames;
}

// Constructor given bunch count and bunch names
TImpactTree::TImpactTree(Int_t                    bunchCount,
                         std::vector<std::string> bunchNames) {

    // Bunch count
    this->_bunchCount = bunchCount;

    // List of bunch names
    if (bunchNames.size() < bunchCount) {
        for (Int_t i = bunchNames.size()+1; i <= bunchCount; i++) {
            bunchNames.push_back("Bunch " + std::to_string(i));
        }
    }
    bunchNames.resize(bunchCount);
    this->_bunchNames = bunchNames;
}

// Default destructor
TImpactTree::~TImpactTree() {

}

// Methods to access members
Int_t TImpactTree::BunchCount() const {
    return this->_bunchCount;
}

std::vector<std::string> TImpactTree::BunchNames() const {
    return this->_bunchNames;
}
