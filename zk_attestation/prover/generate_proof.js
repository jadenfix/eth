import { groth16 } from "snarkjs";
import fs from "fs/promises";
import path from "path";
import { buildPoseidon } from "circomlib";

/**
 * Zero-Knowledge Proof Generator for Trading Signals
 * Generates proofs that trading signals came from authenticated ML models
 * without revealing model parameters or signal details
 */

export class ZKSignalProver {
    constructor() {
        this.circuitPath = "./circuits";
        this.buildPath = "./build";
        this.poseidon = null;
    }

    async initialize() {
        this.poseidon = await buildPoseidon();
        await this.ensureBuildDirectory();
    }

    async ensureBuildDirectory() {
        try {
            await fs.access(this.buildPath);
        } catch {
            await fs.mkdir(this.buildPath, { recursive: true });
        }
    }

    /**
     * Generate proof for ML model attestation
     * @param {Object} modelData - Model parameters and metadata
     * @param {Array} modelData.weights - Model weights (16 values)
     * @param {number} modelData.version - Model version
     * @param {number} modelData.timestamp - Unix timestamp
     * @returns {Object} Proof object
     */
    async generateModelProof(modelData) {
        const { weights, version, timestamp } = modelData;
        
        if (!weights || weights.length !== 16) {
            throw new Error("Model must have exactly 16 weights");
        }

        // Prepare circuit inputs
        const input = {
            weights: weights.map(w => Math.floor(w * 1000)), // Scale to integers
            version: version,
            timestamp: timestamp
        };

        console.log("Generating model attestation proof...");
        
        const wasmFile = path.join(this.buildPath, "model_poseidon.wasm");
        const zkeyFile = path.join(this.buildPath, "model_poseidon_final.zkey");

        const { proof, publicSignals } = await groth16.fullProve(
            input,
            wasmFile,
            zkeyFile
        );

        return {
            proof,
            publicSignals,
            modelHash: publicSignals[0],
            timestamp: timestamp,
            version: version
        };
    }

    /**
     * Generate proof for trading signal attestation
     * @param {Object} signalData - Trading signal data
     * @param {number} signalData.signalType - Signal type (1-10)
     * @param {number} signalData.confidence - Confidence score (0-100)
     * @param {string} signalData.modelHash - Hash of the generating model
     * @param {number} signalData.timestamp - Unix timestamp
     * @returns {Object} Proof object
     */
    async generateSignalProof(signalData) {
        const { signalType, confidence, modelHash, timestamp } = signalData;

        // Validate inputs
        if (signalType < 1 || signalType > 10) {
            throw new Error("Signal type must be between 1 and 10");
        }
        if (confidence < 0 || confidence > 100) {
            throw new Error("Confidence must be between 0 and 100");
        }

        // Prepare circuit inputs
        const input = {
            signal_type: signalType,
            confidence: confidence,
            model_hash: modelHash,
            timestamp: timestamp
        };

        console.log("Generating signal attestation proof...");
        
        const wasmFile = path.join(this.buildPath, "signal_hash.wasm");
        const zkeyFile = path.join(this.buildPath, "signal_hash_final.zkey");

        const { proof, publicSignals } = await groth16.fullProve(
            input,
            wasmFile,
            zkeyFile
        );

        return {
            proof,
            publicSignals,
            signalHash: publicSignals[0],
            isValid: publicSignals[1] === "1",
            timestamp: timestamp,
            signalType: signalType
        };
    }

    /**
     * Generate composite proof linking model and signal
     * @param {Object} modelData - Model parameters
     * @param {Object} signalData - Signal data
     * @returns {Object} Combined proof object
     */
    async generateCompositeProof(modelData, signalData) {
        console.log("Generating composite model+signal proof...");
        
        // Generate model proof
        const modelProof = await this.generateModelProof(modelData);
        
        // Use model hash in signal proof
        const signalDataWithHash = {
            ...signalData,
            modelHash: modelProof.modelHash
        };
        
        const signalProof = await this.generateSignalProof(signalDataWithHash);

        return {
            modelProof,
            signalProof,
            linkage: {
                modelHash: modelProof.modelHash,
                signalHash: signalProof.signalHash,
                timestamp: Math.max(modelProof.timestamp, signalProof.timestamp)
            }
        };
    }

    /**
     * Verify a proof against its circuit
     * @param {Object} proof - Proof to verify
     * @param {Array} publicSignals - Public signals
     * @param {string} circuitName - Name of circuit
     * @returns {boolean} Verification result
     */
    async verifyProof(proof, publicSignals, circuitName) {
        const vkeyFile = path.join(this.buildPath, `${circuitName}_verification_key.json`);
        
        try {
            const vKey = JSON.parse(await fs.readFile(vkeyFile, 'utf8'));
            const result = await groth16.verify(vKey, publicSignals, proof);
            return result;
        } catch (error) {
            console.error("Verification failed:", error);
            return false;
        }
    }

    /**
     * Export proof in blockchain-compatible format
     * @param {Object} proof - Proof object
     * @returns {Object} Formatted proof for smart contract
     */
    formatProofForContract(proof) {
        return {
            a: [proof.pi_a[0], proof.pi_a[1]],
            b: [[proof.pi_b[0][1], proof.pi_b[0][0]], [proof.pi_b[1][1], proof.pi_b[1][0]]],
            c: [proof.pi_c[0], proof.pi_c[1]]
        };
    }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
    const prover = new ZKSignalProver();
    await prover.initialize();

    const command = process.argv[2];
    
    if (command === "model") {
        // Example model proof
        const modelData = {
            weights: Array.from({length: 16}, () => Math.random() * 100),
            version: 1,
            timestamp: Math.floor(Date.now() / 1000)
        };
        
        const proof = await prover.generateModelProof(modelData);
        console.log("Model proof generated:", JSON.stringify(proof, null, 2));
        
    } else if (command === "signal") {
        // Example signal proof
        const signalData = {
            signalType: 5,
            confidence: 85,
            modelHash: "12345678901234567890",
            timestamp: Math.floor(Date.now() / 1000)
        };
        
        const proof = await prover.generateSignalProof(signalData);
        console.log("Signal proof generated:", JSON.stringify(proof, null, 2));
        
    } else if (command === "composite") {
        // Example composite proof
        const modelData = {
            weights: Array.from({length: 16}, () => Math.random() * 100),
            version: 1,
            timestamp: Math.floor(Date.now() / 1000)
        };
        
        const signalData = {
            signalType: 3,
            confidence: 92,
            timestamp: Math.floor(Date.now() / 1000)
        };
        
        const proof = await prover.generateCompositeProof(modelData, signalData);
        console.log("Composite proof generated:", JSON.stringify(proof, null, 2));
        
    } else {
        console.log("Usage: node generate_proof.js [model|signal|composite]");
    }
}
