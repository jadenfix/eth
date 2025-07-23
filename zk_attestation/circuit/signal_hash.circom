pragma circom 2.0.0;

include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom";

// Circuit to generate and verify trading signal hashes
template SignalHash() {
    signal input signal_type;      // 1=MEV, 2=Risk, 3=Anomaly, etc.
    signal input confidence_score; // 0-100
    signal input entity_id;        // Entity being flagged
    signal input timestamp;        // Signal generation time
    signal input model_hash;       // Hash from ModelPoseidon circuit
    signal input nonce;           // Unique nonce
    
    signal output signal_hash;
    signal output is_valid;

    // Ensure confidence score is valid (0-100)
    component confidence_check = LessEqThan(7); // 2^7 = 128 > 100
    confidence_check.in[0] <== confidence_score;
    confidence_check.in[1] <== 100;
    
    // Ensure signal type is valid (1-10)
    component type_check_lower = GreaterThan(4); // 2^4 = 16 > 10
    type_check_lower.in[0] <== signal_type;
    type_check_lower.in[1] <== 0;
    
    component type_check_upper = LessEqThan(4);
    type_check_upper.in[0] <== signal_type;
    type_check_upper.in[1] <== 10;
    
    // Signal is valid if all checks pass
    is_valid <== confidence_check.out * type_check_lower.out * type_check_upper.out;
    
    // Generate signal hash using Poseidon
    component poseidon = Poseidon(6);
    poseidon.inputs[0] <== signal_type;
    poseidon.inputs[1] <== confidence_score;
    poseidon.inputs[2] <== entity_id;
    poseidon.inputs[3] <== timestamp;
    poseidon.inputs[4] <== model_hash;
    poseidon.inputs[5] <== nonce;
    
    signal_hash <== poseidon.out;
    
    // Constrain that invalid signals produce zero hash
    signal_hash * (1 - is_valid) === 0;
}

component main = SignalHash();
