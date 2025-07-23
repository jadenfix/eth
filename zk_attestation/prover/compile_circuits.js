import { execSync } from "child_process";
import fs from "fs/promises";
import path from "path";

/**
 * Circuit Compilation and Setup Script
 * Compiles Circom circuits and generates proving/verification keys
 */

const circuits = [
    "model_poseidon",
    "signal_hash"
];

const buildDir = "./build";
const circuitDir = "../circuit";

async function ensureDirectory(dir) {
    try {
        await fs.access(dir);
    } catch {
        await fs.mkdir(dir, { recursive: true });
    }
}

async function runCommand(command, description) {
    console.log(`\n${description}...`);
    console.log(`Running: ${command}`);
    
    try {
        const output = execSync(command, { 
            stdio: 'inherit',
            cwd: process.cwd()
        });
        console.log(`✅ ${description} completed`);
        return output;
    } catch (error) {
        console.error(`❌ ${description} failed:`, error.message);
        throw error;
    }
}

async function downloadPtau() {
    const ptauFile = path.join(buildDir, "powersOfTau28_hez_final_16.ptau");
    
    try {
        await fs.access(ptauFile);
        console.log("✅ Powers of Tau file already exists");
        return;
    } catch {
        console.log("📥 Downloading Powers of Tau file...");
        await runCommand(
            `curl -L -o ${ptauFile} https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_16.ptau`,
            "Download Powers of Tau ceremony file"
        );
    }
}

async function compileCircuit(circuitName) {
    console.log(`\n🔧 Compiling circuit: ${circuitName}`);
    
    const circuitFile = path.join(circuitDir, `${circuitName}.circom`);
    const wasmFile = path.join(buildDir, `${circuitName}.wasm`);
    const r1csFile = path.join(buildDir, `${circuitName}.r1cs`);
    
    // Compile circuit
    await runCommand(
        `circom ${circuitFile} --wasm --r1cs --sym -o ${buildDir}`,
        `Compile ${circuitName} circuit`
    );
    
    // Move wasm file to correct location
    const wasmDir = path.join(buildDir, `${circuitName}_js`);
    const originalWasm = path.join(wasmDir, `${circuitName}.wasm`);
    
    try {
        await fs.copyFile(originalWasm, wasmFile);
        console.log(`✅ WASM file copied to ${wasmFile}`);
    } catch (error) {
        console.log(`⚠️  Could not copy WASM file: ${error.message}`);
    }
}

async function setupCircuit(circuitName) {
    console.log(`\n🔑 Setting up proving/verification keys for: ${circuitName}`);
    
    const r1csFile = path.join(buildDir, `${circuitName}.r1cs`);
    const ptauFile = path.join(buildDir, "powersOfTau28_hez_final_16.ptau");
    const zkeyFile = path.join(buildDir, `${circuitName}_0000.zkey`);
    const finalZkeyFile = path.join(buildDir, `${circuitName}_final.zkey`);
    const vkeyFile = path.join(buildDir, `${circuitName}_verification_key.json`);
    
    // Phase 1: Setup
    await runCommand(
        `snarkjs groth16 setup ${r1csFile} ${ptauFile} ${zkeyFile}`,
        `Phase 1 setup for ${circuitName}`
    );
    
    // Phase 2: Contribute (dummy contribution for development)
    await runCommand(
        `snarkjs zkey contribute ${zkeyFile} ${finalZkeyFile} --name="First contribution" -v -e="random entropy"`,
        `Phase 2 contribution for ${circuitName}`
    );
    
    // Export verification key
    await runCommand(
        `snarkjs zkey export verificationkey ${finalZkeyFile} ${vkeyFile}`,
        `Export verification key for ${circuitName}`
    );
    
    console.log(`✅ Setup complete for ${circuitName}`);
}

async function generateSolidityVerifier(circuitName) {
    console.log(`\n📄 Generating Solidity verifier for: ${circuitName}`);
    
    const finalZkeyFile = path.join(buildDir, `${circuitName}_final.zkey`);
    const solidityFile = path.join("../contracts", `${circuitName}_verifier.sol`);
    
    await ensureDirectory("../contracts");
    
    await runCommand(
        `snarkjs zkey export solidityverifier ${finalZkeyFile} ${solidityFile}`,
        `Generate Solidity verifier for ${circuitName}`
    );
}

async function main() {
    console.log("🚀 Starting ZK circuit compilation and setup...\n");
    
    // Ensure build directory exists
    await ensureDirectory(buildDir);
    
    // Download Powers of Tau if needed
    await downloadPtau();
    
    // Process each circuit
    for (const circuitName of circuits) {
        try {
            await compileCircuit(circuitName);
            await setupCircuit(circuitName);
            await generateSolidityVerifier(circuitName);
            
            console.log(`\n✅ ${circuitName} circuit fully set up and ready!\n`);
            
        } catch (error) {
            console.error(`\n❌ Failed to setup ${circuitName}:`, error.message);
            process.exit(1);
        }
    }
    
    console.log("🎉 All circuits compiled and set up successfully!");
    console.log("\nNext steps:");
    console.log("1. Run 'npm run prove model' to test model proof generation");
    console.log("2. Run 'npm run prove signal' to test signal proof generation");
    console.log("3. Deploy the Solidity verifiers to your blockchain");
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(error => {
        console.error("Setup failed:", error);
        process.exit(1);
    });
}
