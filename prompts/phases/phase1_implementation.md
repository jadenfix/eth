# Phase 1: Foundation & Core Infrastructure Implementation Guide


MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 

## 🎯 **PHASE 1 OVERVIEW**

**Goal:** Build the essential infrastructure and basic compliance features for the "Palantir of Compliance" system

**Duration:** 2 Weeks (Week 1: Authentication & Security, Week 2: Data Pipeline Enhancement)

**Current Status:** ✅ Basic blockchain dashboard with live data
**Target Status:** 🔒 Enterprise-grade authentication + multi-chain data ingestion

---

## 📋 **WEEK 1: AUTHENTICATION & SECURITY**

### **Day 1-2: NextAuth.js Implementation**

#### **Step 1: Install Dependencies**
```bash
cd /Users/jadenfix/eth/services/ui/nextjs-app
npm install next-auth @next-auth/prisma-adapter prisma @prisma/client
npm install bcryptjs jsonwebtoken
```

#### **Step 2: Create Authentication Configuration**
**File:** `services/ui/nextjs-app/pages/api/auth/[...nextauth].ts`

```typescript
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

export default NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email }
        })

        if (user && await bcrypt.compare(credentials.password, user.password)) {
          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role
          }
        }
        return null
      }
    })
  ],
  session: {
    strategy: 'jwt'
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      session.user.role = token.role
      return session
    }
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error'
  }
})
```

#### **Step 3: Create Database Schema**
**File:** `services/ui/nextjs-app/prisma/schema.prisma`

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  password  String
  name      String?
  role      Role     @default(VIEWER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  sessions  Session[]
  auditLogs AuditLog[]
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model AuditLog {
  id        String   @id @default(cuid())
  userId    String
  action    String
  resource  String
  details   Json?
  ipAddress String?
  userAgent String?
  timestamp DateTime @default(now())
  user      User     @relation(fields: [userId], references: [id])
}

enum Role {
  ADMIN
  ANALYST
  VIEWER
}
```

#### **Step 4: Create Authentication Pages**
**File:** `services/ui/nextjs-app/pages/auth/signin.tsx`

```typescript
import { useState } from 'react'
import { signIn, getSession } from 'next-auth/react'
import { useRouter } from 'next/router'
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  useToast,
  Card,
  CardBody
} from '@chakra-ui/react'

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const toast = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    const result = await signIn('credentials', {
      email,
      password,
      redirect: false
    })

    if (result?.error) {
      toast({
        title: 'Authentication failed',
        description: 'Invalid email or password',
        status: 'error',
        duration: 5000
      })
    } else {
      router.push('/')
    }
    setLoading(false)
  }

  return (
    <Box minH="100vh" bg="gray.50" display="flex" alignItems="center" justifyContent="center">
      <Card maxW="400px" w="full">
        <CardBody>
          <VStack spacing={6}>
            <Heading size="lg">Sign In</Heading>
            <Text color="gray.600">Access the Onchain Command Center</Text>
            
            <form onSubmit={handleSubmit} style={{ width: '100%' }}>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Email</FormLabel>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel>Password</FormLabel>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </FormControl>
                
                <Button
                  type="submit"
                  colorScheme="blue"
                  w="full"
                  isLoading={loading}
                >
                  Sign In
                </Button>
              </VStack>
            </form>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  )
}
```

### **Day 3-4: Role-Based Access Control (RBAC)**

#### **Step 1: Create RBAC Hook**
**File:** `services/ui/nextjs-app/src/hooks/useAuth.ts`

```typescript
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/router'
import { useEffect } from 'react'

export type UserRole = 'ADMIN' | 'ANALYST' | 'VIEWER'

interface UseAuthReturn {
  user: any
  role: UserRole | null
  isLoading: boolean
  isAuthenticated: boolean
  hasPermission: (permission: string) => boolean
  requireAuth: () => void
  requireRole: (role: UserRole) => void
}

const roleHierarchy = {
  ADMIN: ['admin', 'analyst', 'viewer'],
  ANALYST: ['analyst', 'viewer'],
  VIEWER: ['viewer']
}

const permissions = {
  admin: ['all'],
  analyst: ['view_data', 'create_signals', 'edit_workflows'],
  viewer: ['view_data']
}

