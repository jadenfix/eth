import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import DeckGLExplorer from '../../../services/visualization/deckgl_explorer';

interface GraphData {
  nodes: Array<{
    id: string;
    entity_id: string;
    entity_type: 'address' | 'contract' | 'token' | 'transaction' | 'block';
    label: string;
    risk_score?: number;
    balance?: number;
    metadata?: Record<string, any>;
  }>;
  edges: Array<{
    source: string;
    target: string;
    weight: number;
    relationship_type: 'transfer' | 'approval' | 'interaction' | 'ownership';
    value?: number;
    timestamp?: string;
  }>;
}

const ExplorerPage: NextPage = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    // Fetch graph data from ontology API
    const fetchGraphData = async () => {
      try {
        const response = await fetch('/api/ontology/graph', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: `
              query GetEntityGraph($filter: EntityFilter) {
                entities(filter: $filter) {
                  id
                  entity_id
                  entity_type
                  label
                  risk_score
                  balance
                  metadata
                }
                relationships(filter: $filter) {
                  source
                  target
                  weight
                  relationship_type
                  value
                  timestamp
                }
              }
            `,
            variables: {
              filter: selectedFilter === 'all' ? {} : { entity_type: selectedFilter }
            }
          })
        });

        if (response.ok) {
          const data = await response.json();
          setGraphData({
            nodes: data.data.entities,
            edges: data.data.relationships
          });
        } else {
          console.error('Failed to fetch graph data');
        }
      } catch (error) {
        console.error('Error fetching graph data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGraphData();
  }, [selectedFilter]);

  const handleNodeClick = (node: any) => {
    console.log('Node clicked:', node);
    // Could open a detail panel or navigate to entity details
  };

  const handleEdgeClick = (edge: any) => {
    console.log('Edge clicked:', edge);
    // Could show transaction details or relationship info
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading blockchain network graph...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Network Explorer - Onchain Command Center</title>
        <meta name="description" content="Interactive blockchain entity network visualization" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Network Explorer</h1>
                <p className="text-gray-600 mt-1">
                  Visualize blockchain entities and their relationships
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <select
                  value={selectedFilter}
                  onChange={(e) => setSelectedFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Entities</option>
                  <option value="address">Addresses</option>
                  <option value="contract">Contracts</option>
                  <option value="token">Tokens</option>
                  <option value="transaction">Transactions</option>
                </select>
                
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Refresh
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {graphData ? (
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <DeckGLExplorer
                data={graphData}
                onNodeClick={handleNodeClick}
                onEdgeClick={handleEdgeClick}
                width={window.innerWidth - 48} // Account for padding
                height={window.innerHeight - 180} // Account for header and padding
              />
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Graph Data Available</h3>
              <p className="text-gray-600 mb-4">
                Unable to load blockchain network data. This could be due to:
              </p>
              <ul className="text-sm text-gray-500 text-left max-w-md mx-auto space-y-1">
                <li>• Ontology service is not running</li>
                <li>• No entities have been ingested yet</li>
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

        {/* Status Bar */}
        <div className="bg-white border-t px-6 py-2 text-sm text-gray-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span>Nodes: {graphData?.nodes.length || 0}</span>
              <span>Edges: {graphData?.edges.length || 0}</span>
              <span>Filter: {selectedFilter}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Live</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ExplorerPage;
