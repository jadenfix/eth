import { groth16 } from "snarkjs";
import fs from "fs/promises";
import path from "path";

/**
 * Standalone proof verification script
 * Used by the Python API service to verify proofs
 */

async function verifyProof(circuitName, proofFile, signalsFile) {
    try {
        // Load verification key
        const vkeyFile = path.join("./build", `${circuitName}_verification_key.json`);
        const vKey = JSON.parse(await fs.readFile(vkeyFile, 'utf8'));
        
        // Load proof and signals
        const proof = JSON.parse(await fs.readFile(proofFile, 'utf8'));
        const publicSignals = JSON.parse(await fs.readFile(signalsFile, 'utf8'));
        
        // Verify proof
        const result = await groth16.verify(vKey, publicSignals, proof);
        
        console.log(result ? "VERIFIED" : "FAILED");
        return result;
        
    } catch (error) {
        console.error("Verification error:", error.message);
        console.log("FAILED");
        return false;
    }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
    const [,, circuitName, proofFile, signalsFile] = process.argv;
    
    if (!circuitName || !proofFile || !signalsFile) {
        console.error("Usage: node verify_proof.js <circuit_name> <proof_file> <signals_file>");
        process.exit(1);
    }
    
    await verifyProof(circuitName, proofFile, signalsFile);
}