export function useAuth(): UseAuthReturn {
  const { data: session, status } = useSession()
  const router = useRouter()

  const user = session?.user
  const role = user?.role as UserRole || null
  const isLoading = status === 'loading'
  const isAuthenticated = status === 'authenticated'

  const hasPermission = (permission: string): boolean => {
    if (!role) return false
    const userPermissions = permissions[role.toLowerCase() as keyof typeof permissions] || []
    return userPermissions.includes('all') || userPermissions.includes(permission)
  }

  const requireAuth = () => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/signin')
    }
  }

  const requireRole = (requiredRole: UserRole) => {
    requireAuth()
    if (isAuthenticated && role) {
      const userPermissions = roleHierarchy[role] || []
      const requiredPermissions = roleHierarchy[requiredRole] || []
      
      const hasAccess = requiredPermissions.some(perm => 
        userPermissions.includes(perm)
      )
      
      if (!hasAccess) {
        router.push('/unauthorized')
      }
    }
  }

  return {
    user,
    role,
    isLoading,
    isAuthenticated,
    hasPermission,
    requireAuth,
    requireRole
  }
}
```

#### **Step 2: Create Protected Route Component**
**File:** `services/ui/nextjs-app/src/components/auth/ProtectedRoute.tsx`

```typescript
import { ReactNode } from 'react'
import { useAuth, UserRole } from '../../hooks/useAuth'
import { Box, Spinner, Text, VStack } from '@chakra-ui/react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: UserRole
  fallback?: ReactNode
}

export function ProtectedRoute({ 
  children, 
  requiredRole, 
  fallback 
}: ProtectedRouteProps) {
  const { isLoading, isAuthenticated, requireAuth, requireRole } = useAuth()

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="100vh">
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading...</Text>
        </VStack>
      </Box>
    )
  }

  if (!isAuthenticated) {
    requireAuth()
    return fallback || null
  }

  if (requiredRole) {
    requireRole(requiredRole)
  }

  return <>{children}</>
}
```

#### **Step 3: Update Main Dashboard with RBAC**
**File:** `services/ui/nextjs-app/pages/index.tsx`

```typescript
// Add to existing imports
import { useAuth } from '../src/hooks/useAuth'
import { ProtectedRoute } from '../src/components/auth/ProtectedRoute'

// Wrap the MainDashboard component
export default function DashboardPage() {
  return (
    <ProtectedRoute requiredRole="VIEWER">
      <MainDashboard />
    </ProtectedRoute>
  )
}

// Update MainDashboard to use auth
const MainDashboard: React.FC = () => {
  const { user, role, hasPermission } = useAuth()
  
  // Add role-based UI rendering
  const showAdminControls = hasPermission('admin')
  const showAnalystControls = hasPermission('analyst')
  
  // ... rest of existing code
}
```

### **Day 5-7: Audit Logging & BigQuery Integration**

#### **Step 1: Create Audit Service**
**File:** `services/access_control/audit_service.py`

```python
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import bigquery
from google.cloud import logging as cloud_logging

class AuditService:
    def __init__(self):
        self.bq_client = bigquery.Client()
        self.cloud_logger = cloud_logging.Client()
        self.logger = self.cloud_logger.logger('audit-logs')
        
    def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log user action to BigQuery and Cloud Logging"""
        
        audit_entry = {
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': json.dumps(details) if details else None,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': 'production'
        }
        
        # Log to BigQuery
        table_id = f"{self.bq_client.project}.audit.user_actions"
        errors = self.bq_client.insert_rows_json(table_id, [audit_entry])
        
        if errors:
            logging.error(f"Failed to insert audit log: {errors}")
        
        # Log to Cloud Logging
        self.logger.log_struct(audit_entry, severity='INFO')
        
        return audit_entry
    
    def get_user_actions(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Query audit logs from BigQuery"""
        
        query = """
        SELECT * FROM `audit.user_actions`
        WHERE 1=1
        """
        
        if user_id:
            query += f" AND user_id = '{user_id}'"
        if action:
            query += f" AND action = '{action}'"
        if start_date:
            query += f" AND timestamp >= '{start_date}'"
        if end_date:
            query += f" AND timestamp <= '{end_date}'"
            
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        query_job = self.bq_client.query(query)
        results = query_job.result()
        
        return [dict(row) for row in results]
```

#### **Step 2: Create Audit API Endpoint**
**File:** `services/ui/nextjs-app/pages/api/audit/log.ts`

```typescript
import { NextApiRequest, NextApiResponse } from 'next'
import { getSession } from 'next-auth/react'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const session = await getSession({ req })
  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  const { action, resource, details } = req.body

  try {
    // Call audit service
    const auditResponse = await fetch('http://localhost:8000/audit/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.AUDIT_SERVICE_TOKEN}`
      },
      body: JSON.stringify({
        user_id: session.user.id,
        action,
        resource,
        details,
        ip_address: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
        user_agent: req.headers['user-agent']
      })
    })

    if (!auditResponse.ok) {
      throw new Error('Failed to log audit entry')
    }

    res.status(200).json({ success: true })
  } catch (error) {
    console.error('Audit logging error:', error)
    res.status(500).json({ error: 'Failed to log audit entry' })
  }
}
```

#### **Step 3: Create Audit Hook**
**File:** `services/ui/nextjs-app/src/hooks/useAudit.ts`

```typescript
import { useAuth } from './useAuth'

