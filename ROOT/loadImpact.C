// Read in particle count data from `fort.11`
TTree *loadImpact(Int_t bunchCount){

    // Check bunch count
    if (bunchCount < 1) {
        throw std::invalid_argument("Must have at least one bunch.");
    }
    if (bunchCount > 9) {
        throw std::invalid_argument("Cannot cope with more than nine bunches.");
    }

    // Create tree
    TTree *impact_data = new TTree("Impact", "Impact-T simulation data");

    // Create structure to hold data
    struct impact_step_t {
        Long_t i = 0;
        Double_t t = 0.0, z = 0.0;
        Int_t bunches = 0;
        Int_t n1=0, n2=0, n3=0, n4=0, n5=0, n6=0, n7=0, n8=0, n9=0;
    };
    impact_step_t step;
    std::string leafDefinition = "i/L:t/D:z/D:bunches/I";
    for (Int_t i = 1; i <= bunchCount; i++) {
        leafDefinition += ":n" + std::to_string(i) + "/I";
    }

    // Open the file for reading
    ifstream infile("fort.11");

    // Create a branch for the particle count data
    impact_data->Branch("bunches", &step, leafDefinition.c_str());

    // Read in data from `fort.11`
    while (1) {
        if(!infile.good()) break;
        infile >> step.i >> step.t >> step.z >> step.bunches >> step.n1;
        if(bunchCount >= 2) {infile >> step.n2;}
        if(bunchCount >= 3) {infile >> step.n3;}
        if(bunchCount >= 4) {infile >> step.n4;}
        if(bunchCount >= 5) {infile >> step.n5;}
        if(bunchCount >= 6) {infile >> step.n6;}
        if(bunchCount >= 7) {infile >> step.n7;}
        if(bunchCount >= 8) {infile >> step.n8;}
        if(bunchCount == 9) {infile >> step.n9;}
        impact_data->Fill();
    }
    infile.close();

    // Output data summary
    impact_data->Print();

    // Return the tree
    return impact_data;

}
