// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ZKSignalVerifier
 * @dev Verifies zero-knowledge proofs for ML model attestations and trading signals
 * Enables verifiable AI without revealing model parameters or signal details
 */

interface IVerifier {
    function verifyProof(
        uint[2] memory _pA,
        uint[2][2] memory _pB,
        uint[2] memory _pC,
        uint[] memory _pubSignals
    ) external view returns (bool);
}

contract ZKSignalVerifier {
    // Verifier contract addresses (deployed separately)
    IVerifier public immutable modelVerifier;
    IVerifier public immutable signalVerifier;
    
    // Signal attestation registry
    struct SignalAttestation {
        bytes32 signalHash;
        bytes32 modelHash;
        uint256 timestamp;
        uint8 signalType;
        bool verified;
    }
    
    struct ModelAttestation {
        bytes32 modelHash;
        uint256 version;
        uint256 timestamp;
        address attester;
        bool verified;
    }
    
    // Storage
    mapping(bytes32 => SignalAttestation) public signals;
    mapping(bytes32 => ModelAttestation) public models;
    mapping(address => bool) public authorizedAttesters;
    
    // Events
    event ModelAttested(
        bytes32 indexed modelHash,
        uint256 version,
        uint256 timestamp,
        address indexed attester
    );
    
    event SignalAttested(
        bytes32 indexed signalHash,
        bytes32 indexed modelHash,
        uint8 signalType,
        uint256 timestamp,
        address indexed attester
    );
    
    event AttesterAuthorized(address indexed attester, bool authorized);
    
    // Errors
    error UnauthorizedAttester();
    error InvalidProof();
    error ModelNotFound();
    error SignalAlreadyAttested();
    error InvalidSignalType();
    error InvalidTimestamp();
    
    // Modifiers
    modifier onlyAuthorized() {
        if (!authorizedAttesters[msg.sender]) revert UnauthorizedAttester();
        _;
    }
    
    constructor(address _modelVerifier, address _signalVerifier) {
        modelVerifier = IVerifier(_modelVerifier);
        signalVerifier = IVerifier(_signalVerifier);
        authorizedAttesters[msg.sender] = true;
    }
    
    /**
     * @dev Attest to an ML model using zero-knowledge proof
     * @param proof Groth16 proof components [a, b, c]
     * @param modelHash Hash of the model (public signal)
     * @param version Model version
     * @param timestamp Attestation timestamp
     */
    function attestModel(
        uint[2] memory _pA,
        uint[2][2] memory _pB,
        uint[2] memory _pC,
        bytes32 modelHash,
        uint256 version,
        uint256 timestamp
    ) external onlyAuthorized {
        // Prepare public signals for verification
        uint[] memory pubSignals = new uint[](3);
        pubSignals[0] = uint256(modelHash);
        pubSignals[1] = version;
        pubSignals[2] = timestamp;
        
        // Verify the zero-knowledge proof
        bool proofValid = modelVerifier.verifyProof(_pA, _pB, _pC, pubSignals);
        if (!proofValid) revert InvalidProof();
        
        // Validate timestamp (must be recent)
        if (timestamp > block.timestamp || timestamp < block.timestamp - 1 hours) {
            revert InvalidTimestamp();
        }
        
        // Store model attestation
        models[modelHash] = ModelAttestation({
            modelHash: modelHash,
            version: version,
            timestamp: timestamp,
            attester: msg.sender,
            verified: true
        });
        
        emit ModelAttested(modelHash, version, timestamp, msg.sender);
    }
    
    /**
     * @dev Attest to a trading signal using zero-knowledge proof
     * @param proof Groth16 proof components [a, b, c]
     * @param signalHash Hash of the trading signal (public signal)
     * @param modelHash Hash of the generating model
     * @param signalType Type of signal (1-10)
     * @param timestamp Signal generation timestamp
     */
    function attestSignal(
        uint[2] memory _pA,
        uint[2][2] memory _pB,
        uint[2] memory _pC,
        bytes32 signalHash,
        bytes32 modelHash,
        uint8 signalType,
        uint256 timestamp
    ) external onlyAuthorized {
        // Validate signal type
        if (signalType < 1 || signalType > 10) revert InvalidSignalType();
        
        // Check signal not already attested
        if (signals[signalHash].verified) revert SignalAlreadyAttested();
        
        // Verify model exists and is attested
        if (!models[modelHash].verified) revert ModelNotFound();
        
        // Prepare public signals for verification
        uint[] memory pubSignals = new uint[](4);
        pubSignals[0] = uint256(signalHash);
        pubSignals[1] = 1; // isValid flag (should be 1 for valid signals)
        pubSignals[2] = uint256(modelHash);
        pubSignals[3] = timestamp;
        
        // Verify the zero-knowledge proof
        bool proofValid = signalVerifier.verifyProof(_pA, _pB, _pC, pubSignals);
        if (!proofValid) revert InvalidProof();
        
        // Validate timestamp
        if (timestamp > block.timestamp || timestamp < block.timestamp - 1 hours) {
            revert InvalidTimestamp();
        }
        
        // Store signal attestation
        signals[signalHash] = SignalAttestation({
            signalHash: signalHash,
            modelHash: modelHash,
            timestamp: timestamp,
            signalType: signalType,
            verified: true
        });
        
        emit SignalAttested(signalHash, modelHash, signalType, timestamp, msg.sender);
    }
    
    /**
     * @dev Verify if a signal is properly attested
     * @param signalHash Hash of the signal to verify
     * @return verified True if signal is verified
     * @return modelHash Hash of the generating model
     * @return signalType Type of the signal
     * @return timestamp When the signal was generated
     */
    function verifySignal(bytes32 signalHash) 
        external 
        view 
        returns (
            bool verified,
            bytes32 modelHash,
            uint8 signalType,
            uint256 timestamp
        ) 
    {
        SignalAttestation memory signal = signals[signalHash];
        return (
            signal.verified,
            signal.modelHash,
            signal.signalType,
            signal.timestamp
        );
    }
    
    /**
     * @dev Verify if a model is properly attested
     * @param modelHash Hash of the model to verify
     * @return verified True if model is verified
     * @return version Model version
     * @return timestamp When the model was attested
     * @return attester Address that attested the model
     */
    function verifyModel(bytes32 modelHash)
        external
        view
        returns (
            bool verified,
            uint256 version,
            uint256 timestamp,
            address attester
        )
    {
        ModelAttestation memory model = models[modelHash];
        return (
            model.verified,
            model.version,
            model.timestamp,
            model.attester
        );
    }
    
    /**
     * @dev Authorize/deauthorize an attester
     * @param attester Address to authorize or deauthorize
     * @param authorized True to authorize, false to deauthorize
     */
    function setAttesterAuthorization(address attester, bool authorized) 
        external 
        onlyAuthorized 
    {
        authorizedAttesters[attester] = authorized;
        emit AttesterAuthorized(attester, authorized);
    }
    
    /**
     * @dev Get signal attestation details
     * @param signalHash Hash of the signal
     * @return attestation Full signal attestation struct
     */
    function getSignalAttestation(bytes32 signalHash) 
        external 
        view 
        returns (SignalAttestation memory attestation) 
    {
        return signals[signalHash];
    }
    
    /**
     * @dev Get model attestation details
     * @param modelHash Hash of the model
     * @return attestation Full model attestation struct
     */
    function getModelAttestation(bytes32 modelHash) 
        external 
        view 
        returns (ModelAttestation memory attestation) 
    {
        return models[modelHash];
    }
    
    /**
     * @dev Check if signal and model are linked
     * @param signalHash Hash of the signal
     * @param modelHash Hash of the model
     * @return linked True if signal was generated by the model
     */
    function isSignalLinkedToModel(bytes32 signalHash, bytes32 modelHash) 
        external 
        view 
        returns (bool linked) 
    {
        SignalAttestation memory signal = signals[signalHash];
        return signal.verified && signal.modelHash == modelHash;
    }
}