export function useAudit() {
  const { user } = useAuth()

  const logAction = async (
    action: string,
    resource: string,
    details?: any
  ) => {
    try {
      await fetch('/api/audit/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action,
          resource,
          details
        })
      })
    } catch (error) {
      console.error('Failed to log audit action:', error)
    }
  }

  return { logAction }
}
```

---

## 📋 **WEEK 2: DATA PIPELINE ENHANCEMENT**

### **Day 1-3: Multi-Chain Support**

#### **Step 1: Create Multi-Chain Configuration**
**File:** `services/ethereum_ingester/config/chains.py`

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ChainConfig:
    name: str
    chain_id: int
    rpc_url: str
    block_time: int  # seconds
    api_key: str
    enabled: bool = True

class MultiChainConfig:
    def __init__(self):
        self.chains: Dict[int, ChainConfig] = {
            1: ChainConfig(
                name="Ethereum Mainnet",
                chain_id=1,
                rpc_url="https://eth-mainnet.g.alchemy.com/v2/",
                block_time=12,
                api_key=os.getenv("ALCHEMY_ETH_API_KEY")
            ),
            137: ChainConfig(
                name="Polygon",
                chain_id=137,
                rpc_url="https://polygon-mainnet.g.alchemy.com/v2/",
                block_time=2,
                api_key=os.getenv("ALCHEMY_POLYGON_API_KEY")
            ),
            56: ChainConfig(
                name="Binance Smart Chain",
                chain_id=56,
                rpc_url="https://bsc-dataseed.binance.org/",
                block_time=3,
                api_key=""
            )
        }
    
    def get_chain(self, chain_id: int) -> ChainConfig:
        return self.chains.get(chain_id)
    
    def get_enabled_chains(self) -> Dict[int, ChainConfig]:
        return {cid: config for cid, config in self.chains.items() if config.enabled}
```

#### **Step 2: Update Ethereum Ingester for Multi-Chain**
**File:** `services/ethereum_ingester/multi_chain_ingester.py`

```python
import asyncio
from typing import Dict, List
from web3 import Web3
from .config.chains import MultiChainConfig
from .ethereum_ingester import EthereumIngester

class MultiChainIngester:
    def __init__(self):
        self.config = MultiChainConfig()
        self.ingesters: Dict[int, EthereumIngester] = {}
        self.setup_ingesters()
    
    def setup_ingesters(self):
        """Initialize ingesters for each enabled chain"""
        for chain_id, chain_config in self.config.get_enabled_chains().items():
            web3 = Web3(Web3.HTTPProvider(chain_config.rpc_url + chain_config.api_key))
            self.ingesters[chain_id] = EthereumIngester(
                web3=web3,
                chain_id=chain_id,
                chain_name=chain_config.name
            )
    
    async def start_all_ingesters(self):
        """Start ingestion for all enabled chains"""
        tasks = []
        for chain_id, ingester in self.ingesters.items():
            task = asyncio.create_task(ingester.start_ingestion())
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def get_latest_blocks(self) -> Dict[int, dict]:
        """Get latest block from all chains"""
        results = {}
        for chain_id, ingester in self.ingesters.items():
            try:
                block = await ingester.get_latest_block()
                results[chain_id] = block
            except Exception as e:
                print(f"Error getting block for chain {chain_id}: {e}")
        
        return results
```

#### **Step 3: Update API to Support Multi-Chain**
**File:** `services/ui/nextjs-app/pages/api/real-data.ts`

```typescript
import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Get data from all chains
    const multiChainResponse = await fetch('http://localhost:4000/multi-chain/latest')
    const multiChainData = await multiChainResponse.json()

    // Aggregate data from all chains
    const aggregatedData = {
      ethereum: multiChainData.chains[1] || {},
      polygon: multiChainData.chains[137] || {},
      bsc: multiChainData.chains[56] || {},
      summary: {
        totalBlocks: Object.values(multiChainData.chains).reduce((sum: number, chain: any) => 
          sum + (chain.currentBlock || 0), 0),
        totalTransactions: Object.values(multiChainData.chains).reduce((sum: number, chain: any) => 
          sum + (chain.transactionsInBlock || 0), 0),
        activeChains: Object.keys(multiChainData.chains).length
      },
      timestamp: new Date().toISOString()
    }

    res.status(200).json(aggregatedData)
  } catch (error) {
    console.error('Error fetching multi-chain data:', error)
    res.status(500).json({ error: 'Failed to fetch data' })
  }
}
```

