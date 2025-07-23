pragma circom 2.0.0;

include "../node_modules/circomlib/circuits/poseidon.circom";

// Circuit to generate Poseidon hash of ML model parameters
template ModelPoseidon() {
    signal input model_weights[16]; // Simplified model representation
    signal input model_version;
    signal input timestamp;
    signal output hash;

    component poseidon = Poseidon(18); // 16 weights + version + timestamp
    
    for (var i = 0; i < 16; i++) {
        poseidon.inputs[i] <== model_weights[i];
    }
    poseidon.inputs[16] <== model_version;
    poseidon.inputs[17] <== timestamp;
    
    hash <== poseidon.out;
}

component main = ModelPoseidon();
