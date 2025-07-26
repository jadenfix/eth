# 🚨 IMMEDIATE ACTION PLAN
## Fix Current Issues & Get System Running

### **Step 1: Clean Up Port Conflicts**
```bash
# Kill all conflicting processes
pkill -f "python.*graph_api_service"
pkill -f "python.*voice_service" 
pkill -f "node.*next"
pkill -f "python.*ethereum_ingester"

# Verify ports are free
lsof -i :3000,4000,5000
```

### **Step 2: Fix Missing Frontend Pages**
The logs show missing pages: `/intelligence` and `/operations`

```bash
# Create missing pages
cd services/ui/nextjs-app/pages
```

**Create `/intelligence.tsx`:**
```tsx
import React from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import { Box, Heading, Text, useColorModeValue } from '@chakra-ui/react';
import PalantirLayout from '../src/components/layout/PalantirLayout';

const Intelligence: NextPage = () => {
  const textColor = useColorModeValue('gray.900', 'white');
  
  return (
    <PalantirLayout>
      <Head>
        <title>Intelligence - Onchain Command Center</title>
      </Head>
      <Box p={6}>
        <Heading color={textColor} mb={4}>AI Intelligence Dashboard</Heading>
        <Text color={textColor}>Advanced AI-powered blockchain intelligence and threat detection.</Text>
      </Box>
    </PalantirLayout>
  );
};

export default Intelligence;
```

**Create `/operations.tsx`:**
```tsx
import React from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import { Box, Heading, Text, useColorModeValue } from '@chakra-ui/react';
import PalantirLayout from '../src/components/layout/PalantirLayout';

const Operations: NextPage = () => {
  const textColor = useColorModeValue('gray.900', 'white');
  
  return (
    <PalantirLayout>
      <Head>
        <title>Operations - Onchain Command Center</title>
      </Head>
      <Box p={6}>
        <Heading color={textColor} mb={4}>Operations Center</Heading>
        <Text color={textColor}>Real-time operations monitoring and control center.</Text>
      </Box>
    </PalantirLayout>
  );
};

export default Operations;
```

### **Step 3: Start Services Properly**
```bash
# Start services in correct order
cd /Users/jadenfix/eth

# 1. Start Graph API (port 4000)
python services/graph_api/graph_api_service.py &

# 2. Start Voice Ops (port 5000) 
python services/voiceops/voice_service_realtime.py &

# 3. Start ETH Ingester
python services/ethereum_ingester/ethereum_ingester_realtime.py &

# 4. Start Frontend (port 3000)
cd services/ui/nextjs-app && npm run dev &
```

### **Step 4: Verify Services**
```bash
# Check all services are running
curl http://localhost:3000/health
curl http://localhost:4000/health  
curl http://localhost:5000/health

# Check frontend pages
curl http://localhost:3000/intelligence
curl http://localhost:3000/operations
```

### **Step 5: Fix BigQuery Permissions**
```bash
# Grant BigQuery permissions
gcloud projects add-iam-policy-binding ethhackathon \
    --member="serviceAccount:infra-automation@ethhackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding ethhackathon \
    --member="serviceAccount:infra-automation@ethhackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Create datasets
bq mk --project_id=ethhackathon onchain_data
bq mk --project_id=ethhackathon audit_logs
```

### **Step 6: Run Tests**
```bash
# Run comprehensive tests
python -m pytest tests/e2e/test_comprehensive.py -v --tb=short
```

### **Expected Results After These Steps:**
- ✅ All services running on correct ports
- ✅ Frontend accessible at http://localhost:3000
- ✅ All pages working (including /intelligence, /operations)
- ✅ BigQuery permissions granted
- ✅ Tests passing

### **Next Steps:**
1. Follow the comprehensive roadmap
2. Deploy missing V3 features
3. Complete infrastructure setup
4. Run full validation tests

---

**Time Estimate**: 30-60 minutes
**Success Criteria**: All services running, frontend accessible, tests passing 