### **Day 4-5: Transaction Normalization**

#### **Step 1: Create Transaction Normalizer**
**File:** `services/ethereum_ingester/normalizer.py`

```python
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class NormalizedTransaction:
    tx_hash: str
    chain_id: int
    block_number: int
    from_address: str
    to_address: str
    value_wei: int
    value_eth: float
    gas_price_wei: int
    gas_price_gwei: float
    gas_used: int
    gas_limit: int
    status: bool
    timestamp: datetime
    contract_address: str = None
    method_signature: str = None
    input_data: str = None
    logs: List[Dict] = None

class TransactionNormalizer:
    def __init__(self):
        self.eth_decimals = 18
        
    def normalize_transaction(
        self, 
        raw_tx: Dict[str, Any], 
        receipt: Dict[str, Any], 
        chain_id: int,
        block_timestamp: int
    ) -> NormalizedTransaction:
        """Normalize transaction data across different chains"""
        
        # Convert hex values to decimal
        value_wei = int(raw_tx.get('value', '0x0'), 16)
        gas_price_wei = int(raw_tx.get('gasPrice', '0x0'), 16)
        gas_used = int(receipt.get('gasUsed', '0x0'), 16)
        gas_limit = int(raw_tx.get('gas', '0x0'), 16)
        
        # Convert to human-readable values
        value_eth = value_wei / (10 ** self.eth_decimals)
        gas_price_gwei = gas_price_wei / (10 ** 9)
        
        # Determine if it's a contract interaction
        contract_address = None
        method_signature = None
        input_data = None
        
        if raw_tx.get('input') and raw_tx['input'] != '0x':
            contract_address = raw_tx.get('to')
            input_data = raw_tx.get('input')
            method_signature = input_data[:10] if len(input_data) >= 10 else None
        
        return NormalizedTransaction(
            tx_hash=raw_tx.get('hash'),
            chain_id=chain_id,
            block_number=int(raw_tx.get('blockNumber', '0x0'), 16),
            from_address=raw_tx.get('from'),
            to_address=raw_tx.get('to'),
            value_wei=value_wei,
            value_eth=value_eth,
            gas_price_wei=gas_price_wei,
            gas_price_gwei=gas_price_gwei,
            gas_used=gas_used,
            gas_limit=gas_limit,
            status=receipt.get('status') == 1,
            timestamp=datetime.fromtimestamp(block_timestamp),
            contract_address=contract_address,
            method_signature=method_signature,
            input_data=input_data,
            logs=receipt.get('logs', [])
        )
    
    def to_dict(self, normalized_tx: NormalizedTransaction) -> Dict[str, Any]:
        """Convert normalized transaction to dictionary"""
        return {
            'tx_hash': normalized_tx.tx_hash,
            'chain_id': normalized_tx.chain_id,
            'block_number': normalized_tx.block_number,
            'from_address': normalized_tx.from_address,
            'to_address': normalized_tx.to_address,
            'value_wei': normalized_tx.value_wei,
            'value_eth': normalized_tx.value_eth,
            'gas_price_wei': normalized_tx.gas_price_wei,
            'gas_price_gwei': normalized_tx.gas_price_gwei,
            'gas_used': normalized_tx.gas_used,
            'gas_limit': normalized_tx.gas_limit,
            'status': normalized_tx.status,
            'timestamp': normalized_tx.timestamp.isoformat(),
            'contract_address': normalized_tx.contract_address,
            'method_signature': normalized_tx.method_signature,
            'input_data': normalized_tx.input_data,
            'logs': normalized_tx.logs
        }
```

### **Day 6-7: Google Cloud Dataflow Setup**

#### **Step 1: Create Dataflow Pipeline**
**File:** `services/ethereum_ingester/dataflow_pipeline.py`

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import pubsub_v1
import json
import logging

class BlockchainDataProcessor(beam.DoFn):
    def process(self, element):
        """Process blockchain data and emit normalized events"""
        try:
            data = json.loads(element)
            
            # Process transaction data
            if data.get('type') == 'transaction':
                normalized_tx = self.normalize_transaction(data)
                yield {
                    'event_type': 'TRANSACTION_PROCESSED',
                    'data': normalized_tx,
                    'timestamp': data.get('timestamp')
                }
            
            # Process block data
            elif data.get('type') == 'block':
                normalized_block = self.normalize_block(data)
                yield {
                    'event_type': 'BLOCK_PROCESSED',
                    'data': normalized_block,
                    'timestamp': data.get('timestamp')
                }
                
        except Exception as e:
            logging.error(f"Error processing element: {e}")
    
    def normalize_transaction(self, tx_data):
        # Implementation of transaction normalization
        return tx_data
    
    def normalize_block(self, block_data):
        # Implementation of block normalization
        return block_data

