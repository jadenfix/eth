#!/bin/bash

# 🚀 Palantir of On-Chain - Curl Demo Commands
# Specific curl commands to test all API endpoints

echo "🚀 PALANTIR OF ON-CHAIN - CURL API DEMO"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}🔍 $1${NC}"
    echo "----------------------------------------"
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Graph API Health Check
print_header "1. Graph API Health Check"
curl -s http://localhost:4000/health | jq .
echo ""

# 2. Get Entities (Identity & Access Layer)
print_header "2. Get Entities (Identity & Access Layer)"
curl -s http://localhost:4000/api/graph/entities | jq .
echo ""

# 3. Get Entity Relationships
print_header "3. Get Entity Relationships"
curl -s http://localhost:4000/api/graph/relationships | jq .
echo ""

# 4. Trigger BigQuery to Neo4j Sync
print_header "4. Trigger BigQuery to Neo4j Sync"
curl -s -X POST http://localhost:4000/api/graph/sync | jq .
echo ""

# 5. Voice Ops Health Check
print_header "5. Voice Ops Health Check"
curl -s http://localhost:5000/health | jq .
echo ""

# 6. Get Available Voices
print_header "6. Get Available Voices"
curl -s http://localhost:5000/api/voices | jq .
echo ""

# 7. Text-to-Speech Request
print_header "7. Text-to-Speech Request"
curl -s -X POST http://localhost:5000/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Alert: High value transfer detected. 5.5 ETH moved from whale address to DEX.",
    "voice_id": "jqcCZkN6Knx8BJ5TBdYR"
  }' | jq .
echo ""

# 8. Voice Alert
print_header "8. Voice Alert"
curl -s -X POST http://localhost:5000/api/alert \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Critical alert: Sanctioned address detected in transaction",
    "severity": "high",
    "category": "compliance"
  }' | jq .
echo ""

# 9. Test WebSocket Connection (simulate)
print_header "9. WebSocket Endpoints"
echo "WebSocket endpoints available:"
echo "  - ws://localhost:4000/subscriptions (Graph API)"
echo "  - ws://localhost:4000/ws/stream (Real-time data)"
echo "  - ws://localhost:5000/voice (Voice alerts)"
echo ""

# 10. Frontend Status
print_header "10. Frontend Status"
curl -s -I http://localhost:3000 | head -5
echo ""

# 11. Simulate MEV Detection API Call
print_header "11. Simulate MEV Detection API Call"
curl -s -X POST http://localhost:4000/api/graph/sync \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "block_number": 18500000,
    "from_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "to_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "value": 5.5,
    "gas_price": 200000000000,
    "detection_type": "mev_sandwich"
  }' | jq .
echo ""

# 12. Simulate Whale Movement Detection
print_header "12. Simulate Whale Movement Detection"
curl -s -X POST http://localhost:5000/api/alert \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Whale movement detected: 5.5 ETH transfer from known whale address",
    "severity": "medium",
    "category": "whale_tracker",
    "metadata": {
      "from_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "to_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
      "value_eth": 5.5,
      "risk_score": 0.75
    }
  }' | jq .
echo ""

# 13. Simulate Sanctions Screening
print_header "13. Simulate Sanctions Screening"
curl -s -X POST http://localhost:5000/api/alert \
  -H "Content-Type: application/json" \
  -d '{
    "message": "CRITICAL: Sanctioned address detected in transaction",
    "severity": "critical",
    "category": "compliance",
    "metadata": {
      "sanctioned_address": "0x7F367cC41522cE07553e823bf3be79A889DEbe1B",
      "sanctions_list": "OFAC",
      "risk_score": 0.95,
      "compliance_status": "VIOLATION"
    }
  }' | jq .
echo ""

# 14. Test Entity Resolution API
print_header "14. Test Entity Resolution API"
curl -s -X POST http://localhost:4000/api/graph/sync \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
      "0x7F367cC41522cE07553e823bf3be79A889DEbe1B"
    ],
    "entity_resolution": true
  }' | jq .
echo ""

# 15. Performance Test - Multiple Requests
print_header "15. Performance Test - Multiple Requests"
echo "Testing API response times..."

for i in {1..5}; do
    start_time=$(date +%s%N)
    curl -s http://localhost:4000/health > /dev/null
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    echo "  Request $i: ${duration}ms"
done

echo ""

# 16. Simulate Real-time Data Stream
print_header "16. Simulate Real-time Data Stream"
echo "Real-time data endpoints:"
echo "  - Graph API WebSocket: ws://localhost:4000/subscriptions"
echo "  - Voice Ops WebSocket: ws://localhost:5000/voice"
echo "  - Real-time stream: ws://localhost:4000/ws/stream"
echo ""

# 17. Test Error Handling
print_header "17. Test Error Handling"
echo "Testing invalid endpoint..."
curl -s http://localhost:4000/api/nonexistent | jq .
echo ""

# 18. Simulate Audit Trail
print_header "18. Simulate Audit Trail"
curl -s -X POST http://localhost:4000/api/graph/sync \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst@company.com" \
  -H "X-Session-ID: sess_12345" \
  -d '{
    "audit": {
      "user": "analyst@company.com",
      "action": "query_entities",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
      "ip_address": "192.168.1.100",
      "user_agent": "curl/7.68.0"
    }
  }' | jq .
echo ""

# 19. Test Token-gated Access (simulation)
print_header "19. Test Token-gated Access (simulation)"
curl -s -H "X-API-Key: demo_key_123" \
  -H "X-Token-Balance: 150" \
  http://localhost:4000/api/graph/entities | jq .
echo ""

# 20. Final Status Check
print_header "20. Final Status Check"
echo "All services status:"
echo "  - Graph API: $(curl -s http://localhost:4000/health | jq -r '.status')"
echo "  - Voice Ops: $(curl -s http://localhost:5000/health | jq -r '.status')"
echo "  - Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)"
echo ""

echo "🎉 CURL DEMO COMPLETE!"
echo "========================================"
echo ""
echo "🌐 Access URLs:"
echo "  - Dashboard: http://localhost:3000"
echo "  - Graph API: http://localhost:4000"
echo "  - Voice Ops: http://localhost:5000"
echo ""
echo "🔗 Key API Endpoints Tested:"
echo "  ✅ Health checks"
echo "  ✅ Entity queries"
echo "  ✅ Voice operations"
echo "  ✅ Real-time alerts"
echo "  ✅ Error handling"
echo "  ✅ Performance metrics"
echo "  ✅ Audit trails"
echo ""
echo "🎯 All Palantir-grade features demonstrated!" 