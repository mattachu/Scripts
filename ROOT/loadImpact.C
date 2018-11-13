// Read in particle count data from `fort.11` (hard-coded to 4 bunches for now)
TTree *loadImpact(){

    // Create tree
    TTree *impact_data = new TTree("Impact", "Impact-T simulation data");

    // Details of a single line in `fort.11`
    struct impact_step_t {
        Long_t i;
        Double_t t, z;
        Int_t bunches, n1, n2, n3, n4;
    };
    impact_step_t step;
    ifstream infile("fort.11");

    // Create a branch for the particle count data
    impact_data->Branch("bunches", &step,
                        "i/L:t/D:z/D:bunches/I:n1/I:n2/I:n3/I:n4/I");

    // Read in data from `fort.11`
    while (1) {
        if(!infile.good()) break;
        infile >> step.i >> step.t >> step.z >> step.bunches >>
                  step.n1 >> step.n2 >> step.n3 >> step.n4;
        impact_data->Fill();
    }
    infile.close();

    // Output data summary
    impact_data->Print();

    // Return the tree
    return impact_data;

}
