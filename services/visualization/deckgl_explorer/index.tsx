/**
 * Deck.GL Explorer - Force-directed network graphs for blockchain entities
 * Palantir Foundry-style graph visualization for entity relationships
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, LineLayer } from '@deck.gl/layers';
import { StaticMap } from 'react-map-gl';
import { scaleOrdinal, scaleLinear } from 'd3-scale';
import { schemeCategory10 } from 'd3-scale-chromatic';

interface Node {
  id: string;
  entity_id: string;
  entity_type: 'address' | 'contract' | 'token' | 'transaction' | 'block';
  label: string;
  risk_score?: number;
  balance?: number;
  metadata?: Record<string, any>;
}

interface Edge {
  source: string;
  target: string;
  weight: number;
  relationship_type: 'transfer' | 'approval' | 'interaction' | 'ownership';
  value?: number;
  timestamp?: string;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface DeckGLExplorerProps {
  data?: GraphData;
  onNodeClick?: (node: Node) => void;
  onEdgeClick?: (edge: Edge) => void;
  height?: number;
  width?: number;
}

const INITIAL_VIEW_STATE = {
  longitude: 0,
  latitude: 0,
  zoom: 1,
  pitch: 0,
  bearing: 0
};

export default function DeckGLExplorer({
  data,
  onNodeClick,
  onEdgeClick,
  height = 600,
  width = 800
}: DeckGLExplorerProps) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isLoading, setIsLoading] = useState(!data);

  // Color scale for different entity types
  const colorScale = useMemo(() => 
    scaleOrdinal(schemeCategory10)
      .domain(['address', 'contract', 'token', 'transaction', 'block']),
    []
  );

  // Format data for Deck.GL ForceDirectedGraph
  const graphData = useMemo(() => {
    if (!data) return null;

    return {
      nodes: data.nodes.map(node => ({
        ...node,
        color: colorScale(node.entity_type),
        size: Math.log(node.risk_score || 1) * 10 + 5,
        position: [Math.random() * 100, Math.random() * 100] // Initial random positions
      })),
      links: data.edges.map(edge => ({
        ...edge,
        color: edge.relationship_type === 'transfer' ? [255, 0, 0, 180] : [100, 100, 100, 100],
        width: Math.log(edge.weight || 1) + 1
      }))
    };
  }, [data, colorScale]);

  const layers = useMemo(() => {
    if (!graphData) return [];

    return [
      new ForceDirectedGraph({
        id: 'blockchain-graph',
        data: graphData,
        nodeSize: d => d.size,
        nodeColor: d => d.color,
        linkColor: d => d.color,
        linkWidth: d => d.width,
        onNodeClick: (info) => {
          setSelectedNode(info.object);
          onNodeClick?.(info.object);
        },
        onLinkClick: (info) => {
          onEdgeClick?.(info.object);
        },
        pickable: true,
        highlightColor: [255, 255, 0, 255],
        autoHighlight: true,
        simulation: {
          alphaDecay: 0.01,
          alphaMin: 0.01,
          velocityDecay: 0.2
        }
      })
    ];
  }, [graphData, onNodeClick, onEdgeClick]);

  // Sample data for demo purposes
  useEffect(() => {
    if (!data) {
      // Simulate loading sample data
      setTimeout(() => {
        // This would normally come from GraphQL API
        setIsLoading(false);
      }, 1000);
    }
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="relative" style={{ height, width }}>
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        controller={true}
        layers={layers}
        getTooltip={({ object }) => {
          if (!object) return null;
          
          if (object.entity_type) {
            // Node tooltip
            return {
              html: `
                <div class="p-2 bg-gray-800 text-white rounded shadow-lg">
                  <div class="font-bold">${object.label}</div>
                  <div class="text-sm">Type: ${object.entity_type}</div>
                  <div class="text-sm">Risk Score: ${object.risk_score || 'N/A'}</div>
                </div>
              `
            };
          } else {
            // Edge tooltip
            return {
              html: `
                <div class="p-2 bg-gray-800 text-white rounded shadow-lg">
                  <div class="font-bold">${object.relationship_type}</div>
                  <div class="text-sm">Weight: ${object.weight}</div>
                  <div class="text-sm">Value: ${object.value || 'N/A'}</div>
                </div>
              `
            };
          }
        }}
      >
        <StaticMap
          mapStyle="mapbox://styles/mapbox/dark-v10"
          mapboxApiAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
        />
      </DeckGL>

      {/* Control Panel */}
      <div className="absolute top-4 right-4 bg-white p-4 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-2">Graph Controls</h3>
        <div className="space-y-2">
          <button
            className="w-full px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={() => setViewState(INITIAL_VIEW_STATE)}
          >
            Reset View
          </button>
          <div className="text-sm">
            <div>Nodes: {graphData?.nodes.length || 0}</div>
            <div>Edges: {graphData?.links.length || 0}</div>
          </div>
        </div>
      </div>

      {/* Selected Node Panel */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg max-w-sm">
          <h3 className="text-lg font-bold mb-2">Selected Entity</h3>
          <div className="space-y-1 text-sm">
            <div><strong>ID:</strong> {selectedNode.entity_id}</div>
            <div><strong>Type:</strong> {selectedNode.entity_type}</div>
            <div><strong>Label:</strong> {selectedNode.label}</div>
            <div><strong>Risk Score:</strong> {selectedNode.risk_score || 'N/A'}</div>
            {selectedNode.balance && (
              <div><strong>Balance:</strong> {selectedNode.balance} ETH</div>
            )}
          </div>
          <button
            className="mt-2 px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
            onClick={() => setSelectedNode(null)}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
