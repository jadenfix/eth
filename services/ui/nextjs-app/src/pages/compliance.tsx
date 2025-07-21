import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import ComplianceMap from '../../../services/visualization/compliance_map/map';

interface ComplianceData {
  transactions: Array<{
    source: string;
    target: string;
    value: number;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    jurisdiction_source?: string;
    jurisdiction_target?: string;
    sanctions_hit?: boolean;
    timestamp: string;
  }>;
  jurisdictions: Array<{
    jurisdiction: string;
    country_code: string;
    risk_score: number;
    total_volume: number;
    sanctions_list: boolean;
    regulatory_score: number;
  }>;
  entities: Array<{
    entity_id: string;
    name: string;
    entity_type: 'individual' | 'organization' | 'exchange' | 'service';
    jurisdiction: string;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    sanctions_hit: boolean;
    kyc_status: 'verified' | 'pending' | 'failed' | 'none';
  }>;
}

const CompliancePage: NextPage = () => {
  const [complianceData, setComplianceData] = useState<ComplianceData | null>(null);
  const [mapType, setMapType] = useState<'choropleth' | 'sankey'>('choropleth');
  const [selectedRiskLevel, setSelectedRiskLevel] = useState('all');
  const [showSanctions, setShowSanctions] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchComplianceData = async () => {
      try {
        const response = await fetch('/api/compliance/analysis', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            risk_threshold: selectedRiskLevel === 'all' ? 0 : getRiskThreshold(selectedRiskLevel),
            include_sanctions: showSanctions,
            timeRange: '24h'
          })
        });

        if (response.ok) {
          const data = await response.json();
          setComplianceData(data);
        } else {
          console.error('Failed to fetch compliance data');
          // Load sample data for demo
          loadSampleComplianceData();
        }
      } catch (error) {
        console.error('Error fetching compliance data:', error);
        loadSampleComplianceData();
      } finally {
        setIsLoading(false);
      }
    };

    fetchComplianceData();
  }, [selectedRiskLevel, showSanctions]);

  const getRiskThreshold = (level: string): number => {
    switch (level) {
      case 'low': return 0.3;
      case 'medium': return 0.6;
      case 'high': return 0.8;
      default: return 0;
    }
  };

  const loadSampleComplianceData = () => {
    // Sample data for demo purposes
    const sampleData: ComplianceData = {
      jurisdictions: [
        {
          jurisdiction: 'United States',
          country_code: 'US',
          risk_score: 25,
          total_volume: 1000000000,
          sanctions_list: false,
          regulatory_score: 85
        },
        {
          jurisdiction: 'North Korea',
          country_code: 'KP',
          risk_score: 95,
          total_volume: 5000000,
          sanctions_list: true,
          regulatory_score: 10
        },
        {
          jurisdiction: 'Switzerland',
          country_code: 'CH',
          risk_score: 15,
          total_volume: 500000000,
          sanctions_list: false,
          regulatory_score: 90
        },
        {
          jurisdiction: 'Russia',
          country_code: 'RU',
          risk_score: 80,
          total_volume: 100000000,
          sanctions_list: true,
          regulatory_score: 30
        }
      ],
      entities: [
        {
          entity_id: 'entity_1',
          name: 'Binance',
          entity_type: 'exchange',
          jurisdiction: 'Multiple',
          risk_level: 'medium',
          sanctions_hit: false,
          kyc_status: 'verified'
        },
        {
          entity_id: 'entity_2',
          name: 'Lazarus Group',
          entity_type: 'organization',
          jurisdiction: 'North Korea',
          risk_level: 'critical',
          sanctions_hit: true,
          kyc_status: 'none'
        },
        {
          entity_id: 'entity_3',
          name: 'Uniswap Labs',
          entity_type: 'organization',
          jurisdiction: 'United States',
          risk_level: 'low',
          sanctions_hit: false,
          kyc_status: 'verified'
        }
      ],
      transactions: [
        {
          source: 'entity_1',
          target: 'entity_3',
          value: 1000000,
          risk_level: 'low',
          jurisdiction_source: 'Multiple',
          jurisdiction_target: 'United States',
          sanctions_hit: false,
          timestamp: new Date().toISOString()
        },
        {
          source: 'entity_2',
          target: 'entity_1',
          value: 5000000,
          risk_level: 'critical',
          jurisdiction_source: 'North Korea',
          jurisdiction_target: 'Multiple',
          sanctions_hit: true,
          timestamp: new Date().toISOString()
        }
      ]
    };

    setComplianceData(sampleData);
  };

  const handleEntityClick = (entity: any) => {
    console.log('Entity clicked:', entity);
    // Could open entity details modal or sidebar
  };

  const handleFlowClick = (flow: any) => {
    console.log('Transaction flow clicked:', flow);
    // Could show transaction details
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading compliance analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Compliance Map - Onchain Command Center</title>
        <meta name="description" content="Regulatory compliance and risk analysis for blockchain transactions" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Compliance Map</h1>
                <p className="text-gray-600 mt-1">
                  Regulatory compliance and sanctions screening for blockchain transactions
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">View:</span>
                  <select
                    value={mapType}
                    onChange={(e) => setMapType(e.target.value as 'choropleth' | 'sankey')}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="choropleth">Geographic Map</option>
                    <option value="sankey">Flow Diagram</option>
                  </select>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Risk:</span>
                  <select
                    value={selectedRiskLevel}
                    onChange={(e) => setSelectedRiskLevel(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Levels</option>
                    <option value="low">Low Risk</option>
                    <option value="medium">Medium Risk</option>
                    <option value="high">High Risk</option>
                  </select>
                </div>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showSanctions}
                    onChange={(e) => setShowSanctions(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">Show Sanctions</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {complianceData ? (
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <ComplianceMap
                data={complianceData}
                mapType={mapType}
                onEntityClick={handleEntityClick}
                onFlowClick={handleFlowClick}
                width={window.innerWidth - 48}
                height={window.innerHeight - 180}
              />
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Compliance Data Available</h3>
              <p className="text-gray-600 mb-4">
                Unable to load compliance analysis data. This could be due to:
              </p>
              <ul className="text-sm text-gray-500 text-left max-w-md mx-auto space-y-1">
                <li>• Compliance service is not running</li>
                <li>• No transaction data has been analyzed yet</li>
                <li>• API endpoint configuration issues</li>
              </ul>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          )}
        </div>

        {/* Statistics Bar */}
        <div className="bg-white border-t px-6 py-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">
                {complianceData?.entities.filter(e => e.risk_level === 'low').length || '--'}
              </div>
              <div className="text-xs text-gray-600">Low Risk Entities</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">
                {complianceData?.entities.filter(e => e.risk_level === 'medium').length || '--'}
              </div>
              <div className="text-xs text-gray-600">Medium Risk</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {complianceData?.entities.filter(e => e.risk_level === 'high' || e.risk_level === 'critical').length || '--'}
              </div>
              <div className="text-xs text-gray-600">High Risk</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-800">
                {complianceData?.entities.filter(e => e.sanctions_hit).length || '--'}
              </div>
              <div className="text-xs text-gray-600">Sanctions Hits</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {complianceData?.jurisdictions.length || '--'}
              </div>
              <div className="text-xs text-gray-600">Jurisdictions</div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CompliancePage;
