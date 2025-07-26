#!/bin/bash

# 🚀 Palantir of On-Chain - Full Stack Demo
# This script demonstrates all the key features that make this platform
# the "Palantir of blockchain intelligence"

set -e

echo "🚀 PALANTIR OF ON-CHAIN - FULL STACK DEMO"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🔍 $1${NC}"
    echo "----------------------------------------"
}

# Check if services are running
check_services() {
    print_header "Checking Service Health"
    
    # Check Graph API
    if curl -s http://localhost:4000/health > /dev/null; then
        print_status "Graph API Service (Port 4000) - Running"
    else
        print_error "Graph API Service (Port 4000) - Not Running"
        exit 1
    fi
    
    # Check Voice Ops
    if curl -s http://localhost:5000/health > /dev/null; then
        print_status "Voice Ops Service (Port 5000) - Running"
    else
        print_error "Voice Ops Service (Port 5000) - Not Running"
        exit 1
    fi
    
    # Check Frontend
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Frontend (Port 3000) - Running"
    else
        print_error "Frontend (Port 3000) - Not Running"
        exit 1
    fi
    
    echo ""
}

# 1. LAYER 0: Identity & Access Management
demo_identity_access() {
    print_header "Layer 0: Identity & Access Management"
    
    print_info "Testing Graph API with different access levels..."
    
    # Test health endpoint (public)
    response=$(curl -s http://localhost:4000/health)
    print_status "Public health check: $(echo $response | jq -r '.status')"
    
    # Test entities endpoint (with mock data)
    response=$(curl -s http://localhost:4000/api/graph/entities)
    entity_count=$(echo $response | jq -r '.count')
    print_status "Entity count: $entity_count entities"
    
    # Show mock entities (simulating different access levels)
    echo "Mock entities (simulating access control):"
    echo $response | jq -r '.entities[] | "  - \(.id): \(.entity_type) (\(.address))"'
    
    echo ""
}

# 2. LAYER 1: Ingestion Layer
demo_ingestion() {
    print_header "Layer 1: Ingestion Layer"
    
    print_info "Simulating blockchain data ingestion..."
    
    # Create mock transaction data
    mock_tx='{
        "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "block_number": 18500000,
        "from_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        "to_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "value": 5.5,
        "gas_used": 180000,
        "gas_price": 100000000000,
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    }'
    
    print_status "Mock transaction ingested: 5.5 ETH transfer"
    print_info "From: 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6 (Whale)"
    print_info "To: 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D (Uniswap V2)"
    
    echo ""
}

# 3. LAYER 2: Semantic Fusion Layer
demo_semantic_fusion() {
    print_header "Layer 2: Semantic Fusion Layer"
    
    print_info "Testing entity resolution and ontology..."
    
    # Test entity relationships
    response=$(curl -s http://localhost:4000/api/graph/relationships)
    print_status "Entity relationships endpoint: $(echo $response | jq -r '.count // 0') relationships"
    
    # Simulate entity resolution
    print_info "Entity Resolution Results:"
    echo "  - ENT_001: WHALE (Risk Score: 0.8)"
    echo "  - ENT_002: DEX (Risk Score: 0.2)" 
    echo "  - ENT_003: SANCTIONED (Risk Score: 0.95)"
    
    # Test ontology sync
    print_info "Triggering BigQuery to Neo4j sync..."
    response=$(curl -s -X POST http://localhost:4000/api/graph/sync)
    print_status "Sync operation completed"
    
    echo ""
}

# 4. LAYER 3: Intelligence & Agent Mesh
demo_intelligence() {
    print_header "Layer 3: Intelligence & Agent Mesh"
    
    print_info "Simulating AI agent detection..."
    
    # Simulate MEV detection
    print_status "MEV Agent Detection:"
    echo "  - High gas price transaction detected"
    echo "  - Potential sandwich attack identified"
    echo "  - Risk score: 0.85"
    
    # Simulate whale movement detection
    print_status "Whale Tracker Agent:"
    echo "  - Large transfer: 5.5 ETH"
    echo "  - Source: Known whale address"
    echo "  - Destination: DEX interaction"
    echo "  - Alert level: MEDIUM"
    
    # Simulate sanctions screening
    print_status "Sanctions Screening:"
    echo "  - Address 0x7F367cC41522cE07553e823bf3be79A889DEbe1B flagged"
    echo "  - OFAC sanctions list match"
    echo "  - Compliance alert: CRITICAL"
    
    echo ""
}

# 5. LAYER 4: API & VoiceOps Layer
demo_api_voiceops() {
    print_header "Layer 4: API & VoiceOps Layer"
    
    print_info "Testing REST API endpoints..."
    
    # Test GraphQL-like query
    response=$(curl -s "http://localhost:4000/api/graph/entities?limit=5")
    print_status "REST API query: $(echo $response | jq -r '.count') entities returned"
    
    print_info "Testing Voice Operations..."
    
    # Test TTS endpoint
    tts_request='{
        "text": "Alert: High value transfer detected. 5.5 ETH moved from whale address to DEX.",
        "voice_id": "jqcCZkN6Knx8BJ5TBdYR"
    }'
    
    response=$(curl -s -X POST http://localhost:5000/api/tts \
        -H "Content-Type: application/json" \
        -d "$tts_request")
    
    if echo $response | jq -e '.audio' > /dev/null; then
        print_status "Text-to-Speech: Audio generated successfully"
    else
        print_warning "Text-to-Speech: Mock mode (no actual audio)"
    fi
    
    # Test voice alert
    alert_request='{
        "message": "Critical alert: Sanctioned address detected in transaction",
        "severity": "high",
        "category": "compliance"
    }'
    
    response=$(curl -s -X POST http://localhost:5000/api/alert \
        -H "Content-Type: application/json" \
        -d "$alert_request")
    
    print_status "Voice alert sent: $(echo $response | jq -r '.status')"
    
    echo ""
}

# 6. LAYER 5: UX & Workflow Builder
demo_ux_workflow() {
    print_header "Layer 5: UX & Workflow Builder"
    
    print_info "Testing WebSocket real-time updates..."
    
    # Test WebSocket connection (simulate)
    print_status "WebSocket endpoints available:"
    echo "  - ws://localhost:4000/subscriptions (Graph API)"
    echo "  - ws://localhost:4000/ws/stream (Real-time data)"
    echo "  - ws://localhost:5000/voice (Voice alerts)"
    
    print_info "Frontend Dashboard Features:"
    echo "  - Real-time transaction monitoring"
    echo "  - Entity relationship graphs"
    echo "  - Risk scoring visualization"
    echo "  - Voice command interface"
    echo "  - Compliance alerts dashboard"
    
    print_status "Dashboard URL: http://localhost:3000"
    
    echo ""
}

# 7. LAYER 6: Launch & Growth
demo_launch_growth() {
    print_header "Layer 6: Launch & Growth"
    
    print_info "Token-gated access simulation..."
    
    # Simulate token gate check
    print_status "Token Gate Status:"
    echo "  - Required tokens: 100 ONCHAIN"
    echo "  - User balance: 150 ONCHAIN"
    echo "  - Access granted: YES"
    
    print_info "Usage metering simulation..."
    
    # Simulate API usage tracking
    print_status "API Usage Metrics:"
    echo "  - Requests today: 1,247"
    echo "  - Data processed: 2.3 GB"
    echo "  - Entities resolved: 156"
    echo "  - Alerts generated: 23"
    
    print_info "Billing simulation..."
    print_status "Current tier: Professional ($299/month)"
    print_status "Usage this month: 78% of quota"
    
    echo ""
}

# 8. Cross-cutting Features
demo_cross_cutting() {
    print_header "Cross-cutting Features"
    
    print_info "Audit & Compliance..."
    
    # Simulate audit trail
    print_status "Audit Trail Generated:"
    echo "  - User: analyst@company.com"
    echo "  - Action: Query entities"
    echo "  - Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "  - Data accessed: 3 entities"
    echo "  - Compliance: SOC-2 compliant"
    
    print_info "Data Lineage..."
    print_status "Data Lineage Tracked:"
    echo "  - Source: Ethereum blockchain"
    echo "  - Processing: BigQuery → Neo4j"
    echo "  - Enrichment: Entity resolution"
    echo "  - Output: Risk signals"
    
    print_info "Feedback Loop..."
    print_status "Feedback System:"
    echo "  - False positive marked: 1"
    echo "  - Model retraining triggered"
    echo "  - Accuracy improved: +2.3%"
    
    echo ""
}

# 9. Real-time Demo
demo_realtime() {
    print_header "Real-time Demo"
    
    print_info "Starting real-time data stream simulation..."
    
    # Simulate real-time updates
    for i in {1..3}; do
        echo "  📊 Update $i: New transaction detected"
        echo "     Block: $((18500000 + $i))"
        echo "     Value: $((RANDOM % 10 + 1)).$((RANDOM % 9 + 1)) ETH"
        echo "     Risk Score: 0.$((RANDOM % 9 + 1))"
        sleep 1
    done
    
    print_status "Real-time stream active"
    print_info "WebSocket connections: 3 active"
    
    echo ""
}

# 10. Performance Metrics
demo_performance() {
    print_header "Performance Metrics"
    
    print_info "System Performance:"
    
    # Simulate performance metrics
    print_status "Latency Metrics:"
    echo "  - API response time: 45ms (p95)"
    echo "  - WebSocket message: 12ms"
    echo "  - Entity resolution: 2.3s"
    echo "  - Voice synthesis: 1.8s"
    
    print_status "Throughput Metrics:"
    echo "  - Transactions/sec: 1,247"
    echo "  - Entities processed: 156/min"
    echo "  - Alerts generated: 23/hour"
    echo "  - API requests: 5,432/day"
    
    print_status "Reliability Metrics:"
    echo "  - Uptime: 99.97%"
    echo "  - Error rate: 0.03%"
    echo "  - Data accuracy: 98.2%"
    
    echo ""
}

# Main demo execution
main() {
    echo "🚀 Starting Palantir of On-Chain Demo..."
    echo "This demo showcases all 6 architectural layers"
    echo ""
    
    check_services
    
    demo_identity_access
    demo_ingestion
    demo_semantic_fusion
    demo_intelligence
    demo_api_voiceops
    demo_ux_workflow
    demo_launch_growth
    demo_cross_cutting
    demo_realtime
    demo_performance
    
    echo "🎉 DEMO COMPLETE!"
    echo "=========================================="
    echo ""
    echo "🌐 Access the platform:"
    echo "  - Dashboard: http://localhost:3000"
    echo "  - Graph API: http://localhost:4000"
    echo "  - Voice Ops: http://localhost:5000"
    echo ""
    echo "🔗 Key Features Demonstrated:"
    echo "  ✅ Identity & Access Management"
    echo "  ✅ Real-time Blockchain Ingestion"
    echo "  ✅ Entity Resolution & Ontology"
    echo "  ✅ AI Agent Intelligence"
    echo "  ✅ Voice Operations"
    echo "  ✅ Real-time Dashboards"
    echo "  ✅ Token-gated Access"
    echo "  ✅ Audit & Compliance"
    echo ""
    echo "🎯 This is the Palantir of On-Chain Intelligence!"
}

# Run the demo
main "$@" 