def run_pipeline():
    """Run the Dataflow pipeline"""
    
    pipeline_options = PipelineOptions([
        '--project=your-gcp-project',
        '--region=us-central1',
        '--temp_location=gs://your-bucket/temp',
        '--staging_location=gs://your-bucket/staging',
        '--runner=DataflowRunner',
        '--job_name=blockchain-data-pipeline'
    ])
    
    with beam.Pipeline(options=pipeline_options) as pipeline:
        # Read from Pub/Sub
        messages = (
            pipeline 
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
                subscription='projects/your-project/subscriptions/blockchain-data'
            )
        )
        
        # Process blockchain data
        processed_data = (
            messages
            | 'Process Data' >> beam.ParDo(BlockchainDataProcessor())
        )
        
        # Write to BigQuery
        processed_data | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
            'your-project:blockchain.processed_events',
            schema='event_type:STRING,data:STRING,timestamp:TIMESTAMP',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )

if __name__ == '__main__':
    run_pipeline()
```

---

## 🚀 **IMPLEMENTATION CHECKLIST**

### **Week 1 Checklist:**
- [ ] Install NextAuth.js and dependencies
- [ ] Create authentication configuration
- [ ] Set up Prisma database schema
- [ ] Create sign-in page
- [ ] Implement RBAC hook and components
- [ ] Update dashboard with role-based access
- [ ] Create audit service
- [ ] Set up audit API endpoint
- [ ] Integrate audit logging into UI

### **Week 2 Checklist:**
- [ ] Create multi-chain configuration
- [ ] Update ingester for multi-chain support
- [ ] Modify API to return multi-chain data
- [ ] Create transaction normalizer
- [ ] Set up Google Cloud Dataflow pipeline
- [ ] Test multi-chain data ingestion
- [ ] Verify audit logging functionality

---

## 🧪 **TESTING STRATEGY**

### **Authentication Tests:**
```bash
# Test sign-in functionality
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Test protected routes
curl -H "Authorization: Bearer <token>" \
  http://localhost:3000/api/audit/log
```

### **Multi-Chain Tests:**
```bash
# Test multi-chain data endpoint
curl http://localhost:3000/api/real-data

# Test individual chain data
curl http://localhost:4000/chain/1/latest
curl http://localhost:4000/chain/137/latest
```

### **Audit Logging Tests:**
```bash
# Test audit log creation
curl -X POST http://localhost:3000/api/audit/log \
  -H "Content-Type: application/json" \
  -d '{"action":"VIEW_DASHBOARD","resource":"/","details":{"page":"main"}}'
```

---

## 📊 **SUCCESS METRICS**

### **Week 1 Success Criteria:**
- ✅ Users can sign in with email/password
- ✅ Role-based access control working
- ✅ Protected routes redirect unauthorized users
- ✅ Audit logs are created for all user actions
- ✅ Admin users can view audit logs

### **Week 2 Success Criteria:**
- ✅ Multi-chain data ingestion working
- ✅ Ethereum, Polygon, and BSC data available
- ✅ Transaction normalization working across chains
- ✅ Dataflow pipeline processing data
- ✅ Real-time data updates from all chains

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **Authentication not working:**
   - Check DATABASE_URL in environment variables
   - Verify Prisma schema is migrated
   - Check NextAuth.js configuration

2. **Multi-chain data not loading:**
   - Verify API keys for each chain
   - Check RPC endpoint availability
   - Monitor ingester logs for errors

3. **Audit logging failing:**
   - Check BigQuery permissions
   - Verify audit service is running
   - Check network connectivity

### **Debug Commands:**
```bash
# Check database connection
npx prisma db push

# Test multi-chain ingester
python -m services.ethereum_ingester.multi_chain_ingester

# Check audit logs
python -c "from services.access_control.audit_service import AuditService; AuditService().get_user_actions()"
```

---

## 📈 **NEXT STEPS**

After completing Phase 1, you'll have:
- ✅ Enterprise-grade authentication
- ✅ Role-based access control
- ✅ Comprehensive audit logging
- ✅ Multi-chain data ingestion
- ✅ Normalized transaction data

**Ready for Phase 2:** Entity Resolution & Graph Database

This foundation will enable the advanced compliance features in subsequent phases. 